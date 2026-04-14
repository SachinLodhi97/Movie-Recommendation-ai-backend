import requests
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from model_utils import recommender
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
API_KEY = os.getenv("API_KEY")

BASE_URL = "https://api.themoviedb.org/3"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

def fetch(url, params=None):
    try:
        r = requests.get(url, params=params or {}, timeout=10)
        r.raise_for_status()
        return r.json()
    except:
        return {}

def get_trailer(movie_id):
    data = fetch(f"{BASE_URL}/movie/{movie_id}/videos", {"api_key": TMDB_API_KEY})
    for v in data.get("results", []):
        if v.get("site") == "YouTube":
            return f"https://www.youtube.com/embed/{v['key']}"
    return None

def get_movies_by_category(category):
    params = {
        "api_key": TMDB_API_KEY,
        "sort_by": "popularity.desc",
        "primary_release_date.gte": "2025-01-01",
        "primary_release_date.lte": "2026-12-31"
    }

    if category == "bollywood":
        params["with_original_language"] = "hi"
    elif category == "tollywood":
        params["with_original_language"] = "te"
    elif category == "south":
        params["with_original_language"] = "ta|te|ml|kn"
    else:
        params["with_original_language"] = "en"

    data = fetch(f"{BASE_URL}/discover/movie", params)

    movies = []

    for m in data.get("results", []):
        poster_path = m.get("poster_path")
        poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        movies.append({
            "title": m.get("title"),
            "poster": poster,
            "id": m.get("id")
        })

    return movies[:15]

@app.get("/")
def home():
    return {"status": "API is running 🚀"}

@app.get("/search")
def search(query: str, api_key: str = Depends(verify_api_key)):
    data = fetch(f"{BASE_URL}/search/movie", {
        "api_key": TMDB_API_KEY,
        "query": query
    })

    results = []

    for m in data.get("results", [])[:2]:
        poster_path = m.get("poster_path")
        poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        results.append({
            "title": m.get("title"),
            "poster": poster,
            "id": m.get("id")
        })

    return results

@app.get("/movie/{movie_id}")
def movie(movie_id: int, api_key: str = Depends(verify_api_key)):
    trailer = get_trailer(movie_id)

    movie_data = fetch(f"{BASE_URL}/movie/{movie_id}", {
        "api_key": TMDB_API_KEY
    })

    title = movie_data.get("title", "")
    recs = recommender.get_recommendations(title)

    rec_list = []

    for r in recs:
        poster_path = r.get("poster_path")
        poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

        rec_list.append({
            "title": r.get("title"),
            "poster": poster
        })

    return {
        "title": title,
        "trailer": trailer,
        "recommendations": rec_list
    }

@app.get("/category/{type}")
def category(type: str, api_key: str = Depends(verify_api_key)):
    return get_movies_by_category(type)