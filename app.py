import streamlit as st
import pickle
import pandas as pd
import requests

API_KEY = "4bed74c963eaca54ac3ad8239ce98e5f"  # keep safe in real projects

def fetch_poster(movie_id):
    """Return full poster URL or placeholder if missing / API error."""
    try:
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except Exception as e:
        # you can log e if you want
        pass
    # fallback placeholder (blank image or local file)
    return "https://via.placeholder.com/500x750?text=No+Poster"

def recommend(movie):
    # find movie index
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], []

    distances = similarity[movie_index]
    # enumerate distances and sort by similarity score descending, skip the same movie
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for idx, score in movies_list:
        # get the movie_id from your dataframe (ensure the column name is correct)
        movie_id = movies.iloc[idx].movie_id
        recommended_movies.append(movies.iloc[idx].title)

        # fetch poster using the movie_id
        poster_url = fetch_poster(movie_id)
        recommended_movies_posters.append(poster_url)

    return recommended_movies, recommended_movies_posters

# --- load data ---
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations',
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)   # <-- MUST be inside button block

    for i, col in enumerate(cols):
        if i < len(names):
            with col:
                st.image(posters[i], use_column_width=True)
                st.markdown(
                    f"<p style='text-align:center; white-space:normal; font-size:16px; font-weight:600;'>{names[i]}</p>",
                    unsafe_allow_html=True
                )
        else:
            with col:
                st.write("")


# to run: streamlit run app.py
