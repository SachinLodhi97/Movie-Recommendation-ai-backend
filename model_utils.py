import pandas as pd
import joblib

class MovieRecommender:
    def __init__(self):
        try:
            self.movies = pd.read_csv("Recommendation.csv")
            self.kmeans = joblib.load("models/movie_model.pkl")
            self.tfidf = joblib.load("models/tfidf_vectorizer.pkl")
            self.svd = joblib.load("models/svd_model.pkl")
            print("✅ Models loaded!")
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            self.movies = None

    def get_recommendations(self, movie_title, n=100):
        if self.movies is None:
            return []

        try:
            tfidf_vec = self.tfidf.transform([movie_title])
            reduced_vec = self.svd.transform(tfidf_vec)

            cluster_id = self.kmeans.predict(reduced_vec)[0]
            cluster_movies = self.movies[self.movies['cluster'] == cluster_id]

            n = min(n, len(cluster_movies))

            recs = cluster_movies.sample(n=n)[['title', 'poster_path']].to_dict(orient='records')

            return recs  
        except Exception as e:
            print(f"❌ Recommendation error: {e}")
            return []
        


recommender = MovieRecommender()