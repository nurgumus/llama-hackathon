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
        
        prompt = """You are an expert real estate agent with deep knowledge of Istanbul neighborhoods. Your task is to analyze client queries and extract their housing preferences with intelligent reasoning.

====================
AVAILABLE DATA FIELDS
====================

LOCATION & BASIC INFO:
- Mahalle (Neighborhood), İlçe (District)
- Nüfus (Population)

AMENITIES & SERVICES:
- restaurant, cafe, library, school, park
- atm, pharmacy, hospital, mosque
- bus_station, train_station, transit_station

QUALITY INDICES (0-1 scale):
- INDEX_YASAM_KALITESI (Quality of Life Index)
- INDEX_YURUNEBILIRLIK (Walkability Index)
- KULTUREL_AKTIVITE_INDEX (Cultural Activity Index)
- Green_Index (Green Space Index)
- Society_Welfare_Index (Social Welfare Index)

BUILDING CHARACTERISTICS:
- 1980_oncesi (Pre-1980 buildings)
- 1980-2000_arasi (1980-2000 buildings)
- 2000_sonrasi (Post-2000 buildings)
- 1-4 kat_arasi (1-4 floor buildings)
- 5-9 kat_arasi (5-9 floor buildings)
- 9-19 kat_arasi (9-19 floor buildings)

EARTHQUAKE SAFETY SIMULATION:
- cok_agir_hasarli_bina_sayisi (Severely damaged buildings)
- agir_hasarli_bina_sayisi (Heavily damaged buildings)
- orta_hasarli_bina_sayisi (Moderately damaged buildings)
- hafif_hasarli_bina_sayisi (Lightly damaged buildings)
- can_kaybi_sayisi (Expected casualties)
- agir_yarali_sayisi (Serious injuries)
- hastanede_tedavi_sayisi (Hospitalizations)
- hafif_yarali_sayisi (Minor injuries)
- gecici_barinma (People needing temporary shelter)

ECONOMIC DATA:
- Avg_Rent_Per_SqM (Average rent per square meter in TRY)

POLITICAL DATA:
- CHP, AK PARTİ, SAADET, VATAN PARTİSİ (vote percentages)

====================
EXTRACTION TASK
====================

User Query: "USER_QUERY_HERE"

STEP 1 - REASONING:
Provide a thoughtful analysis (3-5 sentences) covering:
- What lifestyle/persona this user represents
- Which explicit preferences they stated
- Which implicit needs you're inferring and WHY
- What trade-offs or priorities you're setting
- Any assumptions you're making about thresholds

STEP 2 - EXTRACT PREFERENCES:

BUDGET & SIZE:
1. monthly_budget (number in TRY, or null)
2. apartment_size_sqm (number, or null)
3. max_rent_per_sqm (number in TRY, or null)

AMENITIES (minimum counts):
4. min_parks (integer, or null)
5. min_schools (integer, or null)
6. min_restaurants (integer, or null)
7. min_cafes (integer, or null)
8. min_hospitals (integer, or null)
9. min_pharmacies (integer, or null)
10. min_mosques (integer, or null)
11. min_libraries (integer, or null)

QUALITY INDICES (0-1 scale):
12. min_green_index (float 0-1, or null)
13. min_walkability_index (float 0-1, or null)
14. min_quality_of_life_index (float 0-1, or null)
15. min_cultural_activity_index (float 0-1, or null)
16. min_welfare_index (float 0-1, or null)

TRANSPORTATION:
17. min_total_stations (integer: bus+train+transit, or null)
18. min_bus_stations (integer, or null)
19. min_train_stations (integer, or null)
20. requires_metro (boolean, or null)

POPULATION & DENSITY:
21. max_population (integer, or null)
22. min_population (integer, or null)
23. prefers_low_density (boolean, or null)

EARTHQUAKE SAFETY:
24. earthquake_safe (boolean, or null)
25. max_casualties (integer, or null)
26. max_severely_damaged (integer, or null)
27. max_heavily_damaged (integer, or null)
28. max_moderately_damaged (integer, or null)
29. max_temporary_shelter_needed (integer, or null)

BUILDING PREFERENCES:
30. prefer_modern_buildings (boolean, or null) - True if post-2000 preferred
31. prefer_historic_buildings (boolean, or null) - True if pre-1980 preferred
32. prefer_low_rise (boolean, or null) - True if 1-4 floors preferred
33. avoid_high_rise (boolean, or null) - True if avoiding 9-19 floors
34. min_post_2000_buildings (integer, or null)

POLITICAL PREFERENCES:
35. prefer_progressive_areas (boolean, or null) - True if high CHP areas preferred
36. prefer_conservative_areas (boolean, or null) - True if high AK PARTİ areas preferred

LIFESTYLE FLAGS:
37. family_friendly (boolean, or null)
38. young_professional (boolean, or null)
39. retiree_friendly (boolean, or null)
40. pet_friendly (boolean, or null)
41. car_free_lifestyle (boolean, or null)
42. nightlife_seeker (boolean, or null)
43. quiet_lifestyle (boolean, or null)

FREE TEXT:
44. preferences_text (string summarizing all preferences)
45. deal_breakers (string listing must-have or must-avoid items)

====================
SMART INFERENCE RULES
====================

🏃 ACTIVE LIFESTYLE INDICATORS:
"walk dog" / "jogging" / "exercise" / "running" / "outdoor activities"
→ min_parks: 3, min_green_index: 0.75, min_walkability_index: 0.7, pet_friendly: true

🌳 NATURE/GREEN PREFERENCES:
"green" / "nature" / "trees" / "garden" / "park" / "greenery"
→ min_parks: 2, min_green_index: 0.8

👨‍👩‍👧‍👦 FAMILY INDICATORS:
"family" / "children" / "kids" / "schools" / "playground"
→ min_schools: 3, min_parks: 2, family_friendly: true, min_welfare_index: 0.8

🤫 QUIET/PEACEFUL INDICATORS:
"quiet" / "peaceful" / "calm" / "serene" / "tranquil" / "away from noise"
→ max_population: 15000, min_green_index: 0.65, quiet_lifestyle: true, prefers_low_density: true

🎉 VIBRANT/SOCIAL INDICATORS:
"vibrant" / "lively" / "social" / "bustling" / "nightlife" / "entertainment"
→ min_restaurants: 8, min_cafes: 8, nightlife_seeker: true, min_cultural_activity_index: 0.7

🚇 TRANSPORTATION INDICATORS:
"metro" / "subway" / "public transport" / "transit" / "train"
→ requires_metro: true, min_train_stations: 1, min_total_stations: 5

"commute" / "accessible" / "well-connected" / "easy access"
→ min_total_stations: 8, min_walkability_index: 0.6

"car-free" / "no car" / "without car" / "walkable city"
→ car_free_lifestyle: true, min_total_stations: 10, min_walkability_index: 0.8, min_restaurants: 5

🏥 HEALTH/MEDICAL INDICATORS:
"elderly" / "health issues" / "medical" / "chronic illness" / "healthcare"
→ min_hospitals: 5, min_pharmacies: 5, prefer_low_rise: true

💼 YOUNG PROFESSIONAL INDICATORS:
"young professional" / "career" / "workspace" / "coworking" / "startup"
→ young_professional: true, min_cafes: 8, min_restaurants: 5, min_total_stations: 8

👴 RETIREE INDICATORS:
"retired" / "elderly" / "senior" / "pension" / "quiet life"
→ retiree_friendly: true, min_hospitals: 3, min_pharmacies: 3, quiet_lifestyle: true, prefer_low_rise: true

🏚️ EARTHQUAKE SAFETY INDICATORS:
"earthquake safe" / "seismic" / "disaster resistant" / "structurally sound"
→ earthquake_safe: true, max_casualties: 5, max_severely_damaged: 30, max_heavily_damaged: 80, prefer_modern_buildings: true

"earthquake proof" / "very safe" / "maximum safety"
→ earthquake_safe: true, max_casualties: 2, max_severely_damaged: 15, max_heavily_damaged: 40, min_post_2000_buildings: 200

"PTSD" / "trauma" / "fear earthquakes" / "anxious about earthquakes"
→ earthquake_safe: true, max_casualties: 0, max_severely_damaged: 10, max_heavily_damaged: 20, prefer_modern_buildings: true

🏛️ CULTURAL/HERITAGE INDICATORS:
"historic" / "traditional" / "heritage" / "old Istanbul" / "authentic"
→ prefer_historic_buildings: true, min_mosques: 2, min_cultural_activity_index: 0.6

"modern" / "contemporary" / "new buildings" / "newly developed"
→ prefer_modern_buildings: true, min_post_2000_buildings: 150

🗳️ POLITICAL INDICATORS:
"progressive" / "liberal" / "secular" / "modern values"
→ prefer_progressive_areas: true

"conservative" / "traditional values" / "religious community"
→ prefer_conservative_areas: true, min_mosques: 3

💰 BUDGET INDICATORS:
"affordable" / "budget-friendly" / "cheap" / "economical"
→ max_rent_per_sqm: 500

"luxury" / "upscale" / "premium" / "high-end"
→ min_quality_of_life_index: 0.9, min_welfare_index: 0.9

"mid-range" / "moderate" / "average price"
→ max_rent_per_sqm: 600

====================
THRESHOLD GUIDELINES
====================

GREEN INDEX:
- 0.9+: Exceptionally green (forest-like)
- 0.8-0.9: Very green (abundant parks)
- 0.7-0.8: Green (good park access)
- 0.6-0.7: Moderate green (some parks)
- <0.6: Limited green space

POPULATION:
- <10,000: Very quiet
- 10,000-15,000: Quiet
- 15,000-20,000: Moderate
- 20,000+: Busy

STATIONS:
- 15+: Excellent connectivity
- 10-14: Very good connectivity
- 5-9: Good connectivity
- 3-4: Moderate connectivity
- 1-2: Limited connectivity

AMENITY COUNTS:
- Restaurants: 3 (basic), 8 (good variety), 15+ (dining hub)
- Cafes: 3 (basic), 8 (social), 15+ (café culture)
- Schools: 2 (basic), 5 (good choice), 10+ (education hub)
- Parks: 1 (minimal), 3 (good), 5+ (very green)
- Hospitals: 2 (basic), 5 (good), 10+ (medical hub)

EARTHQUAKE SAFETY (Conservative thresholds):
- Maximum casualties: 5 (safe), 10 (moderate), 20+ (risky)
- Severely damaged: 30 (safe), 50 (moderate), 100+ (risky)
- Heavily damaged: 80 (safe), 150 (moderate), 300+ (risky)

====================
OUTPUT FORMAT
====================

REASONING:
[Provide 3-5 sentences explaining:
1. What type of person/lifestyle this represents
2. Key explicit preferences they mentioned
3. Important implicit needs you're inferring
4. Threshold decisions and trade-offs you're making
5. Any assumptions or context from the query]

PREFERENCES:
{
    "monthly_budget": null,
    "apartment_size_sqm": null,
    "max_rent_per_sqm": 550,
    "min_parks": 3,
    "min_schools": null,
    "min_restaurants": 5,
    "min_cafes": 8,
    "min_hospitals": null,
    "min_pharmacies": null,
    "min_mosques": null,
    "min_libraries": null,
    "min_green_index": 0.75,
    "min_walkability_index": 0.7,
    "min_quality_of_life_index": null,
    "min_cultural_activity_index": null,
    "min_welfare_index": 0.8,
    "min_total_stations": 8,
    "min_bus_stations": null,
    "min_train_stations": null,
    "requires_metro": true,
    "max_population": null,
    "min_population": null,
    "prefers_low_density": false,
    "earthquake_safe": null,
    "max_casualties": null,
    "max_severely_damaged": null,
    "max_heavily_damaged": null,
    "max_moderately_damaged": null,
    "max_temporary_shelter_needed": null,
    "prefer_modern_buildings": null,
    "prefer_historic_buildings": null,
    "prefer_low_rise": null,
    "avoid_high_rise": null,
    "min_post_2000_buildings": null,
    "prefer_progressive_areas": null,
    "prefer_conservative_areas": null,
    "family_friendly": null,
    "young_professional": true,
    "retiree_friendly": null,
    "pet_friendly": null,
    "car_free_lifestyle": true,
    "nightlife_seeker": false,
    "quiet_lifestyle": false,
    "preferences_text": "Young professional seeking walkable, well-connected area with café culture and green spaces for moderate rent",
    "deal_breakers": "Must have metro access, cannot be far from parks"
}

====================
EXAMPLE QUERIES
====================

EXAMPLE 1:
Query: "I'm a young professional who works remotely. I love café culture and need good metro access, but I also want quiet green spaces for my morning jogs. My budget is around 500-550 TL/sqm."

REASONING:
This user is a remote-working young professional balancing urban convenience with nature access. They explicitly want café culture and metro connectivity, suggesting they value social spaces and mobility despite working from home. The morning jogging mention implies they need quality parks and walkability, not just token green space. I'm setting min_cafes to 8 for genuine café culture, requires_metro to true for non-negotiable transit, min_parks to 3 for running variety, and min_green_index to 0.75 for actual greenery. The "quiet" mention suggests they want respite from work-from-home isolation but not overwhelming density, so I'm leaving population flexible but setting quiet_lifestyle to true.

PREFERENCES:
{
    "monthly_budget": null,
    "apartment_size_sqm": null,
    "max_rent_per_sqm": 550,
    "min_parks": 3,
    "min_schools": null,
    "min_restaurants": null,
    "min_cafes": 8,
    "min_hospitals": null,
    "min_pharmacies": null,
    "min_mosques": null,
    "min_libraries": null,
    "min_green_index": 0.75,
    "min_walkability_index": 0.7,
    "min_quality_of_life_index": null,
    "min_cultural_activity_index": null,
    "min_welfare_index": null,
    "min_total_stations": 5,
    "min_bus_stations": null,
    "min_train_stations": 1,
    "requires_metro": true,
    "max_population": null,
    "min_population": null,
    "prefers_low_density": false,
    "earthquake_safe": null,
    "max_casualties": null,
    "max_severely_damaged": null,
    "max_heavily_damaged": null,
    "max_moderately_damaged": null,
    "max_temporary_shelter_needed": null,
    "prefer_modern_buildings": null,
    "prefer_historic_buildings": null,
    "prefer_low_rise": null,
    "avoid_high_rise": null,
    "min_post_2000_buildings": null,
    "prefer_progressive_areas": null,
    "prefer_conservative_areas": null,
    "family_friendly": null,
    "young_professional": true,
    "retiree_friendly": null,
    "pet_friendly": null,
    "car_free_lifestyle": true,
    "nightlife_seeker": false,
    "quiet_lifestyle": true,
    "preferences_text": "Remote-working young professional seeking balance of café culture, metro access, and green spaces for jogging in quiet setting under 550 TL/sqm",
    "deal_breakers": "Must have metro station, needs genuine café culture (8+ cafés), requires quality parks for running"
}

EXAMPLE 2:
Query: "Looking for a family neighborhood with excellent schools, safe from earthquakes, plenty of parks for the kids, and my elderly parents will live with us so we need hospitals nearby. We're worried about earthquake safety after the recent news. Budget is flexible but prefer under 600 TL/sqm."

REASONING:
This is a multi-generational household with heightened earthquake anxiety, making safety the paramount concern. The "after recent news" mention suggests trauma-informed search priorities, so I'm setting very strict earthquake parameters: max_casualties at 2, max_severely_damaged at 15, and prefer_modern_buildings to true. The elderly parent factor requires substantial medical infrastructure (min_hospitals: 5) and accessibility (prefer_low_rise: true). Children need quality education (min_schools: 5 for choice) and recreation (min_parks: 3). The family_friendly flag activates, implying need for high welfare_index (0.85) and quality_of_life_index (0.8). Budget flexibility suggests prioritizing safety over cost, so max_rent_per_sqm at 600 allows quality neighborhoods.

PREFERENCES:
{
    "monthly_budget": null,
    "apartment_size_sqm": null,
    "max_rent_per_sqm": 600,
    "min_parks": 3,
    "min_schools": 5,
    "min_restaurants": null,
    "min_cafes": null,
    "min_hospitals": 5,
    "min_pharmacies": 3,
    "min_mosques": null,
    "min_libraries": null,
    "min_green_index": 0.7,
    "min_walkability_index": null,
    "min_quality_of_life_index": 0.8,
    "min_cultural_activity_index": null,
    "min_welfare_index": 0.85,
    "min_total_stations": null,
    "min_bus_stations": null,
    "min_train_stations": null,
    "requires_metro": null,
    "max_population": null,
    "min_population": null,
    "prefers_low_density": null,
    "earthquake_safe": true,
    "max_casualties": 2,
    "max_severely_damaged": 15,
    "max_heavily_damaged": 40,
    "max_moderately_damaged": 100,
    "max_temporary_shelter_needed": 300,
    "prefer_modern_buildings": true,
    "prefer_historic_buildings": null,
    "prefer_low_rise": true,
    "avoid_high_rise": null,
    "min_post_2000_buildings": 200,
    "prefer_progressive_areas": null,
    "prefer_conservative_areas": null,
    "family_friendly": true,
    "young_professional": null,
    "retiree_friendly": true,
    "pet_friendly": null,
    "car_free_lifestyle": null,
    "nightlife_seeker": null,
    "quiet_lifestyle": null,
    "preferences_text": "Multi-generational family (young children + elderly parents) prioritizing maximum earthquake safety, excellent schools, medical access, and parks, flexible budget under 600 TL/sqm",
    "deal_breakers": "MUST be earthquake safe (trauma-informed), requires abundant schools and hospitals, needs modern construction, must have parks for children"
}

Now extract preferences from the user query above."""
        
        prompt = prompt.replace("USER_QUERY_HERE", user_query)

        try:
            response = self.llm._call(prompt, max_tokens=800, temperature=0.1)
            
            if not response or len(response.strip()) == 0:
                print("Warning: Empty response from LLM")
                return self._get_empty_preferences(), "Unable to extract preferences - empty response"
            
            # Extract reasoning
            reasoning_match = re.search(r'REASONING:\s*(.+?)(?=PREFERENCES:|$)', response, re.DOTALL)
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "Understanding user preferences..."
            
            # Clean up reasoning - remove separator lines and extra formatting
            reasoning = re.sub(r'=+', '', reasoning)  # Remove === lines
            reasoning = reasoning.strip()
            
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