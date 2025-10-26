# Istanbul Neighborhood Recommendation - Frontend

Beautiful web interface for the Istanbul neighborhood recommendation system.

## 📁 Files

- `index.html` - Main HTML page with beautiful gradient design
- `frontend_script.js` - JavaScript handling API communication and UI
- `serve_frontend.py` - Simple HTTP server to serve the frontend
- `START_FRONTEND.bat` - Windows launcher for the frontend server

## 🚀 How to Use

### Option 1: Using the Batch File (Windows)

1. **Start the API server** (in parent directory):
   ```bash
   python api_endpoint_v2.py
   ```

2. **Start the frontend server**:
   - Double-click `START_FRONTEND.bat`
   - OR run in terminal: `python serve_frontend.py`

3. **Open in browser**:
   - Go to: http://localhost:8000

### Option 2: Manual Setup

1. **Start API** (port 5001):
   ```bash
   cd ..
   python api_endpoint_v2.py
   ```

2. **Start Frontend** (port 8000):
   ```bash
   cd frontend
   python serve_frontend.py
   ```

3. **Open Browser**:
   - Navigate to http://localhost:8000
   - You should see the Istanbul Emlak Öneri Sistemi interface

## ⚠️ Important Notes

### Why Not Open HTML Directly?

❌ **Don't** open `index.html` directly in your browser (file:// protocol)

✅ **Do** use the HTTP server (http://localhost:8000)

**Reason:** Modern browsers block AJAX requests from `file://` to `http://` due to CORS security. You need to serve the HTML through a web server.

### Troubleshooting

**"Backend sunucusuna bağlanılamıyor" Error:**
- Make sure `api_endpoint_v2.py` is running on port 5001
- Check terminal output: should say "Agent ready to serve requests"
- Test API: http://localhost:5001/health

**No results showing:**
- Open browser console (F12 → Console tab)
- Check for JavaScript errors
- Verify API response with: 
  ```bash
  curl -X POST http://localhost:5001/api/recommend -H "Content-Type: application/json" -d "{\"query\": \"test\"}"
  ```

**CORS errors:**
- Use the HTTP server (serve_frontend.py), don't open HTML directly
- API already has CORS enabled in api_endpoint_v2.py

## 🎨 Features

- **Beautiful UI**: Modern gradient design with smooth animations
- **Real-time Search**: Instant recommendations as you type
- **Smart Display**: Shows reasoning, filters, and match explanations
- **Financial Info**: Budget analysis and rent estimates (when budget specified)
- **Responsive**: Works on desktop and mobile
- **Turkish Language**: Full Turkish interface

## 🧪 Example Queries

Try these in the search box:

- "Aileye uygun, yeşil alanlı ve okulları yakın bir yer arıyorum"
- "Bütçem 20000 TL, merkeze yakın, kafeleri bol bir yer"
- "Sakin, huzurlu, doğayla iç içe bir mahalle"
- "Genç profesyonellere uygun, canlı, sosyal olanakları iyi"

## 📡 API Communication

The frontend communicates with the backend API:

**Endpoint**: `http://localhost:5001/api/recommend`

**Request**:
```json
{
  "query": "Your search query in Turkish"
}
```

**Response**:
```json
{
  "status": "success",
  "query": "...",
  "reasoning": "...",
  "recommendations": [
    {
      "rank": 1,
      "neighborhood": "...",
      "district": "...",
      "similarity_score": 32.3,
      "match_reasons": [...],
      "details": {...},
      "financial": {...}
    }
  ]
}
```

## 🔧 Customization

### Change API URL

Edit `frontend_script.js` line 2:
```javascript
const API_URL = 'http://localhost:5001/api/recommend';
```

### Change Frontend Port

Edit `serve_frontend.py` line 9:
```python
PORT = 8000  # Change to any port
```

## 📦 Integration

To integrate with another website:
1. Copy `index.html` and `frontend_script.js` to your project
2. Update `API_URL` in the JavaScript
3. Ensure CORS is enabled on your backend
4. Serve through a web server (not file://)

## 🎯 Project Structure

```
frontend/
├── index.html              # Main HTML page
├── frontend_script.js      # JavaScript logic
├── serve_frontend.py       # HTTP server
├── START_FRONTEND.bat      # Windows launcher
└── README.md              # This file
```

## 💡 Tips

- Keep both servers running while using the app
- Check browser console for detailed logs
- Use example queries for quick testing
- Copy results button copies to clipboard
- Backend test: http://localhost:5001/health

---

**Need Help?** Check the main project README or INTEGRATION_GUIDE.md
