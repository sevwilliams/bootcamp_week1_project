
# coding: utf-8

# In[7]:

import os
import json
from pprint import pprint
from collections import Counter
get_ipython().magic(u'matplotlib inline')
import matplotlib.pyplot as plt
import seaborn as sns
import math
import pandas as pd
import statsmodels.api as sm
import numpy as np
import datetime as dt


#Put all movie data into a list of dictionaries
def movie_data(movie_file):
    movie_info_path = os.path.join('../data', movie_file)
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


# In[28]:

import holidays
from collections import Counter
import datetime


# In[20]:

def gen_holiday(end_yr):
    us_hol = []
    for yr in range(1900,end_yr):
        for date in sorted(holidays.US(years=yr).items()):
            us_hol.append(date[0])
    return us_hol


# In[21]:

us_holidays = gen_holiday(2015)


# In[77]:

def make_date(dt_str):
    if dt_str == None:
        dt_conv = datetime.date(2014,1,3)
    else:
        dt_conv = datetime.date(int(dt_str[0:4]),int(dt_str[5:7]),int(dt_str[8:10]))
    return dt_conv


# In[110]:

def hol_weekend(release_date):
    if make_date(release_date) in us_holidays:
        return 1
    elif make_date(release_date) + datetime.timedelta(days=1) in us_holidays:
        return 1
    elif make_date(release_date) + datetime.timedelta(days=2) in us_holidays:
        return 1
    elif make_date(release_date) + datetime.timedelta(days=3) in us_holidays:
        return 1
    elif make_date(release_date) + datetime.timedelta(days=4) in us_holidays:
        return 1
    elif make_date(release_date) + datetime.timedelta(days=5) in us_holidays:
        return 1
    else:
        return 0


# In[117]:

# M == 0
def day_of_week(release_date):
    dt_conv = make_date(release_date)
    return dt_conv.weekday()        


# In[114]:

merged_data['holiday_weekend'] = merged_data['release_date_wide'].apply(hol_weekend)


# In[118]:

merged_data['day_of_week'] = merged_data['release_date_wide'].apply(day_of_week)


# In[119]:

merged_data.loc[lambda df: df.holiday_weekend == True, :].head()


# In[121]:

merged_data_dropna = merged_data[['production_budget','opening_weekend_take','domestic_gross',
                                  'release_date_wide','widest_release','worldwide_gross','year', 'runtime_minutes',
                                  'metascore','user_score','pos_user_reviews','nut_user_reviews','neg_user_reviews',
                                  'tot_user_reviews','pos_critic_reviews','nut_critic_reviews','neg_critic_reviews',
                                  'tot_critic_reviews','rating','rating_categories','holiday_weekend','day_of_week']].dropna()
merged_data_dropna['release_month'] = merged_data_dropna['release_date_wide'].apply(lambda x: x[5:7]).astype(int)
merged_data_dropna['season'] = merged_data_dropna['release_month'].apply(season_by_month)


# In[237]:

merged_data_dropna['widest_release_sq'] = merged_data_dropna['widest_release'].apply(lambda X:np.log(X))
merged_data_dropna['holiday_weekend_sq'] = merged_data_dropna['holiday_weekend'].apply(lambda X:X**3)


# In[238]:

msk = np.random.rand(len(merged_data_dropna)) < 0.8
train = merged_data_dropna[msk]
test = merged_data_dropna[~msk]


# In[239]:

X = sm.add_constant(train[['production_budget','runtime_minutes','holiday_weekend','day_of_week',
                                            'widest_release_sq','holiday_weekend_sq','widest_release','metascore']].join(
                                            pd.get_dummies(train['season']).join(
                                            pd.get_dummies(train['rating_categories']))))
Y = train['opening_weekend_take']

linmodel = sm.OLS(Y,X).fit()

linmodel.summary()


# In[240]:

train_pred = pd.DataFrame(linmodel.predict(X),index=train.index)
final = pd.concat([train_pred,Y,X],axis=1)
final


# In[241]:

X = sm.add_constant(test[['production_budget','runtime_minutes','holiday_weekend',
                           'widest_release_sq','holiday_weekend_sq','day_of_week','widest_release','metascore']].join(
                                            pd.get_dummies(test['season']).join(
                                            pd.get_dummies(test['rating_categories']))))
Y = test['opening_weekend_take']


# In[242]:

test_pred = pd.DataFrame(linmodel.predict(X),index=test.index)


# In[243]:

final = pd.concat([test_pred,Y,X],axis=1)


# In[244]:

final['diff'] = final[0] - final['opening_weekend_take']


# In[245]:

final


# In[ ]:



