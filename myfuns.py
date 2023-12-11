import pandas as pd
import numpy as np
import requests

# Define the URL for movie data
ratings_data_url = "https://liangfgithub.github.io/MovieData/movies.dat?raw=true"

# Fetch the data from the URL
response = requests.get(ratings_data_url)

# Split the data into lines and then split each line using "::"
movie_lines = response.text.split("\n")
movie_data = [line.split("::") for line in movie_lines if line]

# Create a DataFrame from the movie data
movies = pd.DataFrame(movie_data, columns=["movie_id", "title", "genres"])
movies["movie_id"] = movies["movie_id"].astype(int)

genres = list(
    sorted(
        set([genre for genres in movies.genres.unique() for genre in genres.split("|")])
    )
)

S_reduced = pd.read_pickle("S_reduced.gz")
bayesian_substitutes = pd.read_pickle("bayesian_substitutes.pkl")
genre_recommendations = pd.read_pickle("genre_recommendations.pkl")


def myIBCF(newuser):
    newuser = newuser.to_numpy()
    rating_indices = np.argwhere(~np.isnan(newuser))
    output = S_reduced.iloc[:, 0] * np.NaN

    for i in range(S_reduced.shape[0]):
        movie = S_reduced.iloc[i]
        neighbors = np.argwhere(~np.isnan(movie).to_numpy())
        neighbors_vals = np.intersect1d(rating_indices, neighbors)

        if not len(neighbors_vals):
            continue

        output[i] = np.sum(movie[neighbors_vals] * newuser[neighbors_vals]) / np.sum(
            movie[neighbors_vals]
        )

    output = output[np.isnan(newuser) & (np.abs(output - 0.1) > 0.0001)]
    output = list(output.sort_values(ascending=False).index)

    # Add Bayesian results if not enough results
    while len(output) < 10:
        for movie in bayesian_substitutes.index:
            if movie not in output:
                output.append(movie)

    return output[:10]


def get_displayed_movies(n=50):
    return [
        (movie_id, movie_title)
        for movie_id, movie_title in movies[["movie_id", "title"]].values
    ][:n]


def get_popular_movies(genre: str):
    temp = pd.concat(
        [
            genre_recommendations[genre],
            genre_recommendations[genre].apply(
                lambda x: movies[movies["movie_id"] == x]["title"].values[0]
            ),
        ],
        axis=1,
    )

    return list(temp.itertuples(name=None, index=False))


def get_recommended_movies(new_user_ratings):
    preferences_vector = S_reduced.iloc[:, 0] * np.NaN
    for movie_id, score in new_user_ratings.items():
        preferences_vector["m" + str(movie_id)] = score

    recommendations = myIBCF(preferences_vector)
    output = []
    for movie_id in recommendations:
        movie_id = int(str(movie_id[1:]))
        output.append((movie_id, movies[movies.movie_id == movie_id].title.values[0]))
    return output
