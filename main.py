"""
Istanbul Neighborhood Recommendation Agent - Demo Presentation
Shows clear 3-step flow: Query → Agent Reasoning → Top 3 Results
"""

import os
import re
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from utils.groq_llm_init import groq_llm
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

class NeighborhoodAgent:
    """Real estate recommendation agent with transparent reasoning"""
    
    def __init__(self, 
                 data_path='neighborhoods_with_descriptions.csv',
                 db_path='./chroma_db',
                 collection_name='istanbul_neighborhoods'):
        """Initialize the agent"""
        self.df = pd.read_csv(data_path)
        
        # Remove bad data
        initial_count = len(self.df)
        self.df = self.df[self.df['Mahalle'] != 'Unknown'].copy()
        filtered_count = initial_count - len(self.df)
        
        if filtered_count > 0:
            print(f"Cleaned {filtered_count} invalid entries from database")
        
        # Calculate total stations (bus + train + transit)
        self.df['total_stations'] = (
            self.df['bus_station'].fillna(0) + 
            self.df['train_station'].fillna(0) + 
            self.df['transit_station'].fillna(0)
        )
        
        self.llm = groq_llm
        
        # Create unique IDs
        if 'Mahalle_ID' not in self.df.columns:
            self.df['Mahalle_ID'] = self.df['İlçe'] + '_' + self.df['Mahalle']
            self.df['Mahalle_ID'] = self.df['Mahalle_ID'].str.replace(' ', '_')
        
        # Initialize vector database
        print("Connecting to vector database...")
        self.client = chromadb.PersistentClient(path=db_path)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )
        
        print(f"Agent initialized with {len(self.df)} neighborhoods\n")
    
    def extract_preferences_with_llm(self, user_query: str) -> tuple:
        """Extract structured preferences from natural language query with reasoning"""
        
        prompt = """You are a real estate agent analyzing a client's housing preferences. Extract preferences AND explain your reasoning.

User Query: "USER_QUERY_HERE"

First, provide your reasoning about what the user needs (2-3 sentences explaining what you understood and WHY you're setting certain thresholds).

Then extract these fields:
1. monthly_budget (number in TRY, or null)
2. apartment_size_sqm (number, or null) 
3. min_parks (minimum number of parks, or null) - Set to 1+ if parks mentioned or good for walking/dogs
4. min_schools (minimum number of schools, or null) - Set to 1+ if schools/family/children mentioned
5. min_restaurants (minimum number of restaurants, or null) - Set to 3+ if dining/food/nightlife mentioned
6. min_cafes (minimum number of cafes, or null) - Set to 3+ if cafes/coffee/vibrant/social mentioned
7. min_green_index (0-1 scale, or null) - IMPORTANT: Set to 0.7+ if "green", "nature", "trees", "park", "walk dog", "outdoor" mentioned
8. max_population (maximum population, or null) - Set to 20000 if "quiet", "peaceful", "calm" mentioned
9. min_total_stations (minimum total stations: bus+train+transit, or null) - Set to 2+ if "public transport", "metro", "transit", "commute" mentioned
10. max_casualties (maximum casualties in earthquake simulation, or null) - Set to 5 if earthquake safety mentioned
11. max_severely_damaged (maximum severely damaged buildings in earthquake simulation, or null) - Set to 50 if earthquake safety mentioned
12. max_heavily_damaged (maximum heavily damaged buildings in earthquake simulation, or null) - Set to 100 if earthquake safety mentioned
13. earthquake_safe (boolean, or null) - Set to true if "earthquake safe", "seismic safety", "earthquake resistant" mentioned
14. preferences_text (free text description of preferences)

EARTHQUAKE SAFETY DATA AVAILABLE:
- can_kaybi_sayisi: Expected casualties in earthquake simulation
- cok_agir_hasarli_bina_sayisi: Number of severely damaged buildings
- agir_hasarli_bina_sayisi: Number of heavily damaged buildings
- orta_hasarli_bina_sayisi: Number of moderately damaged buildings
- hafif_hasarli_bina_sayisi: Number of lightly damaged buildings
- gecici_barinma: Number of people needing temporary shelter

PUBLIC TRANSPORTATION DATA AVAILABLE:
- bus_station: Number of bus stations
- train_station: Number of train stations
- transit_station: Number of transit stations
- Total stations = bus_station + train_station + transit_station

RULES FOR IMPLICIT EXTRACTION:
- "green area" / "nature" / "trees" / "outdoor" → min_green_index: 0.7, min_parks: 2
- "walk my dog" / "walking" / "exercise" → min_green_index: 0.7, min_parks: 2
- "quiet" / "peaceful" / "calm" → max_population: 20000, min_green_index: 0.6
- "family" / "children" / "kids" → min_schools: 2, min_parks: 2
- "vibrant" / "lively" / "social" / "nightlife" → min_restaurants: 5, min_cafes: 5
- "public transport" / "metro" / "commute" / "transit" / "subway" → min_total_stations: 8
- "easy commute" / "accessible" / "well-connected" → min_total_stations: 5
- "safe" / "secure" / "earthquake safe" / "seismic" → earthquake_safe: true, max_casualties: 5, max_severely_damaged: 50
- "earthquake resistant" / "not near fault" / "seismically safe" → earthquake_safe: true, max_casualties: 3, max_severely_damaged: 30

Format your response EXACTLY like this:

REASONING: [Your 2-3 sentence explanation here]

PREFERENCES: {"monthly_budget": 30000, "apartment_size_sqm": null, "min_parks": 2, "min_schools": null, "min_restaurants": null, "min_cafes": null, "min_green_index": 0.8, "max_population": 20000, "min_total_stations": null, "max_casualties": null, "max_severely_damaged": null, "max_heavily_damaged": null, "earthquake_safe": null, "preferences_text": "quiet green area"}

Extract from user query above:"""
        
        prompt = prompt.replace("USER_QUERY_HERE", user_query)

        try:
            response = self.llm._call(prompt, max_tokens=800, temperature=0.1)
            
            if not response or len(response.strip()) == 0:
                print("Warning: Empty response from LLM")
                return self._get_empty_preferences(), "Unable to extract preferences - empty response"
            
            # Extract reasoning
            reasoning_match = re.search(r'REASONING:\s*(.+?)(?=PREFERENCES:|$)', response, re.DOTALL)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "Understanding user preferences..."
            
            # Extract JSON - more robust pattern
            json_match = re.search(r'PREFERENCES:\s*(\{.*?\})\s*(?:\n|$)', response, re.DOTALL)
            if not json_match:
                # Try alternative pattern - look for the JSON object
                json_match = re.search(r'\{.*?"monthly_budget".*?\}', response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1) if json_match.lastindex else json_match.group(0)
                # Clean up the JSON string
                json_str = json_str.strip()
                try:
                    preferences = json.loads(json_str)
                    return preferences, reasoning
                except json.JSONDecodeError as je:
                    print(f"JSON parse error: {je}")
                    print(f"JSON string was: {json_str}")
            else:
                print(f"Could not find PREFERENCES in response.")
                print(f"Full response: {response[:500]}...")  # Print first 500 chars
            
            return self._get_empty_preferences(), reasoning
        except Exception as e:
            print(f"Error during preference extraction: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return self._get_empty_preferences(), "Unable to extract preferences"
    
    def _get_empty_preferences(self):
        """Return empty preferences dict"""
        prefs = {
            "monthly_budget": None,
            "apartment_size_sqm": None,
            "min_parks": None,
            "min_schools": None,
            "min_restaurants": None,
            "min_cafes": None,
            "min_green_index": None,
            "max_population": None,
            "min_total_stations": None,
            "max_casualties": None,
            "max_severely_damaged": None,
            "max_heavily_damaged": None,
            "earthquake_safe": None,
            "preferences_text": None
        }
        return prefs
    
    def filter_by_constraints(self, preferences: dict):
        """Apply database filters based on extracted preferences"""
        filtered_df = self.df.copy()
        filters_applied = []
        
        # Budget filter
        monthly_budget = preferences.get('monthly_budget')
        apartment_size = preferences.get('apartment_size_sqm') or 80
        
        if monthly_budget:
            filtered_df['estimated_rent'] = filtered_df['Avg_Rent_Per_SqM'] * apartment_size
            filtered_df = filtered_df[filtered_df['estimated_rent'] <= monthly_budget]
            filters_applied.append(f"Budget: ≤{monthly_budget:,} TRY/month")
        
        # Amenity filters
        if preferences.get('min_parks'):
            filtered_df = filtered_df[filtered_df['park'] >= preferences['min_parks']]
            filters_applied.append(f"Parks: ≥{preferences['min_parks']}")
        
        if preferences.get('min_schools'):
            filtered_df = filtered_df[filtered_df['school'] >= preferences['min_schools']]
            filters_applied.append(f"Schools: ≥{preferences['min_schools']}")
        
        if preferences.get('min_restaurants'):
            filtered_df = filtered_df[filtered_df['restaurant'] >= preferences['min_restaurants']]
            filters_applied.append(f"Restaurants: ≥{preferences['min_restaurants']}")
        
        if preferences.get('min_cafes'):
            filtered_df = filtered_df[filtered_df['cafe'] >= preferences['min_cafes']]
            filters_applied.append(f"Cafes: ≥{preferences['min_cafes']}")
        
        # Green index filter
        if preferences.get('min_green_index'):
            filtered_df = filtered_df[filtered_df['Green_Index'] >= preferences['min_green_index']]
            filters_applied.append(f"Green Index: ≥{preferences['min_green_index']}")
        
        # Population filter (for quiet areas)
        if preferences.get('max_population'):
            filtered_df = filtered_df[filtered_df['Nüfus'] <= preferences['max_population']]
            filters_applied.append(f"Population: ≤{preferences['max_population']:,}")
        
        # Public transportation filter
        if preferences.get('min_total_stations'):
            filtered_df = filtered_df[filtered_df['total_stations'] >= preferences['min_total_stations']]
            filters_applied.append(f"Total Stations (bus+train+transit): ≥{preferences['min_total_stations']}")
        
        # Earthquake safety filters
        if preferences.get('earthquake_safe') or preferences.get('max_casualties') is not None:
            # Filter by casualties
            if preferences.get('max_casualties') is not None:
                filtered_df = filtered_df[filtered_df['can_kaybi_sayisi'] <= preferences['max_casualties']]
                filters_applied.append(f"Max Casualties (earthquake sim): ≤{preferences['max_casualties']}")
        
        if preferences.get('max_severely_damaged') is not None:
            filtered_df = filtered_df[filtered_df['cok_agir_hasarli_bina_sayisi'] <= preferences['max_severely_damaged']]
            filters_applied.append(f"Max Severely Damaged Buildings: ≤{preferences['max_severely_damaged']}")
        
        if preferences.get('max_heavily_damaged') is not None:
            filtered_df = filtered_df[filtered_df['agir_hasarli_bina_sayisi'] <= preferences['max_heavily_damaged']]
            filters_applied.append(f"Max Heavily Damaged Buildings: ≤{preferences['max_heavily_damaged']}")
        
        return filtered_df, filters_applied
    
    def search_with_constraints(self, preferences: dict, n_results: int = 3):
        """Two-step approach: filter first, then semantic search"""
        
        print("\nSTEP 1: Creating Database Filters")
        print("-" * 70)
        
        # Pre-filter by hard constraints
        filtered_df, filters_applied = self.filter_by_constraints(preferences)
        
        if filters_applied:
            print("Filters applied:")
            for f in filters_applied:
                print(f"  • {f}")
        else:
            print("  No hard filters applied")
        
        print(f"\nResult: {len(filtered_df)} neighborhoods match criteria (from {len(self.df)} total)")
        
        if len(filtered_df) == 0:
            print("\nNo neighborhoods match your constraints.")
            return []
        
        # Get IDs of filtered neighborhoods
        filtered_mahalles = filtered_df['Mahalle'].tolist()
        filtered_ilces = filtered_df['İlçe'].tolist()
        
        # STEP 2: Semantic search within filtered results
        print("\nSTEP 2: Semantic Search")
        print("-" * 70)
        
        preferences_text = preferences.get('preferences_text') or "good neighborhood"
        print(f"Searching for: '{preferences_text}'")
        
        try:
            # Query vector database
            results = self.collection.query(
                query_texts=[preferences_text],
                n_results=min(50, len(self.df))
            )
            
            # Filter results to match our constraints
            filtered_results = {'ids': [[]], 'metadatas': [[]], 'distances': [[]]}
            
            for doc_id, metadata, distance in zip(
                results['ids'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            ):
                if metadata['mahalle'] in filtered_mahalles and metadata['ilce'] in filtered_ilces:
                    filtered_results['ids'][0].append(doc_id)
                    filtered_results['metadatas'][0].append(metadata)
                    filtered_results['distances'][0].append(distance)
                    
                    if len(filtered_results['ids'][0]) >= n_results:
                        break
            
            results = filtered_results
            
            # Parse results
            recommendations = []
            for doc_id, metadata, distance in zip(
                results['ids'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            ):
                rec = {
                    'mahalle': metadata['mahalle'],
                    'ilce': metadata['ilce'],
                    'similarity': 1 - distance,
                    'metadata': metadata
                }
                
                # Add rent calculations if budget specified
                if preferences.get('monthly_budget'):
                    apartment_size = preferences.get('apartment_size_sqm') or 80
                    rent_per_sqm = metadata.get('avg_rent_per_sqm', 0)
                    monthly_rent = rent_per_sqm * apartment_size
                    rec['monthly_rent'] = monthly_rent
                    rec['budget_remaining'] = preferences['monthly_budget'] - monthly_rent
                
                recommendations.append(rec)
            
            print(f"Found {len(recommendations)} semantic matches\n")
            return recommendations
            
        except Exception as e:
            print(f"Search error: {e}")
            print("Falling back to top-rated neighborhoods in filtered results...")
            fallback = filtered_df.nlargest(n_results, 'Society_Welfare_Index')
            return self._dataframe_to_recommendations(fallback, preferences)
    
    def _dataframe_to_recommendations(self, df: pd.DataFrame, preferences: dict):
        """Convert dataframe rows to recommendation format"""
        recommendations = []
        apartment_size = preferences.get('apartment_size_sqm') or 80
        
        for _, row in df.iterrows():
            rec = {
                'mahalle': row['Mahalle'],
                'ilce': row['İlçe'],
                'similarity': 0.5,
                'metadata': {
                    'mahalle': row['Mahalle'],
                    'ilce': row['İlçe'],
                    'green_index': row['Green_Index'],
                    'society_welfare_index': row['Society_Welfare_Index'],
                    'avg_rent_per_sqm': row['Avg_Rent_Per_SqM'],
                    'restaurant': row['restaurant'],
                    'school': row['school'],
                    'park': row['park'],
                    'cafe': row['cafe'],
                    'nufus': row['Nüfus'],
                    'bus_station': row['bus_station'],
                    'train_station': row['train_station'],
                    'transit_station': row['transit_station'],
                    'total_stations': row['total_stations']
                }
            }
            
            if preferences.get('monthly_budget'):
                monthly_rent = row['Avg_Rent_Per_SqM'] * apartment_size
                rec['monthly_rent'] = monthly_rent
                rec['budget_remaining'] = preferences['monthly_budget'] - monthly_rent
            
            recommendations.append(rec)
        
        return recommendations
    
    def explain_match(self, rec, preferences):
        """Generate explanation for why this neighborhood matched"""
        reasons = []
        meta = rec['metadata']
        
        # Budget explanation
        if rec.get('budget_remaining'):
            if rec['budget_remaining'] > 5000:
                reasons.append(f"Well under budget (saves {rec['budget_remaining']:,.0f} TRY)")
            elif rec['budget_remaining'] > 0:
                reasons.append(f"Within budget (saves {rec['budget_remaining']:,.0f} TRY)")
        
        # Green space
        if preferences.get('min_green_index') and meta.get('green_index', 0) >= preferences['min_green_index']:
            reasons.append(f"Meets green space requirement ({meta['green_index']:.2f})")
        
        # Schools
        if preferences.get('min_schools') and meta.get('school', 0) >= preferences['min_schools']:
            reasons.append(f"Has {int(meta['school'])} schools")
        
        # Parks
        if preferences.get('min_parks') and meta.get('park', 0) >= preferences['min_parks']:
            reasons.append(f"Has {int(meta['park'])} parks")
        
        # Public transportation
        if preferences.get('min_total_stations'):
            total_stations = meta.get('total_stations', 0)
            if total_stations >= preferences['min_total_stations']:
                reasons.append(f"Good public transport ({int(total_stations)} stations)")
        
        # Earthquake safety
        if preferences.get('earthquake_safe') or preferences.get('max_casualties') is not None:
            casualties = meta.get('can_kaybi_sayisi', 0)
            if casualties == 0:
                reasons.append("Excellent earthquake safety (0 expected casualties)")
            elif casualties <= 5:
                reasons.append(f"Good earthquake safety ({int(casualties)} expected casualties)")
            elif casualties <= 10:
                reasons.append(f"Moderate earthquake safety ({int(casualties)} expected casualties)")
        
        return reasons
    
    def process_query(self, user_query: str):
        """Main demo flow: Query → Reasoning → Results"""
        
        # Header
        print("\n" + "="*70)
        print("ISTANBUL NEIGHBORHOOD RECOMMENDATION DEMO")
        print("="*70)
        print(f"\nUser Query: \"{user_query}\"")
        
        # STEP 1: Agent Reasoning
        print("\n" + "="*70)
        print("AGENT REASONING: Extracting Preferences")
        print("="*70)
        
        preferences, reasoning = self.extract_preferences_with_llm(user_query)
        
        print(f"\n{reasoning}")
        
        print("\nExtracted preferences:")
        for key, value in preferences.items():
            if value is not None:
                print(f"  • {key}: {value}")
        
        # STEP 2: Database filtering and search
        print("\n" + "="*70)
        recommendations = self.search_with_constraints(preferences, n_results=3)
        
        # STEP 3: Display results
        print("="*70)
        print("TOP 3 RECOMMENDATIONS")
        print("="*70)
        
        if not recommendations:
            print("\nNo neighborhoods found matching all criteria.")
            return []
        
        for i, rec in enumerate(recommendations, 1):
            metadata = rec['metadata']
            
            print(f"\n#{i}. {rec['mahalle']}, {rec['ilce']}")
            print("-" * 70)
            
            # Why it matched
            reasons = self.explain_match(rec, preferences)
            if reasons:
                print(f"Why: {' • '.join(reasons)}")
            
            # Financial info
            if 'monthly_rent' in rec:
                print(f"Estimated Rent: {rec['monthly_rent']:,.0f} TRY/month")
                if rec['budget_remaining'] >= 0:
                    print(f"Budget Remaining: {rec['budget_remaining']:,.0f} TRY")
            
            # Quality metrics
            if 'green_index' in metadata:
                print(f"Green Index: {metadata['green_index']:.2f}/1.0")
            if 'society_welfare_index' in metadata:
                print(f"Welfare Index: {metadata['society_welfare_index']:.2f}/1.0")
            
            # Earthquake safety data (if earthquake concerns mentioned)
            if preferences.get('earthquake_safe') or preferences.get('max_casualties') is not None:
                print("\nEarthquake Safety (Simulation Results):")
                if 'can_kaybi_sayisi' in metadata:
                    print(f"  Expected Casualties: {int(metadata['can_kaybi_sayisi'])}")
                if 'cok_agir_hasarli_bina_sayisi' in metadata:
                    print(f"  Severely Damaged Buildings: {int(metadata['cok_agir_hasarli_bina_sayisi'])}")
                if 'agir_hasarli_bina_sayisi' in metadata:
                    print(f"  Heavily Damaged Buildings: {int(metadata['agir_hasarli_bina_sayisi'])}")
                if 'orta_hasarli_bina_sayisi' in metadata:
                    print(f"  Moderately Damaged Buildings: {int(metadata['orta_hasarli_bina_sayisi'])}")
                if 'gecici_barinma' in metadata:
                    print(f"  People Needing Shelter: {int(metadata['gecici_barinma'])}")
            
            # Amenities
            amenities = []
            for key in ['restaurant', 'school', 'park', 'cafe']:
                if key in metadata and metadata[key] > 0:
                    amenities.append(f"{int(metadata[key])} {key}s")
            
            if amenities:
                print(f"Amenities: {', '.join(amenities)}")
            
            # Public Transportation
            transport = []
            if 'bus_station' in metadata and metadata['bus_station'] > 0:
                transport.append(f"{int(metadata['bus_station'])} bus")
            if 'train_station' in metadata and metadata['train_station'] > 0:
                transport.append(f"{int(metadata['train_station'])} train")
            if 'transit_station' in metadata and metadata['transit_station'] > 0:
                transport.append(f"{int(metadata['transit_station'])} transit")
            
            if transport:
                total = metadata.get('total_stations', 0)
                print(f"Public Transport: {', '.join(transport)} (Total: {int(total)} stations)")
            
            # Population
            if 'nufus' in metadata and metadata['nufus'] > 0:
                print(f"Population: {int(metadata['nufus']):,}")
        
        print("\n" + "="*70 + "\n")
        return recommendations


def main():
    """Run demo"""
    print("REAL ESTATE RECOMMENDATION AGENT - DEMO")
    print("="*70)
    
    if groq_llm is None:
        print("Error: Groq LLM not initialized")
        return
    
    try:
        agent = NeighborhoodAgent()
    except Exception as e:
        print(f"Initialization failed: {e}")
        return
    
    # Demo queries
    demo_queries = [
        "family neighborhood with good schools, budget 40000 for 100 sqm",
        "green quiet area with at least 2 parks, budget 30000",
        "vibrant area with many restaurants and cafes",
        "earthquake safe neighborhood for family, budget 35000",
        "easy commute with good public transport access, budget 32000"
    ]
    
    # Run each demo query
    for query in demo_queries:
        agent.process_query(query)
        input("Press Enter to continue to next demo...\n")
    
    # Interactive mode
    print("\nINTERACTIVE MODE")
    print("Enter your query or 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("Query: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            if user_input:
                agent.process_query(user_input)
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()