import streamlit as st
import tmdbsimple as tmdb
import random
import time



class Query:
    def __init__(self, earliest=1980, latest=2023, vote_average=7,
    vote_count=100, total_query = 5, movie_per_query=3, genres=None ):

        self.earliest = earliest
        self.latest =  latest
        self.vote_average = vote_average
        self.vote_count = vote_count
        self.total_query = total_query
        self.movie_per_query = movie_per_query
        # all official genres in the database
        if genres:
            self.genres = genres
        else:
            raise ValueError("genres cannot be None")
        self.genres_dict = {}
        for genre in self.genres:
            self.genres_dict[genre['id']] = genre['name']
        self.discover = tmdb.Discover()

    def random_query(self):
        movies = []
        q = 0
        while q < self.movie_per_query:
            genre = str(self.genres[random.randint(0, len(self.genres)-1)]['id'])
            release_year = random.randint(self.earliest, self.latest)
            try:
                total_pages = movie_query = self.discover.movie(page=1, with_genres=genre,
                        primary_release_date_gte=f"{release_year}-01-01",
                        primary_release_date_lte=f"{release_year}-12-31",
                        vote_average_gte=self.vote_average,
                        vote_count_gte=self.vote_count)['total_pages']

                page = random.randint(1, total_pages)

                movie_query = self.discover.movie(page=page, with_genres=genre,
                        primary_release_date_gte=f"{release_year}-01-01",
                        primary_release_date_lte=f"{release_year}-12-31",
                        vote_average_gte=self.vote_average,
                        vote_count_gte=self.vote_count)['results']

                movie = movie_query[random.randint(0, len(movie_query)-1)]

                movies.append(movie)
                q += 1
            except:
                print(genre,release_year)

            time.sleep(0.01)
        return movies

@st.cache_resource
def create_query(earliest=1980, latest=2023, vote_average=7, vote_count=100,
                total_query = 5, movie_per_query = 3,genres=None):
    return Query(earliest=earliest, latest=latest, vote_average=vote_average,
                    vote_count=vote_count, total_query = total_query,
                    movie_per_query = movie_per_query, genres=genres)
