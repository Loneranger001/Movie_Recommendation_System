import pandas as pd
import re
import logging
from azure.storage.blob import BlobServiceClient
import io, tempfile

def read_csv_from_blob(connection_string, container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        download_stream = blob_client.download_blob()
        temp_file.write(download_stream.readall())
        temp_file.flush()
        # read the temp file all at once
        return pd.read_csv(temp_file.name)
    # steam_downloader = blob_client.download_blob()
    # data = steam_downloader.readall()

def read_movie_data(path):
    try:
        movies = pd.read_csv(path)
        movies["clean_title"] = movies["title"].apply(clean_title)
        return movies
    except Exception as e:
        raise Exception(f"Error reading data from {path} in read_movie_data: {e}")

def read_ratings_data(path):
    try:
        ratings = pd.DataFrame()
        # ratings = pd.read_csv(path)
        for chunk in pd.read_csv(path,chunksize=2000000):
            ratings = pd.concat([ratings,chunk], axis=0) 
        return ratings    
    except Exception as e:
        raise Exception(f"Error reading ratings data from {path} in read_ratings_data: {e}")

def clean_title(title):
    try:
        return re.sub("[^A-Za-z0-9 ]","",title)
    except Exception as e:
        logging.error(f"Unexpected Error occured in clean_title: {e}")
        raise Exception(f"Error cleaning titles in clean_title: {e}")

def read_movie_data(path):
    try:
        movies = pd.read_csv(path)
        movies["clean_title"] = movies["title"].apply(clean_title)
        return movies
    except Exception as e:
        raise Exception(f"Error reading data from {path} in read_movie_data: {e}")

def read_ratings_data(path):
    try:
        ratings = pd.DataFrame()
        # ratings = pd.read_csv(path)
        for chunk in pd.read_csv(path,chunksize=2000000):
            ratings = pd.concat([ratings,chunk], axis=0) 
        return ratings    
    except Exception as e:
        raise Exception(f"Error reading ratings data from {path} in read_ratings_data: {e}")

def get_movieId(title,movies,ratings):
    try:
        movieId = None
        logging.info(f"inside get_movieId, title passed {title}")
        logging.info(f"Number of rows in movies: {len(movies)}")
        movieId = movies[movies["title"].str.contains(title, case=False)]["movieId"]
        if movieId.empty:
            return None
        else:
            movieId = movieId.iloc[0]
            logging.info(f"movieId: {movieId}")
            if movieId in ratings["movieId"].values:
                return movieId
            else:
                return None
    except Exception as e:
        logging.error(f"Unexpected error in get_movieId: {e}")
        raise

def find_similar_movies(movie_title,movies,ratings):
    try:
        # get the movie id
        movie_id = get_movieId(movie_title,movies,ratings)
        logging.info(f"movie_id from get_movieId function: {movie_id}")

        # get the recommended movies
        if movie_id is not None:
            similar_users = ratings[(ratings["movieId"]==movie_id) & (ratings["rating"] > 4)]["userId"].unique()
            similar_user_recs = ratings[(ratings["userId"].isin(similar_users)) & (ratings["rating"] > 4)]["movieId"]
            similar_user_recs=similar_user_recs.value_counts() / len(similar_users)
            # movies which are liked by greater than 10% of the people
            similar_user_recs= similar_user_recs[similar_user_recs > .1]
            all_users = ratings[ratings["movieId"].isin(similar_user_recs.index) & (ratings["rating"] > 4)]
            # proportion of all users who have liked the a movie
            all_users_recs = all_users["movieId"].value_counts()/len(all_users["userId"].unique())
            
            recs_percentages = pd.concat([similar_user_recs,all_users_recs],axis=1)
            recs_percentages.columns = ["similar","all"]
            recs_percentages["score"] = recs_percentages["similar"]/recs_percentages["all"]
            recs_percentages=recs_percentages.sort_values(by=["score"],ascending=False)
            movies_merged = pd.merge(movies,recs_percentages,left_on="movieId",right_index=True)[["movieId","title","score"]]
            logging.info(f"Number of rows returned from find_similar_moves : {len(movies_merged)}")
            return movies_merged.sort_values(by=["score"],ascending=False)["title"].head(10).tolist()
        else:
            return []
    except Exception as e:
        raise Exception(f"Error in function find_similar_movies: {e}")