import streamlit as st
import pickle
import requests
import os

# Load data
movie_df = pickle.load(open("movie_df.pkl", "rb"))
movie_similarity_df = pickle.load(open("movie_similarity_df.pkl", "rb"))
restricted_movies = pickle.load(open("restricted_movies.pkl", "rb"))

# Fetch poster from TMDB
def fetch_movie_poster(movie_id):
    api_key = "291596fc4042cc91839854d0a821c41f"
    base_url = "https://api.themoviedb.org/3/movie/"
    poster_base_url = "https://image.tmdb.org/t/p/w500"

    url = f"{base_url}{movie_id}?api_key={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"{poster_base_url}{poster_path}"
    return "https://via.placeholder.com/300x450?text=No+Poster"

# Recommendation logic
def recommend(movie_name, rating):
    if movie_name not in movie_similarity_df.columns:
        raise ValueError("Movie not found in the dataset.")

    similar_score = movie_similarity_df[movie_name] * (rating - 2.5)
    similar_score = similar_score.sort_values(ascending=False)
    similar_score = list(similar_score.index)

    restricted_titles = list(restricted_movies["title"])
    movieList = []
    posterList = []
    count = 1

    for i in similar_score:
        if i in restricted_titles and count < 7:
            mid = restricted_movies.loc[restricted_movies["title"] == i].movie_id.values[0]
            movieList.append(i)
            posterList.append(fetch_movie_poster(mid))
            count += 1

    return movieList[1:6], posterList[1:6]

# Streamlit UI
st.set_page_config(page_title="Movie Recommender", layout="centered")
st.title("🎬 Movie Recommender System")
st.markdown("Recommend movies based on your favorite movie and how much you liked it.")

movie_names = movie_df['title'].values
selected_movie = st.selectbox("Select a movie you like:", movie_names)
rating = st.slider("Rate this movie (0 to 5):", 0.0, 5.0, 3.0, 0.5)

if st.button("Recommend"):
    try:
        with st.spinner("Fetching recommendations..."):
            names, posters = recommend(selected_movie, rating)
            st.success("Recommendations:")

            cols = st.columns(len(names))
            for i in range(len(names)):
                with cols[i]:
                    st.image(posters[i], use_column_width=True)
                    st.caption(names[i])
    except ValueError as ve:
        st.error(str(ve))
    except Exception as e:
        st.error(f"Something went wrong: {e}")
