"""
Flask API endpoint for Istanbul Neighborhood Recommendation System
Integrates with main_v4.py agent and serves the frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
from main_v4 import NeighborhoodAgent
from utils.groq_llm_init import groq_llm

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Initialize agent globally
print("🚀 Initializing Neighborhood Agent...")
try:
    agent = NeighborhoodAgent()
    print("✅ Agent ready to serve requests\n")
except Exception as e:
    print(f"❌ Failed to initialize agent: {e}")
    agent = None


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "agent_initialized": agent is not None,
        "llm_initialized": groq_llm is not None
    }), 200


@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Main recommendation endpoint"""
    try:
        # Check if agent is initialized
        if agent is None:
            return jsonify({
                "error": "Agent not initialized",
                "status": "error"
            }), 503
        
        # Get query from request
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                "error": "Query parameter is required",
                "status": "error"
            }), 400
        
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({
                "error": "Query cannot be empty",
                "status": "error"
            }), 400
        
        print(f"\n📝 Received query: {user_query}")
        
        # Extract preferences with reasoning
        preferences, reasoning = agent.extract_preferences_with_llm(user_query)
        
        # Get recommendations
        filtered_df, filters_applied = agent.filter_by_constraints(preferences)
        recommendations = agent.search_with_constraints(preferences, n_results=3)
        
        # Format response for frontend
        response_data = {
            "status": "success",
            "query": user_query,
            "reasoning": reasoning,
            "preferences": {k: v for k, v in preferences.items() if v is not None},
            "filters_applied": filters_applied,
            "total_neighborhoods": len(agent.df),
            "filtered_neighborhoods": len(filtered_df),
            "recommendations": []
        }
        
        # Format each recommendation
        for i, rec in enumerate(recommendations, 1):
            metadata = rec['metadata']
            
            recommendation = {
                "rank": i,
                "neighborhood": rec['mahalle'],
                "district": rec['ilce'],
                "similarity_score": round(rec.get('similarity', 0) * 100, 1),
                "match_reasons": agent.explain_match(rec, preferences),
                "details": {
                    "green_index": round(metadata.get('green_index', 0), 2),
                    "welfare_index": round(metadata.get('society_welfare_index', 0), 2),
                    "population": int(metadata.get('nufus', 0)) if metadata.get('nufus', 0) > 0 else None,
                    "amenities": {
                        "restaurants": int(metadata.get('restaurant', 0)),
                        "schools": int(metadata.get('school', 0)),
                        "parks": int(metadata.get('park', 0)),
                        "cafes": int(metadata.get('cafe', 0))
                    }
                }
            }
            
            # Add financial info if budget was specified
            if 'monthly_rent' in rec:
                recommendation['financial'] = {
                    "monthly_rent": int(rec['monthly_rent']),
                    "budget_remaining": int(rec['budget_remaining'])
                }
            
            response_data['recommendations'].append(recommendation)
        
        print(f"✅ Returning {len(recommendations)} recommendations\n")
        
        return jsonify(response_data), 200
    
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "error": str(e),
            "type": type(e).__name__
        }), 500


@app.route('/api/neighborhoods', methods=['GET'])
def list_neighborhoods():
    """List all available neighborhoods"""
    try:
        if agent is None:
            return jsonify({"error": "Agent not initialized"}), 503
        
        neighborhoods = []
        for _, row in agent.df.iterrows():
            neighborhoods.append({
                "mahalle": row['Mahalle'],
                "ilce": row['İlçe'],
                "green_index": round(row['Green_Index'], 2),
                "welfare_index": round(row['Society_Welfare_Index'], 2),
                "rent_per_sqm": int(row['Avg_Rent_Per_SqM'])
            })
        
        return jsonify({
            "status": "success",
            "total": len(neighborhoods),
            "neighborhoods": neighborhoods
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def stats():
    """Get database statistics"""
    try:
        if agent is None:
            return jsonify({"error": "Agent not initialized"}), 503
        
        df = agent.df
        
        stats_data = {
            "status": "success",
            "statistics": {
                "total_neighborhoods": len(df),
                "districts": df['İlçe'].nunique(),
                "avg_green_index": round(df['Green_Index'].mean(), 2),
                "avg_welfare_index": round(df['Society_Welfare_Index'].mean(), 2),
                "avg_rent_per_sqm": int(df['Avg_Rent_Per_SqM'].mean()),
                "rent_range": {
                    "min": int(df['Avg_Rent_Per_SqM'].min()),
                    "max": int(df['Avg_Rent_Per_SqM'].max())
                },
                "total_restaurants": int(df['restaurant'].sum()),
                "total_schools": int(df['school'].sum()),
                "total_parks": int(df['park'].sum()),
                "total_cafes": int(df['cafe'].sum())
            }
        }
        
        return jsonify(stats_data), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "error": "Endpoint not found",
        "available_endpoints": [
            "GET /health",
            "POST /api/recommend",
            "GET /api/neighborhoods",
            "GET /api/stats"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "status": "error",
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("ISTANBUL NEIGHBORHOOD RECOMMENDATION API")
    print("="*70)
    print("\nAvailable endpoints:")
    print("  GET  /health              - Health check")
    print("  POST /api/recommend       - Get neighborhood recommendations")
    print("  GET  /api/neighborhoods   - List all neighborhoods")
    print("  GET  /api/stats           - Get database statistics")
    print("\n" + "="*70 + "\n")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
