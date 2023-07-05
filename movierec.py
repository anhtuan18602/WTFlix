import tmdbsimple as tmdb
import streamlit as st
from datetime import datetime
from recommend import recommend
from query import create_query

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJkOGRlYWRmZGVhMjBhYTY5MmVmZDkyNzcwZmJjMzVmMSIsInN1YiI6IjY0OTE2MTc3MmY4ZDA5MDEwMGFiZjA1ZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.3O37eW5IAoEDnXIPnH5y6LGOLFfrP_u92AkxOCNRfsA"
}

tmdb.API_KEY = "d8deadfdea20aa692efd92770fbc35f1"
tmdb.REQUESTS_TIMEOUT = 5

#
vote_count = 200
vote_average = 7
total_query = 5
movie_per_query = 3
genres = tmdb.Genres().movie_list()['genres']
status = st.empty()
columns = st.columns(movie_per_query)


def make_sliders():
    values = st.slider(
        'Range of release year:',
        1920, 2023, (1980, 2023), key="slider")
    return values


def make_checkboxes(value=True):
    columns[0].write("Genres:")
    checkboxes_list = {}
    i=0
    for genre in genres:
        columns[i%movie_per_query].checkbox(genre["name"],value=value,
                                    key=genre["name"], on_change=check_genres_number)
        i+=1
    if st.session_state.all_box_checked:
        columns[i%movie_per_query].checkbox("Uncheck all",value=False,
                            on_change=change_check_status,key="uncheck")
    else:
        columns[i%movie_per_query].checkbox("Check all",value=False,
                            on_change=change_check_status,key="uncheck")
    return


def make_buttons():
    skip_button = status.button('skip',key="skip")
    button_list = []
    i = 0

    for column in columns:
        column.button(f"choose {i+1}",key=f"button{i}",on_click=check_counter)
        i+=1


def make_image(movies):
    for t in range(len(movies)):
        movie = movies[t]
        columns[t%movie_per_query].image(f"https://image.tmdb.org/t/p/w500{movie['poster_path']}",caption=movie["title"])


def query_from_ids(ids):
    ret = []
    for id in ids:
        ret.append(tmdb.Movies(id).info())
    return ret

def submit_and_begin():

    st.session_state.setdefault("counter", 0)
    st.session_state.setdefault("earliest", st.session_state.slider[0])
    st.session_state.setdefault("latest", st.session_state.slider[1])
    genres_chosen = []
    for genre in genres:
        if st.session_state[genre["name"]]:
            genres_chosen.append(genre)
    if len(genres_chosen)==0:
        raise ValueError("No genres chosen")

    st.session_state.setdefault("genres", genres_chosen)


def change_check_status():
    st.session_state.all_box_checked = not st.session_state.all_box_checked



def check_genres_number():
    i=0
    for genre in genres:
        if st.session_state[genre["name"]]:
            i+=1
    if i != 0:
        st.session_state.uncheck = False
    else:
        st.write("You should choose at least 1 genres for recommendation!")
        st.session_state.all_box_checked = False
    if i == len(genres):
        st.session_state.all_box_checked = True

def check_counter():
    chosen_list = st.session_state.chosen
    last_query = st.session_state.last
    for j in range(movie_per_query):
        if st.session_state[f"button{j}"]:
            chosen_list.append(last_query[j])
    st.session_state.chosen = chosen_list
    st.session_state.counter += 1
    if st.session_state.counter == total_query:
        st.session_state.finished = True

def main():
    st.session_state.setdefault("all_box_checked", True)
    if "counter" not in st.session_state:
        make_sliders()
        make_checkboxes(st.session_state.all_box_checked)
        st.button("Start", on_click=submit_and_begin)
    else:
        start()




def start():

    counter = st.session_state.counter
    query = create_query(earliest=st.session_state.earliest,
                        latest=st.session_state.latest,
                        genres=st.session_state.genres)
    chosen_list = st.session_state.setdefault("chosen", [])
    st.session_state.setdefault("last", [])
    finished = st.session_state.setdefault("finished", False)

    if not finished:
        status.write("Pick movies that you like!")

    if finished:
        if(len(chosen_list)==0):
            raise ValueError("No movies chosen")
        status.write("Here's the result:")
        result = recommend(chosen_list,
                earliest_release=st.session_state.earliest,
                latest_release=st.session_state.latest,
                vote_average=vote_average,vote_count=vote_count,
                genres=st.session_state.genres)
        recommended = query_from_ids(result)
        make_image(recommended)

    else:
        make_buttons()



        if counter < total_query:

            movies = query.random_query()
            make_image(movies)
            st.session_state["last"] = movies

    st.write([movie['title'] for movie in chosen_list])
    st.stop()

if __name__ == "__main__":
    main()
