"""
Test Client for Istanbul Neighborhood Recommendation API
This script can be used to test the API endpoint
"""

import requests
import json

# API endpoint URL (change this to your server URL)
API_URL = "http://localhost:5000/recommend"

def test_recommendation(query: str):
    """Send a query to the API and print the results"""
    
    print("\n" + "="*70)
    print(f"📤 Sending query: {query}")
    print("="*70)
    
    try:
        # Send POST request
        response = requests.post(
            API_URL,
            json={"query": query},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            
            print("\n✅ Success!")
            print(f"\n📊 Found {data['total_matches']} matching neighborhoods\n")
            
            # Print extracted preferences
            prefs = data['extracted_preferences']
            print("🔍 Extracted Preferences:")
            print(f"  💰 Budget: ₺{prefs['monthly_budget']:,.0f}/month" if prefs['monthly_budget'] else "  💰 Budget: Not specified")
            print(f"  📏 Size: {prefs['apartment_size_sqm']} m²")
            print(f"  🎯 Preferences: {prefs['preferences'] or 'Not specified'}")
            print(f"  🏪 Amenities: {prefs['amenities'] or 'Not specified'}")
            
            # Print recommendations
            print("\n" + "="*70)
            print("🏘️ TOP RECOMMENDATIONS")
            print("="*70)
            
            for rec in data['recommendations'][:5]:  # Show top 5
                print(f"\n{rec['rank']}. {rec['neighborhood']}, {rec['district']}")
                print(f"   🎯 Match Score: {rec['match_score']:.2%}")
                
                if 'estimated_monthly_rent' in rec:
                    print(f"   💵 Est. Rent: ₺{rec['estimated_monthly_rent']:,.0f}/month")
                    if 'budget_remaining' in rec:
                        print(f"   💰 Budget Remaining: ₺{rec['budget_remaining']:,.0f}")
                
                if 'green_index' in rec:
                    print(f"   🌳 Green Index: {rec['green_index']:.2f}/1.0")
                
                if 'amenities' in rec:
                    amenities_str = ", ".join([f"{v} {k}s" for k, v in list(rec['amenities'].items())[:4]])
                    print(f"   🏪 Amenities: {amenities_str}")
            
            print("\n" + "="*70)
            
            return data
            
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection Error: Could not connect to the API server.")
        print("   Make sure the server is running on the correct URL.")
        return None
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return None


def main():
    """Test the API with example queries"""
    
    print("\n" + "="*70)
    print("🧪 API CLIENT TEST")
    print("="*70)
    
    # Test queries
    test_queries = [
        "I want a green quiet neighborhood with good schools, my budget is 30000 a month",
        "family friendly area with parks and hospitals, 100 sqm, budget 40000",
        "affordable neighborhood with cafes and restaurants, budget 25000",
        "vibrant area with nightlife, my budget is 35000 TL"
    ]
    
    print(f"\n📡 Testing API at: {API_URL}")
    
    # Test each query
    for i, query in enumerate(test_queries, 1):
        print(f"\n\n{'='*70}")
        print(f"TEST #{i}/{len(test_queries)}")
        print(f"{'='*70}")
        
        test_recommendation(query)
        
        if i < len(test_queries):
            input("\nPress Enter to continue to next test...")
    
    print("\n\n✅ All tests completed!")


if __name__ == "__main__":
    # Interactive mode
    print("\n" + "="*70)
    print("🤖 NEIGHBORHOOD RECOMMENDATION API CLIENT")
    print("="*70)
    print(f"\n📡 API URL: {API_URL}")
    print("\n💡 Options:")
    print("  1. Run automated tests")
    print("  2. Enter custom query")
    print("  3. Exit")
    
    choice = input("\nChoose an option (1-3): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        print("\n" + "="*70)
        print("💬 CUSTOM QUERY MODE")
        print("="*70)
        print("\n💡 Example queries:")
        print("  • 'my budget is 20000 a month'")
        print("  • 'I want a green area with cafes, budget 35000 TL'")
        print("  • 'family friendly place with schools, 100 sqm, 40000 monthly'")
        print("\nType 'quit' to exit.\n")
        
        while True:
            query = input("\n🗣️ Your query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not query:
                continue
            
            test_recommendation(query)
    else:
        print("\n👋 Goodbye!")