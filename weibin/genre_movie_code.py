def in_list(alist, i):
    if isinstance(alist, list):
        return i in alist
    return False
 
def add_dummy(df, var_name):
    dummy = [in_list(i, var_name)*1 for i in df['genre']]
    df[var_name] = dummy
       
df_test=critics_df[:].copy()
pprint(df_test['genre'])
add_dummy(df_test, 'Drama')
add_dummy(df_test, 'Comedy')
add_dummy(df_test, 'Thriller')
add_dummy(df_test, 'Action')
add_dummy(df_test, 'Romance')
pprint(df_test)
