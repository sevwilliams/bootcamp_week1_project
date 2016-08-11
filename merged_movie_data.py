import os
import json
from pprint import pprint
from collections import Counter
%matplotlib inline
import matplotlib.pyplot as plt
import seaborn as sns
import math
import pandas as pd
import statsmodels.api as sm
import numpy as np


#Put all movie data into a list of dictionaries
def movie_data(movie_file):
    movie_info_path = os.path.join('data', movie_file)
    json_movie_list = os.listdir(movie_info_path)
    python_movie_list = []
    for json_movie in json_movie_list:
        json_path = os.path.join(movie_info_path, json_movie)
        with open(json_path, 'r') as file:
            python_movie = json.load(file)
            python_movie_list.append(python_movie)
    return python_movie_list

mojo = movie_data('boxofficemojo')
metacritic = movie_data('metacritic')

metacritic_clean = [item for item in metacritic if isinstance(item, dict)]

mojo_df = pd.DataFrame(mojo)
metacritic_df = pd.DataFrame(metacritic_clean)

merged_data = pd.merge(left=mojo_df, right=metacritic_df, how='inner', on=['title'])

def consolodate_director(col_x, col_y):
    director = []
    for i in xrange(len(col_x)):
        if col_x[i] == None:
            director.append(col_y[i])
        if col_y[i] == None:
            director.append(col_x[i])
        director.append(col_x[i])
    return pd.Series(director)

merged_data['director'] = consolodate_director(merged_data['director_x'], merged_data['director_y'])

merged_data.rename(columns={'year_x':'year'}, inplace=True)

del merged_data['year_y']
del merged_data['director_x']
del merged_data['director_y']
