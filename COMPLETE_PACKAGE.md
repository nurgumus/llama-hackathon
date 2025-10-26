# 🏠 Istanbul Neighborhood Recommendation System - Complete Package

## 📦 What's Included

### Backend Files:
1. **`api_endpoint_v2.py`** - Flask API server (main backend)
2. **`main_v4.py`** - Agent with reasoning and recommendations
3. **`groq_llm_init.py`** - Groq LLM wrapper
4. **`vector_db_creation.py`** - ChromaDB setup

### Frontend Files:
1. **`index.html`** - Beautiful web interface
2. **`frontend_script.js`** - Frontend logic

### Testing & Documentation:
1. **`test_api.py`** - API testing script
2. **`INTEGRATION_GUIDE.md`** - Complete API documentation
3. **`START_API.bat`** - Quick start script for Windows

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start the Backend
```bash
python api_endpoint_v2.py
```

Or double-click `START_API.bat`

### Step 2: Open Frontend
Open `index.html` in your browser

### Step 3: Try a Query!
Example: `"Aile için iyi okulları olan, bütçe 40000"`

---

## 🎯 Integration with Your Friend's Website

Your friend's website expects:
- **Endpoint:** `POST /api/recommend`
- **Request:** `{"query": "user query here"}`
- **Port:** 5001

### To integrate:

1. **Update their `app.py` line 9:**
```python
LLAMA_API_URL = 'http://localhost:5001/api/recommend'
```

2. **Or use the provided frontend:**
   - Copy `index.html` and `frontend_script.js`
   - Already configured to work!

---

## 📊 System Architecture

```
User Query (Turkish/English)
    ↓
Flask API (api_endpoint_v2.py)
    ↓
Agent (main_v4.py)
    ├→ Groq LLM (extract preferences + reasoning)
    ├→ Database Filter (apply constraints)
    └→ ChromaDB (semantic search)
    ↓
Top 3 Recommendations
    ↓
JSON Response to Frontend
```

---

## ✨ Key Features

### 1. **Intelligent Understanding**
- Understands both Turkish and English
- Extracts implicit requirements (e.g., "green area" → min_green_index: 0.7)
- Provides reasoning for its decisions

### 2. **Smart Filtering**
- Budget calculations
- Amenity requirements (schools, parks, restaurants)
- Population limits (for quiet areas)
- Green space requirements

### 3. **Semantic Search**
- Vector database with 160 neighborhoods
- Finds neighborhoods matching the vibe/atmosphere
- Not just keyword matching

### 4. **Clean Data**
- Automatically filters out "Unknown" neighborhoods
- Handles missing data gracefully
- Consistent formatting

---

## 📋 API Endpoints

### `POST /api/recommend`
Get neighborhood recommendations

**Request:**
```json
{
  "query": "Aile için iyi okulları olan, bütçe 40000"
}
```

**Response:**
```json
{
  "status": "success",
  "reasoning": "Agent's reasoning...",
  "recommendations": [
    {
      "rank": 1,
      "neighborhood": "Balmumcu",
      "district": "Beşiktaş",
      "similarity_score": 89.5,
      "financial": {
        "monthly_rent": 28000,
        "budget_remaining": 12000
      },
      "details": { ... }
    }
  ]
}
```

### `GET /health`
Check if API is running

### `GET /api/neighborhoods`
List all neighborhoods

### `GET /api/stats`
Database statistics

---

## 🧪 Testing

### Automatic Testing:
```bash
python test_api.py
```

### Manual Testing:
```bash
curl -X POST http://localhost:5001/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"query":"yeşil alan, bütçe 30000"}'
```

---

## 🎨 Example Queries

### For Families:
```
"Aile için iyi okulları olan, bütçe 40000, 100 metrekare"
"Çocuklu aileler için güvenli mahalle"
```

### For Nature Lovers:
```
"Yeşil alan, en az 2 park, bütçe 30000"
"Köpeğimi gezdirebileceğim yeşil bir yer"
```

### For Social Life:
```
"Canlı bir yer, çok restoran ve kafe"
"Gençlere uygun sosyal hayat"
```

### For Peace & Quiet:
```
"Sessiz ve sakin, nüfusu az bir yer"
"Huzurlu, emeklilere uygun mahalle"
```

---

## 🔧 Configuration

### Required Environment Variables (`.env`):
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Required Data Files:
- `istanbul_mahalle_complete_data_with_descriptions_with_descriptions.csv`
- `chroma_db/` directory

### Optional Configuration:
Change port in `api_endpoint_v2.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

---

## 🐛 Troubleshooting

### "Agent not initialized"
- Check GROQ_API_KEY is set
- Verify CSV file exists
- Check ChromaDB directory exists

### "Backend çalışmıyor"
- Make sure you ran `python api_endpoint_v2.py`
- Check port 5001 is not in use
- Look for error messages in terminal

### No results returned
- Try more general queries
- Check database has data
- Verify filters aren't too strict

---

## 📈 Performance

- **Response time:** 2-5 seconds per query
- **Concurrent users:** Supports multiple requests
- **Database:** 160 neighborhoods indexed
- **LLM:** Groq (fast inference)

---

## 🚢 Deployment Tips

For production:
1. Use `gunicorn` instead of Flask dev server
2. Set `debug=False`
3. Add rate limiting
4. Add authentication
5. Use HTTPS
6. Set proper CORS origins

Example:
```bash
gunicorn -w 4 -b 0.0.0.0:5001 api_endpoint_v2:app
```

---


