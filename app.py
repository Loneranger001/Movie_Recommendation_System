from flask import Flask, render_template, request
# import pandas as pd
# import re
import logging
import os
from helperfunctions.utils import clean_title,find_similar_movies, get_movieId, read_movie_data, read_ratings_data, read_csv_from_blob

app = Flask(__name__)
logging.basicConfig(level=logging.ERROR)

# Global variables to store the data
movies = None
ratings = None

# get necessary files from the blob storage

BLOB_CONNECTION_STRING = os.getenv("BLOB_CONN_STR")
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER")
MOVIES_BLOB_NAME = "movies.csv"
RATINGS_BLOB_NAME = "ratings.csv"

if BLOB_CONNECTION_STRING is None:
    raise Exception(f"Blob connection string is not configured")

if BLOB_CONTAINER is None:
    raise Exception(f"Blob container is not configured")

movies  = read_csv_from_blob(BLOB_CONNECTION_STRING, BLOB_CONTAINER, MOVIES_BLOB_NAME)
ratings = read_csv_from_blob(BLOB_CONNECTION_STRING, BLOB_CONTAINER, RATINGS_BLOB_NAME)

if movies is None:
    raise Exception(f"Unable to read movies dataset")


if ratings is None:
    raise Exception(f"Unable to read ratings dataset")

@app.route("/v1/recommendations", methods=["GET", "POST"])
def recommend_movie():
    # Initialize movie as None when the page initially loaded
    movie_title = None
    recommended_movies = []
    # If POST request, get the movie title from the form
    if request.method == "POST":
        movie_title = request.form.get("movie_title")
        logging.info(f"movie_title from the user interface: {movie_title}")
        recommended_movies = find_similar_movies(movie_title,movies,ratings)
        logging.info(f"Recommended Movies: {recommended_movies}")
    return render_template("index.html", movies=recommended_movies)


if __name__ == "__main__":
    app.run(debug=True)
