import csv
import json
import requests
import os

# Using the raw URL for the IMDb Top 1000 dataset
DATASET_URL = "https://raw.githubusercontent.com/krishna-koly/IMDB_TOP_1000/main/imdb_top_1000.csv"
OUTPUT_FILE = "movies_extended.json"

# Prioritizing rarer genres to balance the emotion categories
EMOTION_PRIORITY = [
    ("fear",     ["Horror"]),
    ("surprise", ["Sci-Fi", "Mystery", "Fantasy"]),
    ("disgust",  ["Crime", "Film-Noir"]),
    ("angry",    ["Action", "Western", "War"]),
    ("happy",    ["Comedy", "Animation", "Family", "Musical"]),
    ("sad",      ["Drama", "Romance"]),
    ("fear",     ["Thriller"]), # Thriller as a fallback for Fear
]

def clean_poster_url(url):
    """Upgrade IMDb poster quality by stripping resizing suffixes."""
    if not url: return url
    # Case 1: URL contains ._V1_... (IMDb's resizing marker)
    if "._V1_" in url:
        return url.split("._V1_")[0] + "._V1_.jpg"
    # Case 2: URL contains @ symbol (Alternate IMDb resizing marker)
    if "@" in url:
        return url.split("@")[0] + "@.jpg"
    return url

def download_csv(url, target_path):
    print(f"Downloading dataset from {url}...")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        with open(target_path, 'wb') as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error downloading: {e}")
        return False

def map_movie_to_emotion(genres_str):
    genres = [g.strip() for g in genres_str.split(",")]
    
    for emotion, mapping_genres in EMOTION_PRIORITY:
        if any(g in mapping_genres for g in genres):
            return emotion
            
    return "neutral"

def process_csv(csv_path):
    movies_by_emotion = {
        "happy": [], "sad": [], "angry": [], "fear": [], 
        "surprise": [], "disgust": [], "neutral": []
    }

    try:
        with open(csv_path, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                title = row.get("Series_Title")
                genre = row.get("Genre")
                year = row.get("Released_Year")
                rating = float(row.get("IMDB_Rating", 0))
                overview = row.get("Overview")
                poster = clean_poster_url(row.get("Poster_Link"))

                if not title or not genre:
                    continue

                emotion = map_movie_to_emotion(genre)
                
                movie_obj = {
                    "title": title,
                    "genre": genre,
                    "year": year,
                    "rating": rating,
                    "description": overview,
                    "poster": poster
                }
                
                movies_by_emotion[emotion].append(movie_obj)
                count += 1
            
            return movies_by_emotion
    except Exception as e:
        print(f"Error processing CSV: {e}")
        return None

def main():
    temp_csv = "temp_imdb.csv"
    if download_csv(DATASET_URL, temp_csv):
        data = process_csv(temp_csv)
        if data:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"Successfully updated {OUTPUT_FILE} with 1000 movies.")
            for emo, movieList in data.items():
                print(f" - {emo.capitalize()}: {len(movieList)}")
        
        if os.path.exists(temp_csv):
            os.remove(temp_csv)

if __name__ == "__main__":
    main()
