import base64
import pickle
import pandas as pd
import requests
import streamlit as st


# Function to fetch poster for a given movie ID
def fetch_poster(movie_id):
    try:
        response = requests.get(
            'https://api.themoviedb.org/3/movie/{}?api_key=b1041507cc5370a36fa6ac21b683b753&language=en-US'.format(
                movie_id))
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        else:
            return None
    except requests.exceptions.RequestException as e:
        st.error("Error fetching poster: {}".format(e))
        return None


# Function to recommend movies similar to the selected movie
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index
    if len(movie_index) == 0:
        st.warning("Movie not found in the dataset.")
        return [], []  # Return empty lists if movie not found
    movie_index = movie_index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]
    recommended_movies = []
    recommended_movies_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)
        if poster_url:
            recommended_movies_posters.append(poster_url)
            recommended_movies.append(movies.iloc[i[0]].title)

    # If fewer than 5 recommendations are available, display a warning
    if len(recommended_movies) < 10:
        st.warning("Only {} recommendations available.".format(len(recommended_movies)))

    return recommended_movies, recommended_movies_posters


# Load movie data and similarity scores
movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movies = pd.DataFrame(movie_dict)

# Streamlit application setup

# Define the CSS for the background image
background_image = 'image.jpg'

# Read the image file and encode it in base64
with open(background_image, "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

# Generate the background style with full-screen coverage and higher z-index
background_style = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{image_data}");
        background-size: 100% 100%;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1; /* Ensure the background stays behind other content */
    }}
    .stButton, .stTextInput {{
        z-index: 1; /* Ensure other elements are above the background */
    }}
    </style>
"""

# Set the page layout with the background image
st.markdown(background_style, unsafe_allow_html=True)
st.title("Movie Recommendation system")

selected_movie_name = st.selectbox('Select a movie', movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    num_recommendations = len(names)

    # Calculate the number of rows needed based on the number of recommendations
    num_rows = (num_recommendations + 4) // 5  # Round up to the nearest multiple of 5

    for row in range(num_rows):
        cols = st.columns(5)  # Create 5 columns for each row
        start_index = row * 5
        end_index = min((row + 1) * 5, num_recommendations)

        for i in range(start_index, end_index):
            with cols[i % 5]:  # Alternate between the five columns
                st.text(names[i])
                if posters[i]:
                    st.image(posters[i])
                else:
                    st.warning("Poster not found")
