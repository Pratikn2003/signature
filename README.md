# SIGNIFY — Signature Forgery Detection System

Signify is a digital signature verification web application that provides intelligent authentication to ensure document integrity and eliminate fraudulent signature risks.

## Live Demo

**Frontend (GitHub Pages):** https://pratikn2003.github.io/signature/

**Backend (Render):** https://signature-e63s.onrender.com

## Project Structure

```
├── index.html              # Main frontend page
├── assets/
│   ├── css/                # Stylesheets
│   ├── js/                 # Frontend JavaScript
│   └── img/                # Images and icons
└── backend/
    ├── app.py              # Flask API server
    ├── preprocessing.py    # Image preprocessing
    ├── feature_extraction.py # HOG feature extraction
    ├── requirements.txt    # Python dependencies
    ├── Procfile            # Render deployment config
    └── runtime.txt         # Python version
```

## Setup

### Frontend
Open `index.html` in a browser or serve via a local HTTP server (e.g., Live Server on port 5500).

### Backend
```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend API runs on port 5000 by default for local development. For production, the frontend is configured to use the Render deployment URL.
