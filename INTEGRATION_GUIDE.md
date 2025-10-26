# Istanbul Neighborhood Recommendation System - Integration Guide

## 🚀 Quick Start

### 1. Start the Backend API
```bash
python api_endpoint_v2.py
```

The API will run on `http://localhost:5001`

### 2. Open the Frontend
Simply open `index.html` in your browser, or use a simple HTTP server:

```bash
# Using Python
python -m http.server 8000

# Then visit: http://localhost:8000
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:5001
```

### Endpoints

#### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "llm_initialized": true
}
```

#### 2. Get Recommendations
```http
POST /api/recommend
```

**Request Body:**
```json
{
  "query": "Aile için iyi okulları olan, bütçe 40000, 100 metrekare"
}
```

**Response:**
```json
{
  "status": "success",
  "query": "Aile için iyi okulları olan, bütçe 40000, 100 metrekare",
  "reasoning": "The user is looking for a family-friendly neighborhood...",
  "preferences": {
    "monthly_budget": 40000,
    "apartment_size_sqm": 100,
    "min_schools": 2
  },
  "filters_applied": [
    "Budget: ≤40,000 TRY/month",
    "Schools: ≥2"
  ],
  "total_neighborhoods": 160,
  "filtered_neighborhoods": 45,
  "recommendations": [
    {
      "rank": 1,
      "neighborhood": "Balmumcu",
      "district": "Beşiktaş",
      "similarity_score": 89.5,
      "match_reasons": [
        "Well under budget (saves 12,000 TRY)",
        "Has 13 schools"
      ],
      "details": {
        "green_index": 0.93,
        "welfare_index": 1.0,
        "population": 5988,
        "amenities": {
          "restaurants": 0,
          "schools": 13,
          "parks": 2,
          "cafes": 4
        }
      },
      "financial": {
        "monthly_rent": 28000,
        "budget_remaining": 12000
      }
    }
  ]
}
```

#### 3. List All Neighborhoods
```http
GET /api/neighborhoods
```

**Response:**
```json
{
  "status": "success",
  "total": 160,
  "neighborhoods": [
    {
      "mahalle": "Balmumcu",
      "ilce": "Beşiktaş",
      "green_index": 0.93,
      "welfare_index": 1.0,
      "rent_per_sqm": 560
    }
  ]
}
```

#### 4. Get Statistics
```http
GET /api/stats
```

**Response:**
```json
{
  "status": "success",
  "statistics": {
    "total_neighborhoods": 160,
    "districts": 39,
    "avg_green_index": 0.67,
    "avg_welfare_index": 0.75,
    "avg_rent_per_sqm": 320,
    "rent_range": {
      "min": 200,
      "max": 560
    },
    "total_restaurants": 1250,
    "total_schools": 890,
    "total_parks": 540,
    "total_cafes": 980
  }
}
```

---

## 🔗 Integrating with Your Friend's Frontend

### Option 1: Update the Backend URL in their script.js
Change the API endpoint in their `script.js`:

```javascript
const API_URL = 'http://localhost:5001/api/recommend';
```

### Option 2: Use the provided frontend
- Copy `index.html` and `frontend_script.js` to your project
- They're already configured to work with `api_endpoint_v2.py`

---

## 🎯 Example Queries

### Turkish Examples:
```
"Aile için iyi okulları olan, bütçe 40000, 100 metrekare"
"Yeşil alan, en az 2 park, bütçe 30000"
"Canlı bir yer, çok restoran ve kafe"
"Sessiz ve sakin, nüfusu az bir yer"
"Denize yakın, modern bir mahalle"
```

### English Examples:
```
"family neighborhood with good schools, budget 40000 for 100 sqm"
"green quiet area with at least 2 parks, budget 30000"
"vibrant area with many restaurants and cafes"
"quiet peaceful neighborhood with low population"
"modern neighborhood near the sea"
```

---

## 🛠️ Architecture

```
┌─────────────────┐
│   Frontend      │
│  (index.html)   │
└────────┬────────┘
         │ HTTP POST
         │ /api/recommend
         ▼
┌─────────────────┐
│  Flask API      │
│ (api_endpoint   │
│     _v2.py)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Agent (main_v4) │
│  - LLM Extract  │
│  - DB Filter    │
│  - Vector Search│
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│ Groq   │ │ ChromaDB │
│ LLM    │ │ Vectors  │
└────────┘ └──────────┘
```

---

## 📋 Requirements

Install dependencies:
```bash
pip install flask flask-cors pandas chromadb sentence-transformers groq python-dotenv
```

---

## 🔧 Configuration

### Environment Variables (.env)
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Data Files Required:
- `istanbul_mahalle_complete_data_with_descriptions_with_descriptions.csv`
- `chroma_db/` directory with vector embeddings

---

## 🐛 Troubleshooting

### Backend won't start:
- Check if Groq API key is set in `.env`
- Verify CSV file exists
- Check if ChromaDB directory exists

### No results returned:
- Try more general queries
- Check database has data loaded
- Verify filters aren't too restrictive

### CORS errors:
- Backend includes CORS headers
- Check frontend is hitting correct URL

---

## 📞 API Response Format

All responses include:
- `status`: "success" or "error"
- `error`: Error message (if status is "error")

Success responses vary by endpoint but follow consistent structure.

---

## 🎨 Customization

### Change Port:
In `api_endpoint_v2.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Change Number of Results:
In the agent call:
```python
recommendations = agent.search_with_constraints(preferences, n_results=3)
```

### Adjust Filters:
Modify `filter_by_constraints()` in `main_v4.py`

---

## 📊 Testing

### Test with curl:
```bash
curl -X POST http://localhost:5001/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"query":"yeşil alan, bütçe 30000"}'
```

### Test health:
```bash
curl http://localhost:5001/health
```

---

## 🚀 Deployment Notes

For production:
1. Set `debug=False` in Flask app
2. Use a proper WSGI server (gunicorn, waitress)
3. Set appropriate CORS origins
4. Add rate limiting
5. Add authentication if needed

Example with gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5001 api_endpoint_v2:app
```

---

## 📝 Notes

- API automatically filters out "Unknown" neighborhoods
- LLM understands both Turkish and English queries
- Results are ranked by semantic similarity
- Financial calculations assume standard apartment sizes
