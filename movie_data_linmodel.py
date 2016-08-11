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
import datetime as dt


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

def review_breakdown(review_col, index):
    lst = []
    for group in review_col:
        lst.append(group[index])
    return pd.Series(lst)

def season_by_month(month):
    if month in (12,1,2):
      return 'winter'
    elif month in (3,4,5):
      return 'spring'
    elif month in (6,7,8):
      return 'summer'
    elif month in (9,10,11):
      return 'fall'

def group_ratings(rating):
    if rating not in ('R','PG','PG-13','Not Rated'):
        return 'other'
    else:
        return rating

merged_data['director'] = consolodate_director(merged_data['director_x'], merged_data['director_y'])
merged_data['rating_categories'] = merged_data['rating'].apply(group_ratings)
merged_data['pos_user_reviews'] = review_breakdown(merged_data['num_user_reviews'], 0)
merged_data['nut_user_reviews'] = review_breakdown(merged_data['num_user_reviews'], 1)
merged_data['neg_user_reviews'] = review_breakdown(merged_data['num_user_reviews'], 2)
merged_data['tot_user_reviews'] = review_breakdown(merged_data['num_user_reviews'], 3)
merged_data['pos_critic_reviews'] = review_breakdown(merged_data['num_critic_reviews'], 0)
merged_data['nut_critic_reviews'] = review_breakdown(merged_data['num_critic_reviews'], 1)
merged_data['neg_critic_reviews'] = review_breakdown(merged_data['num_critic_reviews'], 2)
merged_data['tot_critic_reviews'] = review_breakdown(merged_data['num_critic_reviews'], 3)

merged_data.rename(columns={'year_x':'year'}, inplace=True)

del merged_data['year_y']
del merged_data['director_x']
del merged_data['director_y']

merged_data_dropna = merged_data[['production_budget','opening_weekend_take','domestic_gross',
                                  'release_date_wide','widest_release','worldwide_gross','year', 'runtime_minutes',
                                  'metascore','user_score','pos_user_reviews','nut_user_reviews','neg_user_reviews',
                                  'tot_user_reviews','pos_critic_reviews','nut_critic_reviews','neg_critic_reviews',
                                  'tot_critic_reviews','rating','rating_categories']].dropna()

merged_data_dropna['release_month'] = merged_data_dropna['release_date_wide'].apply(lambda x: x[5:7]).astype(int)
merged_data_dropna['season'] = merged_data_dropna['release_month'].apply(season_by_month)

#merged_data_dropna.join(pd.get_dummies(merged_data_dropna['rating']))

X = sm.add_constant(merged_data_dropna[['production_budget','runtime_minutes']].join(
                                            pd.get_dummies(merged_data_dropna['season']).join(
                                            pd.get_dummies(merged_data_dropna['rating_categories']))))
Y = merged_data_dropna['opening_weekend_take']

linmodel = sm.OLS(Y,X).fit()

linmodel.summary()
