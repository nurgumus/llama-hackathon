"""
Create ChromaDB Vector Database for Istanbul Neighborhood Data
Uses sentence-transformers/all-MiniLM-L6-v2 for embeddings
"""

import os
import pandas as pd
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict
import json

class IstanbulNeighborhoodVectorDB:
    """Create and manage ChromaDB vector database for Istanbul neighborhoods"""
    
    def __init__(self, 
                 csv_path: str = 'istanbul_mahalle_complete_data_with_descriptions_with_descriptions.csv',
                 db_path: str = './chroma_db',
                 collection_name: str = 'istanbul_neighborhoods'):
        """
        Initialize the vector database creator
        
        Args:
            csv_path: Path to the CSV file with neighborhood data
            db_path: Path where ChromaDB will be stored
            collection_name: Name of the collection in ChromaDB
        """
        self.csv_path = csv_path
        self.db_path = db_path
        self.collection_name = collection_name
        
        print("="*70)
        print("🗄️ ISTANBUL NEIGHBORHOOD VECTOR DATABASE CREATOR")
        print("="*70)
        
        # Load data
        print(f"\n📥 Loading data from {csv_path}...")
        self.df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(self.df)} neighborhoods with {len(self.df.columns)} features")
        
        # Initialize ChromaDB
        print(f"\n🔧 Initializing ChromaDB at {db_path}...")
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Use sentence-transformers embedding function
        print("📦 Loading embedding model: sentence-transformers/all-MiniLM-L6-v2...")
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("✅ Embedding model loaded")
        
        # Create or get collection
        self.collection = None
    
    def create_text_for_embedding(self, row: pd.Series) -> str:
        """
        Create a rich text description for embedding from neighborhood data
        
        Args:
            row: A row from the dataframe
            
        Returns:
            Formatted text for embedding
        """
        # Start with the description if available
        text_parts = []
        
        if pd.notna(row.get('Description')):
            text_parts.append(f"Description: {row['Description']}")
        
        # Add basic info
        text_parts.append(f"Neighborhood: {row['Mahalle']} in {row['İlçe']} district")
        text_parts.append(f"Location: Latitude {row['Enlem']}, Longitude {row['Boylam']}")
        
        # Add rent and quality indices
        if pd.notna(row.get('Avg_Rent_Per_SqM')):
            text_parts.append(f"Average rent: {row['Avg_Rent_Per_SqM']} TRY per square meter")
        
        if pd.notna(row.get('Green_Index')):
            text_parts.append(f"Green space index: {row['Green_Index']}")
        
        if pd.notna(row.get('Society_Welfare_Index')):
            text_parts.append(f"Society welfare index: {row['Society_Welfare_Index']}")
        
        if pd.notna(row.get('INDEX_YASAM_KALITESI')):
            text_parts.append(f"Quality of life index: {row['INDEX_YASAM_KALITESI']}")
        
        # Add amenities (places)
        amenities = []
        place_types = ['restaurant', 'library', 'school', 'park', 'atm', 'cafe', 
                       'pharmacy', 'hospital', 'mosque', 'bus_station', 'train_station', 'transit_station']
        
        for place_type in place_types:
            if place_type in row and pd.notna(row[place_type]) and row[place_type] > 0:
                amenities.append(f"{int(row[place_type])} {place_type.replace('_', ' ')}s")
        
        if amenities:
            text_parts.append(f"Nearby amenities: {', '.join(amenities[:8])}")  # Limit to first 8
        
        # Add population if available
        if pd.notna(row.get('Nüfus')):
            text_parts.append(f"Population: {int(row['Nüfus'])} residents")
        
        # Add building info if available
        if pd.notna(row.get('1980_oncesi')):
            text_parts.append(f"Buildings: {row['1980_oncesi']} pre-1980, {row['1980-2000_arasi']} 1980-2000, {row['2000_sonrasi']} post-2000")
        
        # Add earthquake risk if available
        if pd.notna(row.get('can_kaybi_sayisi')):
            text_parts.append(f"Earthquake scenario: {row['can_kaybi_sayisi']} estimated casualties, {row['cok_agir_hasarli_bina_sayisi']} severely damaged buildings")
        
        return " | ".join(text_parts)
    
    def create_metadata(self, row: pd.Series) -> Dict:
        """
        Create metadata dictionary for each neighborhood
        
        Args:
            row: A row from the dataframe
            
        Returns:
            Dictionary of metadata
        """
        metadata = {
            'mahalle': str(row['Mahalle']),
            'ilce': str(row['İlçe']),
            'latitude': float(row['Enlem']),
            'longitude': float(row['Boylam']),
        }
        
        # Add numeric fields that are present and not null
        numeric_fields = {
            'avg_rent_per_sqm': 'Avg_Rent_Per_SqM',
            'green_index': 'Green_Index',
            'society_welfare_index': 'Society_Welfare_Index',
            'yasam_kalitesi': 'INDEX_YASAM_KALITESI',
            'yurunebilirlik': 'INDEX_YURUNEBILIRLIK',
            'kulturel_aktivite': 'KULTUREL_AKTIVITE_INDEX',
            'nufus': 'Nüfus',
            'restaurant': 'restaurant',
            'library': 'library',
            'school': 'school',
            'park': 'park',
            'cafe': 'cafe',
            'pharmacy': 'pharmacy',
            'hospital': 'hospital',
        }
        
        for meta_key, df_key in numeric_fields.items():
            if df_key in row and pd.notna(row[df_key]):
                metadata[meta_key] = float(row[df_key])
        
        return metadata
    
    def create_vector_db(self, reset: bool = True):
        """
        Create the vector database from the CSV data
        
        Args:
            reset: If True, delete existing collection and create new one
        """
        print("\n" + "="*70)
        print("🔨 CREATING VECTOR DATABASE")
        print("="*70)
        
        # Delete existing collection if reset is True
        if reset:
            try:
                self.client.delete_collection(name=self.collection_name)
                print(f"🗑️ Deleted existing collection: {self.collection_name}")
            except:
                pass
        
        # Create collection
        print(f"\n📦 Creating collection: {self.collection_name}...")
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Istanbul neighborhood data with embeddings"}
        )
        print("✅ Collection created")
        
        # Prepare data for insertion
        print("\n📝 Preparing data for embedding...")
        documents = []
        metadatas = []
        ids = []
        id_counter = {}  # Track IDs to ensure uniqueness
        
        for idx, row in self.df.iterrows():
            # Create text for embedding
            doc_text = self.create_text_for_embedding(row)
            documents.append(doc_text)
            
            # Create metadata
            metadata = self.create_metadata(row)
            metadatas.append(metadata)
            
            # Create unique ID with counter for duplicates
            base_id = f"{row['İlçe']}_{row['Mahalle']}".replace(' ', '_')
            
            # Handle duplicates by adding a counter
            if base_id in id_counter:
                id_counter[base_id] += 1
                doc_id = f"{base_id}_{id_counter[base_id]}"
            else:
                id_counter[base_id] = 0
                doc_id = base_id
            
            ids.append(doc_id)
        
        print(f"✅ Prepared {len(documents)} documents for embedding")
        
        # Add to collection (ChromaDB will automatically create embeddings)
        print("\n🔄 Adding documents to ChromaDB (this may take a moment)...")
        
        # Add in batches to avoid memory issues
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i+batch_size]
            batch_meta = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            self.collection.add(
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids
            )
            print(f"  ✓ Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1} ({len(batch_docs)} documents)")
        
        print(f"\n✅ Successfully added all {len(documents)} neighborhoods to vector database!")
        
        # Get collection info
        collection_count = self.collection.count()
        print(f"\n📊 Collection info:")
        print(f"  • Name: {self.collection_name}")
        print(f"  • Total documents: {collection_count}")
        print(f"  • Embedding model: sentence-transformers/all-MiniLM-L6-v2")
        print(f"  • Database path: {self.db_path}")
        
        return self.collection
    
    def test_query(self, query_text: str, n_results: int = 3):
        """
        Test the vector database with a sample query
        
        Args:
            query_text: Text to search for
            n_results: Number of results to return
        """
        print("\n" + "="*70)
        print("🔍 TESTING VECTOR DATABASE")
        print("="*70)
        print(f"\n📝 Query: \"{query_text}\"")
        print(f"📊 Retrieving top {n_results} results...\n")
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        for i, (doc_id, metadata, distance) in enumerate(zip(
            results['ids'][0], 
            results['metadatas'][0], 
            results['distances'][0]
        )):
            print(f"🏘️ Result {i+1} (similarity: {1-distance:.4f})")
            print(f"  • Neighborhood: {metadata['mahalle']}")
            print(f"  • District: {metadata['ilce']}")
            if 'avg_rent_per_sqm' in metadata:
                print(f"  • Avg Rent: ₺{metadata['avg_rent_per_sqm']:.0f}/m²")
            if 'green_index' in metadata:
                print(f"  • Green Index: {metadata['green_index']:.2f}")
            if 'society_welfare_index' in metadata:
                print(f"  • Welfare Index: {metadata['society_welfare_index']:.2f}")
            print()
        
        return results


