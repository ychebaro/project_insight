""" Getting user books ratings for 
users with minreviews (80)
books with minratings (10)

:Author: Yassmine Chebaro <yassmnine.chebaro@mssm.edu>
:Date: 2019-09-26
:License: MIT
"""

# Import Libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import itertools


def get_users_books(books_sci, bookmap, ratings):
	""" Extracts books and users with a minimal number of books reviewed and a minimal
	number of reviews per user
	
	Args:
		dfscifi (:obj:`DataFrame`): pandas DataFrame of scifi books
		bookmap (:obj:`DataFrame`): pandas DataFrame of users and ratings per book
		dfusers (:obj:`DataFrame`): pandas DataFrame of users interactions
	Returns:
		:obj:`df`: pandas DataFrame corresponding to the criteria
	"""

	# Replacing book_id from csv with goodread book_id_gr
	book_dict = bookmap.set_index('book_id_csv').T.to_dict('list')
	ratings['book_id_gr'] = ratings['book_id'].map(book_dict)
	ratings['book_id_gr'] = ratings['book_id_gr'].str.get(0)
	ratings_clean = ratings.drop(['book_id' ] , axis='columns')

	# Extracting ratings for read and read/reviewed books
	ratings_read = ratings_clean[ratings_clean['is_read'] == 1]
	ratings_rr = ratings_read[ratings_read['is_reviewed'] == 1]

	# Extracting books in read&reviewed in the scifi category
	booksf_list = list(set(books_sci['book_id']))
	df_ratings = ratings_rr[ratings_rr['book_id_gr'].isin(booksf_list)]

	# Getting user count 
	sum_read_user = df_ratings.groupby('user_id')['is_read'].count()
	df_read_user = pd.DataFrame({'user_id':sum_read_user.index, 'number_read':sum_read_user.values})
	
	df_ratings['user_counts'] = df_ratings.groupby(['user_id'])['book_id_gr'].transform('count')
	df_ratings['book_counts'] = df_ratings.groupby(['book_id_gr'])['user_id'].transform('count')

	# Apply user + book cuts and add a user index for matrix building later
	df2 = df_ratings[(df_ratings['user_counts'] > 80) & (df_ratings['book_counts'] > 10)]
	df2['user_idx'] = pd.Categorical(df2['user_id']).codes 
	df2['book_idx'] = pd.Categorical(df2['book_id_gr']).codes 

	# Set number of books and users variables for later use
	n_ubooks_y = len(df2.book_id_gr.unique()) 
	n_uusers_y = len(df2.user_id.unique())

	return df2

def main():
	# Reading in user_ratings, book id mapping from csv to goodreads id and scifi books
	ratings = pd.read_csv('goodreads_interactions.csv')
	bookmap = pd.read_csv('book_id_map.csv')
	books_sci = pd.read_csv('books-scifi.csv')

	df2 = get_users_books(books_sci, bookmap, ratings)

	df2.to_csv('ratings_books_u80_b10-v3.csv', index=False)


if __name__ == '__main__':
	main()

