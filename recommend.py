import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from connect import connect
from scipy import sparse
from multiprocessing import Pool
import re


#list of features to be queried
feature_types = ["keywords_features", "people_features", "genre_ids_features", "title_features"]
columns = feature_types + ["id"]
#features_weight = [1.0, 2.0, 0.5]
#weight_dict = dict(zip(features,features_weight))
#features = ['id',"combined_features"]

def combined_features(row,feature_type=None):
    if feature_type == "title":
        return re.sub(r'\W+', ' ', row[feature_type])
    return " ".join(row[feature_type])


def query(earliest=1950,latest=2023,vote_average=6,vote_count=0,genres=None):
    #Establish a connection
    conn = connect()

    # Create a cursor to execute SQL queries
    cur = conn.cursor()

    column_names = (", ".join(columns))
    # SQL query to fetch specific columns from a table
    genre_ids = [genre['id'] for genre in genres]
    query = (
    f"SELECT DISTINCT {column_names} "
    "FROM movies m "
    "JOIN genres g ON m.id = g.movie_id "
    f"WHERE date(m.primary_release_date) >= '{earliest}-01-01' "
    f"AND date(m.primary_release_date) <= '{latest}-12-31' "
    f"AND m.vote_average >= {vote_average} "
    f"AND m.vote_count >= {vote_count} "
    f"AND g.genre IN ({','.join('?' for _ in genre_ids)})"
    "GROUP BY m.id"
    )

    cur.execute(query,genre_ids)
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=columns)
    print(len(df))
    cur.close()
    conn.close()
    #print(df)
    return df


def format_data(df):
    print(df[feature_type])
    #Fill all empty cells with ''
    for feature_type in feature_types:
        df[feature_type] = df[feature_type].fillna('')

    #Combine all the features into columns
    for feature_type in feature_types:
        df[feature_type] = df.apply(combined_features, feature_type=feature_type, axis =1)
    df.to_csv("data_final.csv",index=False,encoding='utf-8')
    print("file saved")


def extract_features(df, feature_type):
    cv = CountVectorizer()

    count_matrix = cv.fit_transform(df[feature_type])
    print("Count Matrix:", cv.get_feature_names_out())


    #Inverse Frequency: Assign higher weights to elements that occur less frequently.
    #IF = 1 / frequency
    features = cv.get_feature_names_out()
    weights = np.ones(len(features))

    if feature_type != "people":
        feature_occurrences = np.array(count_matrix.sum(axis=0)).flatten()
        weights = [1 / occurrences for occurrences in feature_occurrences]
    return count_matrix.multiply(weights).tocsr()


def calculate_cosine_similarity(args):
    movie_index, count_matrix = args
    return cosine_similarity(count_matrix[movie_index], count_matrix)[0]


def get_largest_indexes(lst, n):
    arr = np.array(lst)
    indexes = np.argpartition(arr, -n)[-n:]
    sorted_indexes = indexes[np.argsort(arr[indexes])][::-1]
    return sorted_indexes.tolist()


def recommend(movies,earliest_release=1950,latest_release=2023,vote_average=6,vote_count=0, genres=None):
    #Get data
    df = query(earliest=earliest_release, latest=latest_release, vote_average=vote_average, vote_count=vote_count, genres=genres)

    #Add combined_features column
    #format_data(df)

    #Create the count matrix
    matrices = {}
    for feature_type in feature_types:
        matrices[feature_type] = extract_features(df, feature_type)




    num_movies = len(df)
    indices = df[df['id'].isin([movie['id'] for movie in movies])].index.tolist()

    features_similarity = {}
    features_similarity_sum = {}

    for feature_type in feature_types:
        features_similarity[feature_type] = cosine_similarity(matrices[feature_type][indices], matrices[feature_type])
        features_similarity_sum[feature_type] = np.sum(features_similarity[feature_type], axis=0)

    similarity_sum = np.sum(list(features_similarity_sum.values()), axis=0)
    #print(sorted(similarity_sum,reverse=True)[0:10])
    largest_indices = get_largest_indexes(similarity_sum,50)


    i=0
    result = []
    chosen_ids = [x['id'] for x in movies]

    for index in largest_indices:
        id = df[df.index == index]["id"].values[0]
        if id not in chosen_ids:
            i=i+1
            result.append(id)
        if i>=15:
            break
    return result
