# 🏠 Istanbul Neighborhood Recommendation System# llama-hackathon

https://ulasav.csb.gov.tr/dataset/34-mahalle-bazli-bina-analiz-verisi

An intelligent AI-powered real estate recommendation system that helps users find the perfect neighborhood in Istanbul based on their preferences, using LLM-based natural language understanding, vector embeddings, and comprehensive Istanbul datasets.https://sonuc.ysk.gov.tr/sorgu

https://data.ibb.gov.tr/ 

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)https://sonuc.ysk.gov.tr/sorgu

[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)https://data.ibb.gov.tr/ 


# Terminal 1: Start your API

## 📋 Table of Contentspython api_endpoint_v2.py

- [Project Description](#-project-description)

- [Features](#-features)# Terminal 2: Test it

- [Technologies Used](#-technologies-used)python test_api.py

- [System Architecture](#-system-architecture)

- [Installation](#-installation)# Then open index.html in browser

- [Usage](#-usage)

- [API Documentation](#-api-documentation)# 🏠 Istanbul Neighborhood Recommendation System - Complete Package

- [Data Sources](#-data-sources)

- [Development Notes](#-development-notes)## 📦 What's Included

- [Team Members](#-team-members)

- [Demo Screenshots](#-demo-screenshots)### Backend Files:

1. **`api_endpoint_v2.py`** - Flask API server (main backend)

---2. **`main_v4.py`** - Agent with reasoning and recommendations

3. **`groq_llm_init.py`** - Groq LLM wrapper

## 🎯 Project Description4. **`vector_db_creation.py`** - ChromaDB setup



The **Istanbul Neighborhood Recommendation System** is an AI-powered agent that helps users discover ideal neighborhoods in Istanbul based on natural language queries. The system combines:### Frontend Files:

1. **`index.html`** - Beautiful web interface

- **Natural Language Processing**: Users can express preferences in conversational Turkish or English2. **`frontend_script.js`** - Frontend logic

- **Intelligent Filtering**: Multi-dimensional filtering based on budget, amenities, earthquake safety, and public transportation

- **Semantic Search**: Vector embeddings for context-aware neighborhood matching### Testing & Documentation:

- **Real Data**: Comprehensive Istanbul datasets including demographics, amenities, earthquake simulations, and infrastructure1. **`test_api.py`** - API testing script

2. **`INTEGRATION_GUIDE.md`** - Complete API documentation

### Purpose3. **`START_API.bat`** - Quick start script for Windows



Finding the right neighborhood is a critical decision for renters and buyers. This system simplifies the search by:---

1. Understanding complex, natural language queries

2. Applying intelligent filters across multiple data dimensions## 🚀 Quick Start (3 Steps)

3. Providing transparent reasoning for recommendations

4. Showing earthquake safety data from official simulations### Step 1: Start the Backend

5. Displaying detailed neighborhood characteristics```bash

python api_endpoint_v2.py

---```



## ✨ FeaturesOr double-click `START_API.bat`



### 🧠 AI-Powered Understanding### Step 2: Open Frontend

- **Natural Language Queries**: Express preferences conversationallyOpen `index.html` in your browser

- **Context Extraction**: Automatically extracts budget, amenities, safety concerns, and lifestyle preferences

- **Reasoning Transparency**: Shows why each neighborhood was recommended### Step 3: Try a Query!

Example: `"Aile için iyi okulları olan, bütçe 40000"`

### 🔍 Comprehensive Filtering

- **Budget & Rent**: Filter by monthly budget and apartment size---

- **Amenities**: Schools, parks, restaurants, cafes, hospitals, pharmacies

- **Public Transportation**: Bus, train, and transit station access## 🎯 Integration with Your Friend's Website

- **Earthquake Safety**: Filter by expected casualties and building damage (based on official simulations)

- **Quality of Life**: Green spaces, welfare index, walkability scoresYour friend's website expects:

- **Population Density**: Quiet vs vibrant neighborhoods- **Endpoint:** `POST /api/recommend`

- **Request:** `{"query": "user query here"}`

### 📊 Rich Data Integration- **Port:** 5001

- **959 Istanbul Neighborhoods** with detailed metrics

- **Earthquake Simulation Data** from Istanbul Metropolitan Municipality### To integrate:

- **Amenity Counts** from OpenStreetMap and official sources

- **Demographic Data** including population, housing statistics1. **Update their `app.py` line 9:**

- **Political Data** for understanding neighborhood characteristics```python

- **Infrastructure Data** including building ages and qualityLLAMA_API_URL = 'http://localhost:5001/api/recommend'

```

### 🎨 User-Friendly Interface

- Clean, modern web interface2. **Or use the provided frontend:**

- Interactive recommendations   - Copy `index.html` and `frontend_script.js`

- Real-time query processing   - Already configured to work!

- Mobile-responsive design

---

---

## 📊 System Architecture

## 🛠 Technologies Used

```

### BackendUser Query (Turkish/English)

- **Python 3.9+**: Core programming language    ↓

- **Flask 3.0**: Web framework for REST APIFlask API (api_endpoint_v2.py)

- **Flask-CORS**: Cross-origin resource sharing    ↓

- **Pandas**: Data manipulation and analysisAgent (main_v4.py)

    ├→ Groq LLM (extract preferences + reasoning)

### AI & Machine Learning    ├→ Database Filter (apply constraints)

- **Groq API**: Fast LLM inference (Llama 3.3 70B)    └→ ChromaDB (semantic search)

- **LangChain**: LLM framework for development    ↓

- **Sentence Transformers**: Vector embeddings (all-MiniLM-L6-v2)Top 3 Recommendations

- **ChromaDB**: Vector database for semantic search    ↓

JSON Response to Frontend

### Frontend```

- **HTML5/CSS3**: Modern web standards

- **Vanilla JavaScript**: No framework overhead---

- **Responsive Design**: Mobile-first approach

## ✨ Key Features

### Data Processing

- **NumPy**: Numerical computations### 1. **Intelligent Understanding**

- **Python-dotenv**: Environment variable management- Understands both Turkish and English

- **JSON**: Data interchange format- Extracts implicit requirements (e.g., "green area" → min_green_index: 0.7)

- Provides reasoning for its decisions

---

### 2. **Smart Filtering**

## 🏗 System Architecture- Budget calculations

- Amenity requirements (schools, parks, restaurants)

```- Population limits (for quiet areas)

┌─────────────────────────────────────────────────────────────┐- Green space requirements

│                         Frontend                             │

│                    (index.html + JS)                         │### 3. **Semantic Search**

└──────────────────────┬──────────────────────────────────────┘- Vector database with 160 neighborhoods

                       │ HTTP/JSON- Finds neighborhoods matching the vibe/atmosphere

                       ▼- Not just keyword matching

┌─────────────────────────────────────────────────────────────┐

│                      Flask API Server                        │### 4. **Clean Data**

│                   (api_endpoint_v2.py)                       │- Automatically filters out "Unknown" neighborhoods

└──────────────────────┬──────────────────────────────────────┘- Handles missing data gracefully

                       │- Consistent formatting

                       ▼

┌─────────────────────────────────────────────────────────────┐---

│                  Neighborhood Agent                          │

│                      (main.py)                               │## 📋 API Endpoints

│  ┌──────────────────────────────────────────────────────┐   │

│  │  1. Preference Extraction (LLM)                      │   │### `POST /api/recommend`

│  │  2. Database Filtering (Pandas)                      │   │Get neighborhood recommendations

│  │  3. Semantic Search (ChromaDB + Embeddings)          │   │

│  │  4. Result Ranking & Explanation                     │   │**Request:**

│  └──────────────────────────────────────────────────────┘   │```json

└────────┬────────────────┬────────────────┬──────────────────┘{

         │                │                │  "query": "Aile için iyi okulları olan, bütçe 40000"

         ▼                ▼                ▼}

    ┌────────┐      ┌──────────┐    ┌────────────┐```

    │ Groq   │      │ ChromaDB │    │   CSV      │

    │  LLM   │      │  Vector  │    │   Data     │**Response:**

    │        │      │    DB    │    │            │```json

    └────────┘      └──────────┘    └────────────┘{

```  "status": "success",

  "reasoning": "Agent's reasoning...",

### Data Flow  "recommendations": [

    {

1. **User Query** → Frontend sends natural language query to API      "rank": 1,

2. **Preference Extraction** → LLM extracts structured preferences      "neighborhood": "Balmumcu",

3. **Hard Filtering** → Pandas filters by constraints (budget, amenities, safety)      "district": "Beşiktaş",

4. **Semantic Search** → Vector DB finds semantically similar neighborhoods      "similarity_score": 89.5,

5. **Ranking & Explanation** → Agent generates match reasons      "financial": {

6. **Response** → JSON with top 3 recommendations + reasoning        "monthly_rent": 28000,

        "budget_remaining": 12000

---      },

      "details": { ... }

## 📦 Installation    }

  ]

### Prerequisites}

- Python 3.9 or higher```

- pip (Python package manager)

- Groq API key (free at [groq.com](https://groq.com))### `GET /health`

Check if API is running

### Step 1: Clone the Repository

```bash### `GET /api/neighborhoods`

git clone https://github.com/nurgumus/llama-hackathon.gitList all neighborhoods

cd llama-hackathon

```### `GET /api/stats`

Database statistics

### Step 2: Create Virtual Environment (Recommended)

```bash---

# Windows

python -m venv venv## 🧪 Testing

venv\Scripts\activate

### Automatic Testing:

# macOS/Linux```bash

python3 -m venv venvpython test_api.py

source venv/bin/activate```

```

### Manual Testing:

### Step 3: Install Dependencies```bash

```bashcurl -X POST http://localhost:5001/api/recommend \

pip install -r requirements.txt  -H "Content-Type: application/json" \

```  -d '{"query":"yeşil alan, bütçe 30000"}'

```

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:---

```env

GROQ_API_KEY=your_groq_api_key_here## 🎨 Example Queries

```

### For Families:

To get a Groq API key:```

1. Visit [console.groq.com](https://console.groq.com)"Aile için iyi okulları olan, bütçe 40000, 100 metrekare"

2. Sign up for a free account"Çocuklu aileler için güvenli mahalle"

3. Generate an API key```

4. Copy it to your `.env` file

### For Nature Lovers:

### Step 5: Verify Installation```

```bash"Yeşil alan, en az 2 park, bütçe 30000"

python -c "import flask, pandas, chromadb, groq; print('✅ All dependencies installed!')""Köpeğimi gezdirebileceğim yeşil bir yer"

``````



---### For Social Life:

```

## 🚀 Usage"Canlı bir yer, çok restoran ve kafe"

"Gençlere uygun sosyal hayat"

### Quick Start (Windows)```

Double-click `START_ALL.bat` to launch both backend and frontend automatically.

### For Peace & Quiet:

### Manual Start```

"Sessiz ve sakin, nüfusu az bir yer"

#### Option 1: Start Backend Only"Huzurlu, emeklilere uygun mahalle"

```bash```

python api_endpoint_v2.py

```---

Server will start at `http://localhost:5000`## 📝 Notes



#### Option 2: Start Full System- API automatically filters out "Unknown" neighborhoods

Terminal 1 (Backend):- LLM understands both Turkish and English queries

```bash- Results are ranked by semantic similarity

python api_endpoint_v2.py- Financial calculations assume standard apartment sizes

```

## 🔧 Configuration

Terminal 2 (Frontend):

```bash### Required Environment Variables (`.env`):

cd frontend```env

python serve_frontend.pyGROQ_API_KEY=your_groq_api_key_here

``````

Or simply open `frontend/index.html` in your browser.

### Required Data Files:

### Example Queries- `istanbul_mahalle_complete_data_with_descriptions_with_descriptions.csv`

- `chroma_db/` directory

Try these queries in Turkish or English:

### Optional Configuration:

**Turkish:**Change port in `api_endpoint_v2.py`:

- `"Aile için iyi okulları olan, bütçe 40000 TL"````python

- `"Deprem güvenliği yüksek, yeşil alan çok olan mahalle"`app.run(host='0.0.0.0', port=5001, debug=True)

- `"İyi toplu taşıma, canlı, cafe ve restoran çok olan yer"````

- `"Sakin, az nüfuslu, doğal alan çok olan semtler"`

---

**English:**

- `"Family-friendly neighborhood with good schools, budget 40000"`## 🐛 Troubleshooting

- `"Earthquake safe area with lots of green spaces"`

- `"Vibrant area with good public transport and many cafes"`### "Agent not initialized"

- `"Quiet neighborhood with low population and parks"`- Check GROQ_API_KEY is set

- Verify CSV file exists

### Command Line Demo- Check ChromaDB directory exists

```bash

python main.py### "Backend çalışmıyor"

```- Make sure you ran `python api_endpoint_v2.py`

This runs the interactive demo with pre-configured example queries.- Check port 5001 is not in use

- Look for error messages in terminal

---

### No results returned

## 📡 API Documentation- Try more general queries

- Check database has data

### Base URL- Verify filters aren't too strict

```

http://localhost:5000---

```

## 📈 Performance

### Endpoints

- **Response time:** 2-5 seconds per query

#### 1. Health Check- **Concurrent users:** Supports multiple requests

```http- **Database:** 160 neighborhoods indexed

GET /health- **LLM:** Groq (fast inference)

```

---

**Response:**

```json## 🚢 Deployment Tips

{

  "status": "healthy",For production:

  "agent_initialized": true,1. Use `gunicorn` instead of Flask dev server

  "llm_initialized": true2. Set `debug=False`

}3. Add rate limiting

```4. Add authentication

5. Use HTTPS

#### 2. Get Recommendations6. Set proper CORS origins

```http

POST /api/recommendExample:

Content-Type: application/json```bash

```gunicorn -w 4 -b 0.0.0.0:5001 api_endpoint_v2:app

```

**Request Body:**

```json---

{

  "query": "family neighborhood with good schools, budget 40000"

}
```

**Response:**
```json
{
  "status": "success",
  "query": "family neighborhood with good schools, budget 40000",
  "reasoning": "The user is looking for a family-friendly neighborhood...",
  "preferences": {
    "monthly_budget": 40000,
    "min_schools": 2,
    "min_parks": 2,
    "preferences_text": "family neighborhood with good schools"
  },
  "filters_applied": [
    "Budget: ≤40,000 TRY/month",
    "Schools: ≥2",
    "Parks: ≥2"
  ],
  "total_neighborhoods": 959,
  "filtered_neighborhoods": 234,
  "recommendations": [
    {
      "rank": 1,
      "neighborhood": "Acıbadem",
      "district": "Üsküdar",
      "similarity_score": 95.3,
      "match_reasons": [
        "Has 8 schools",
        "Has 3 parks",
        "Well under budget (saves 12,500 TRY)"
      ],
      "details": {
        "green_index": 0.85,
        "welfare_index": 0.92,
        "population": 15420,
        "amenities": {
          "restaurants": 12,
          "schools": 8,
          "parks": 3,
          "cafes": 15
        }
      },
      "financial": {
        "monthly_rent": 27500,
        "budget_remaining": 12500
      }
    }
  ]
}
```

#### 3. Get Neighborhood Details
```http
GET /api/neighborhood/{district}/{neighborhood}
```

**Response:** Detailed information about a specific neighborhood.

### Error Responses

**400 Bad Request:**
```json
{
  "error": "Query parameter is required",
  "status": "error"
}
```

**503 Service Unavailable:**
```json
{
  "error": "Agent not initialized",
  "status": "error"
}
```

---

## 📊 Data Sources

This project integrates multiple official and open datasets:

### 1. Istanbul Metropolitan Municipality (İBB)
- **Earthquake Simulation Data**: Building damage and casualty projections
- **Neighborhood Statistics**: Demographics, infrastructure
- **Source**: [data.ibb.gov.tr](https://data.ibb.gov.tr/)

### 2. Supreme Electoral Council (YSK)
- **Electoral Data**: Political preferences by neighborhood
- **Source**: [sonuc.ysk.gov.tr](https://sonuc.ysk.gov.tr/sorgu)

### 3. General Directorate of Civil Protection (AFAD)
- **Building Analysis**: Seismic vulnerability assessments
- **Source**: [ulasav.csb.gov.tr](https://ulasav.csb.gov.tr/dataset/34-mahalle-bazli-bina-analiz-verisi)

### 4. OpenStreetMap
- **Amenity Data**: Schools, parks, restaurants, cafes, hospitals, pharmacies
- **Transportation**: Bus, train, and transit stations

### Dataset Statistics
- **959 Neighborhoods** across all Istanbul districts
- **50+ Features** per neighborhood including:
  - Demographics (population, density)
  - Quality of life indices (welfare, walkability, green space)
  - Amenities (restaurants, schools, parks, cafes, etc.)
  - Transportation (bus, train, transit stations)
  - Earthquake safety (casualties, building damage projections)
  - Infrastructure (building ages, floor counts)
  - Political preferences (election results)

---

## 💡 Development Notes

### LLM Backend Options

This project supports **two LLM backend configurations**:

#### 1. Groq API (Production - Current)
**Used for**: Fast testing, demos, and deployment
- **Model**: Llama 3.3 70B Versatile
- **Speed**: ~500 tokens/second
- **Cost**: Free tier available
- **Configuration**: `utils/groq_llm_init.py`

#### 2. Self-Hosted vLLM (Development)
**Used for**: Most of the development phase
- **Deployment**: Google Colab with GPU
- **Tunnel**: ngrok for external access
- **Model**: Llama 3.1 8B Instruct or Llama 3.2 3B Instruct
- **Configuration**: `utils/llm_init.py`

**Why we used both approaches:**

During **development**, we used a **self-hosted Llama model on Google Colab** with GPU acceleration, exposed via ngrok. This gave us:
- ✅ Unlimited experimentation without API costs
- ✅ Full control over model parameters
- ✅ Ability to test with different model sizes
- ✅ No rate limits during iterative development

For **fast testing and demos**, we switched to **Groq API** because:
- ✅ Blazing fast inference (~500 tokens/sec)
- ✅ Reliable uptime without managing infrastructure
- ✅ Easy to share and deploy
- ✅ Free tier sufficient for demos

### Setting Up Self-Hosted vLLM (Optional)

If you want to replicate our development setup with self-hosted vLLM:

1. **Open Google Colab** with GPU runtime (T4 or better)

2. **Install vLLM**:
```python
!pip install vllm pyngrok
```

3. **Start vLLM server**:
```python
from vllm import LLM
import subprocess

# Start vLLM OpenAI-compatible server
subprocess.Popen([
    "python", "-m", "vllm.entrypoints.openai.api_server",
    "--model", "meta-llama/Llama-3.1-8B-Instruct",
    "--port", "8000"
])
```

4. **Expose with ngrok**:
```python
from pyngrok import ngrok

# Create tunnel
public_url = ngrok.connect(8000)
print(f"🌐 Public URL: {public_url}")
```

5. **Update `.env`**:
```env
NGROK_API_URL=https://your-ngrok-url.ngrok.io/v1/chat/completions
```

6. **Switch backend in code**:
```python
# In main.py, change:
from utils.llm_init import llm  # Self-hosted vLLM
# Instead of:
from utils.groq_llm_init import groq_llm  # Groq API
```

### Vector Database

The system uses **ChromaDB** with pre-computed embeddings:
- **Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimension**: 384
- **Storage**: `./chroma_db/`

To rebuild the vector database:
```bash
python utils/vector_db_creation.py
```

---

## 👥 Team Members

- **Nur Gumus** - AI/ML Engineer & Project Lead
- **[Team Member 2]** - Backend Developer
- **[Team Member 3]** - Frontend Developer
- **[Team Member 4]** - Data Engineer

*Please update with your actual team members' names, roles, and optionally GitHub profiles or LinkedIn links.*

---

## 📸 Demo Screenshots

### Main Interface
*[Screenshots will be added here]*

### Query Example
*[Add screenshot showing a query and results]*

### Earthquake Safety Information
*[Add screenshot showing earthquake data visualization]*

### Neighborhood Details
*[Add screenshot of detailed neighborhood view]*

---

## 🗂 Project Structure

```
llama-hackathon/
├── main.py                          # Core agent with reasoning logic
├── api_endpoint_v2.py               # Flask REST API
├── requirements.txt                 # Python dependencies
├── START_ALL.bat                    # Quick start script (Windows)
├── .env                             # Environment variables (create this)
├── README.md                        # This file
├── INTEGRATION_GUIDE.md             # Detailed API integration guide
│
├── frontend/                        # Web interface
│   ├── index.html                   # Main page
│   ├── index2.html                  # Alternative interface
│   ├── frontend_script.js           # Client-side logic
│   ├── frontend_script2.js          # Alternative client logic
│   ├── serve_frontend.py            # Simple HTTP server
│   └── START_FRONTEND.bat           # Frontend launcher
│
├── utils/                           # Utility modules
│   ├── groq_llm_init.py            # Groq API integration (current)
│   ├── llm_init.py                 # Self-hosted vLLM integration
│   └── vector_db_creation.py       # ChromaDB setup
│
├── tests/                           # Test scripts
│   ├── test_api.py                 # API endpoint tests
│   └── test_client.py              # Integration tests
│
├── istanbul_data/                   # Raw data files
│   ├── deprem-senaryosu-analiz-sonuclar.csv
│   ├── mahalle_geojson.json
│   ├── istanbul_mahalle_complete_data_with_descriptions.csv
│   └── ...
│
├── description_generation/          # Neighborhood description generation
│   ├── csv_create.ipynb            # Data aggregation notebook
│   └── description-70B.ipynb       # Description generation with Llama 70B
│
├── chroma_db/                       # Vector database (generated)
│   └── ...
│
└── neighborhoods_with_descriptions.csv  # Main dataset (959 neighborhoods)
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required for Groq API (current setup)
GROQ_API_KEY=your_groq_api_key

# Optional (for self-hosted vLLM during development)
NGROK_API_URL=https://your-ngrok-url.ngrok.io/v1/chat/completions

# Optional (API configuration)
FLASK_PORT=5000
FLASK_DEBUG=False
```

---

## 🧪 Testing

Run the test suite:

```bash
# Test API endpoints
python tests/test_api.py

# Test client integration
python tests/test_client.py
```

---

## 🚧 Troubleshooting

### Common Issues

**1. "GROQ_API_KEY not found"**
- Ensure `.env` file exists in project root
- Check that API key is correctly formatted without quotes

**2. "Agent not initialized"**
- Verify `neighborhoods_with_descriptions.csv` exists
- Check that ChromaDB directory (`chroma_db/`) is present
- Ensure all dependencies are installed

**3. "No neighborhoods match your constraints"**
- Try relaxing query constraints (e.g., higher budget)
- Check budget values are reasonable (20,000-60,000 TRY typical range)
- Use broader amenity requirements

**4. Import errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again
- Check Python version (must be 3.9+)

**5. "Unable to extract preferences"**
- Check that LLM is responding (look at terminal logs)
- Verify GROQ_API_KEY is valid
- Try rephrasing the query more explicitly

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Contact

For questions or feedback, please open an issue on GitHub or contact the team.

---

## 🙏 Acknowledgments

- **Istanbul Metropolitan Municipality** for providing comprehensive open data
- **Groq** for fast LLM inference API and free tier access
- **Meta AI** for the Llama models (3.1, 3.2, 3.3)
- **Google Colab** for free GPU resources during development
- **Sentence Transformers** for embedding models
- **ChromaDB** for vector database technology
- **ngrok** for secure tunneling during development

---

**Built with ❤️ for Istanbul residents seeking their perfect neighborhood**
