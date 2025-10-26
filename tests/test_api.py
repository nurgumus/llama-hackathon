"""
Simple test script for the Istanbul Neighborhood API
Tests all endpoints and displays results
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def test_health():
    """Test the health check endpoint"""
    print_section("1. Testing Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_recommend():
    """Test the recommendation endpoint"""
    print_section("2. Testing Recommendation Endpoint")
    
    test_queries = [
        "Aile için iyi okulları olan, bütçe 40000, 100 metrekare",
        "Yeşil alan, en az 2 park, bütçe 30000",
        "Canlı bir yer, çok restoran ve kafe"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test Query {i} ---")
        print(f"Query: {query}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/recommend",
                json={"query": query},
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success!")
                print(f"Reasoning: {data['reasoning'][:100]}...")
                print(f"Found {len(data['recommendations'])} recommendations")
                
                for rec in data['recommendations']:
                    print(f"\n  #{rec['rank']}. {rec['neighborhood']}, {rec['district']}")
                    print(f"     Similarity: {rec['similarity_score']}%")
                    if rec.get('financial'):
                        print(f"     Rent: {rec['financial']['monthly_rent']:,} TRY")
            else:
                print(f"❌ Error: {response.json()}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True

def test_neighborhoods():
    """Test the neighborhoods list endpoint"""
    print_section("3. Testing Neighborhoods List")
    
    try:
        response = requests.get(f"{BASE_URL}/api/neighborhoods")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"Total neighborhoods: {data['total']}")
            print("\nFirst 5 neighborhoods:")
            for n in data['neighborhoods'][:5]:
                print(f"  - {n['mahalle']}, {n['ilce']} (Green: {n['green_index']}, Rent: {n['rent_per_sqm']} TRY/sqm)")
        else:
            print(f"❌ Error: {response.json()}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return True

def test_stats():
    """Test the statistics endpoint"""
    print_section("4. Testing Statistics Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            stats = data['statistics']
            print(f"\nDatabase Statistics:")
            print(f"  Total Neighborhoods: {stats['total_neighborhoods']}")
            print(f"  Districts: {stats['districts']}")
            print(f"  Avg Green Index: {stats['avg_green_index']}")
            print(f"  Avg Welfare Index: {stats['avg_welfare_index']}")
            print(f"  Avg Rent: {stats['avg_rent_per_sqm']} TRY/sqm")
            print(f"  Rent Range: {stats['rent_range']['min']} - {stats['rent_range']['max']} TRY/sqm")
            print(f"\nTotal Amenities:")
            print(f"  Restaurants: {stats['total_restaurants']}")
            print(f"  Schools: {stats['total_schools']}")
            print(f"  Parks: {stats['total_parks']}")
            print(f"  Cafes: {stats['total_cafes']}")
        else:
            print(f"❌ Error: {response.json()}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" ISTANBUL NEIGHBORHOOD API - TEST SUITE")
    print("="*70)
    print(f"\nTesting API at: {BASE_URL}")
    print("\nMake sure the API is running:")
    print("  python api_endpoint_v2.py")
    
    input("\nPress Enter to start tests...")
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Recommendations", test_recommend),
        ("Neighborhoods List", test_neighborhoods),
        ("Statistics", test_stats)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print("\n\nTests interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print_section("TEST SUMMARY")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
