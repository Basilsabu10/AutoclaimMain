# AutoClaim Server

FastAPI backend for insurance claim processing with AI-powered damage analysis.

## 📁 Project Structure

```
server/
├── app/                      # Main application package
│   ├── __init__.py
│   ├── main.py               # FastAPI app, CORS, routes
│   │
│   ├── api/                  # API Routes
│   │   ├── __init__.py
│   │   ├── auth.py           # /register, /login, /me
│   │   └── claims.py         # /claims/* endpoints
│   │
│   ├── core/                 # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py         # Settings from .env
│   │   ├── security.py       # JWT, password hashing
│   │   └── dependencies.py   # FastAPI dependencies
│   │
│   ├── db/                   # Database layer
│   │   ├── __init__.py
│   │   ├── database.py       # SQLAlchemy engine/session
│   │   └── models.py         # User, Claim, Policy models
│   │
│   └── services/             # AI & business logic
│       ├── __init__.py
│       ├── ai_orchestrator.py  # Main AI pipeline
│       ├── groq_service.py     # Groq LLaMA Vision
│       ├── gemini_service.py   # Google Gemini fallback
│       ├── yolo_service.py     # Object detection
│       ├── exif_service.py     # Image metadata
│       └── ocr_service.py      # Number plate OCR
│
├── scripts/                  # Utility scripts
├── tests/                    # Test files
├── data/                     # ML models (yolov8n.pt)
├── uploads/                  # User uploaded files
│
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
├── run.py                    # Entry point
└── README.md                 # This file
```

## 🚀 Quick Start

```bash
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
python run.py
```

Server runs at: http://localhost:8000

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register new user |
| POST | `/login` | Get access token |
| GET | `/me` | Current user info |

### Claims
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/claims` | Submit new claim with images |
| GET | `/claims/my` | Get user's claims |
| GET | `/claims/all` | Get all claims (admin) |
| GET | `/claims/{id}` | Get claim details |
| PUT | `/claims/{id}/status` | Update status (admin) |
| POST | `/claims/{id}/analyze` | Re-run AI analysis (admin) |

## 🤖 AI Pipeline

The AI analysis pipeline processes claims through:

1. **EXIF Extraction** (`exif_service.py`)
   - Extract timestamp, GPS location from image metadata
   - Falls back to filename parsing

2. **OCR** (`ocr_service.py`)
   - Extract vehicle number plate using EasyOCR

3. **YOLO Detection** (`yolo_service.py`)
   - Detect vehicles and objects in images
   - Uses YOLOv8n model

4. **LLM Analysis** (`groq_service.py` / `gemini_service.py`)
   - Damage type classification (scratch, dent, collision, etc.)
   - Severity assessment (minor, moderate, severe)
   - Cost estimation
   - Recommendation (approve, review, reject)

## ⚙️ Configuration

Edit `.env` file:

```env
# AI Services
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key

# Security (change in production!)
SECRET_KEY=your_secret_key
```

## 🧪 Testing

```bash
# Test AI pipeline
python tests/test_pipeline.py
```

## 📦 Key Dependencies

- **FastAPI** - Web framework
- **SQLAlchemy** - Database ORM
- **ultralytics** - YOLOv8 object detection
- **groq** - Groq LLaMA API
- **google-generativeai** - Gemini API
- **Pillow** - Image processing
- **python-jose** - JWT tokens