def main():
    """Main function to create the vector database"""
    
    # Initialize and create the database
    creator = IstanbulNeighborhoodVectorDB(
        csv_path='neighborhoods_with_descriptions.csv',
        db_path='./chroma_db',
        collection_name='istanbul_neighborhoods'
    )
    
    # Create the vector database
    collection = creator.create_vector_db(reset=True)
    
    # Test with sample queries
    print("\n" + "="*70)
    print("🧪 RUNNING TEST QUERIES")
    print("="*70)
    
    test_queries = [
        "affordable neighborhood with good schools and parks",
        "green area with low earthquake risk",
        "expensive district with high quality of life and many cafes",
        "family-friendly area with hospitals and pharmacies nearby"
    ]
    
    for query in test_queries:
        creator.test_query(query, n_results=3)
        print("\n" + "-"*70 + "\n")
    
    print("="*70)
    print("✅ VECTOR DATABASE CREATION COMPLETE!")
    print("="*70)
    print(f"\n📁 Database saved at: ./chroma_db")
    print(f"📦 Collection name: istanbul_neighborhoods")
    print(f"🔧 Embedding model: sentence-transformers/all-MiniLM-L6-v2")
    print(f"\n💡 You can now use this vector database in your agent!")


if __name__ == "__main__":
    main()
