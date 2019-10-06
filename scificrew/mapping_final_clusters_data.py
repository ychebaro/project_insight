""" Getting final clusters data

:Author: Yassmine Chebaro <yassmnine.chebaro@mssm.edu>
:Date: 2019-09-30
:License: MIT
"""

# Import Libraries
import pandas as pd
import numpy as np
import random
from collections import Counter



def main():
	# clusters group user id
	clusters_users = pd.read_csv('clusters_final.csv')

	# clusters group user id
	clusters_users_names = pd.read_csv('clusters_group_names.csv')

	# user average sentiment
	users_sentiment = pd.read_csv('users_ave_sentiment.csv')

	# user favorite book
	users_favbook = pd.read_csv('user_book_fav.csv')

	# map user idx with user id to extract from this df
	ratings_books = pd.read_csv('ratings_books_u80_b10.csv')

	# map user id with user goodreads id
	user_id_map = pd.read_csv('user_id_map.csv')

	# Mapping user idx for clustering to user id from csv
	user_idx_id = ratings_books.drop(ratings_books.columns[[1, 2, 3, 4, 5, 6, 8]], axis=1)
	user_id_list = list(set(user_idx_id['user_id']))
	user_idx_list = list(set(user_idx_id['user_idx']))
	user_idx_id = user_idx_id.drop_duplicates()
	user_idx_id.columns = ['user_id_csv', 'user_idx']

	# map user id with user id gr
	user_dict = user_id_map.set_index('user_id_csv').T.to_dict('list')
	user_idx_id['user_id_gr'] = user_idx_id['user_id_csv'].map(user_dict)
	user_idx_id['user_id_gr'] = user_idx_id['user_id_gr'].str.get(0)

	# map user sentiment with user id gr
	user_dict = user_id_map.set_index('user_id').T.to_dict('list')
	users_sentiment.columns = ['user_id_gr', 'Average sentiment']

	# merging DataFrames of user idx and sentiment
	test = pd.merge(user_idx_id, users_sentiment, on='user_id_gr')

	# merging with clustering DataFrame
	test2 = pd.merge(test, clusters_users, on='user_idx')

	# merging with users favorite books
	users_favbook.columns = ['user_id_csv', 'book_id', 'title']
	test3 = pd.merge(test2, users_favbook, on='user_id_csv')

	# merging with users names
	final = pd.merge(test3, clusters_users_names, on='user_idx')
	final.to_csv('clusters.csv', index=False)


if __name__ == '__main__':
	main()















