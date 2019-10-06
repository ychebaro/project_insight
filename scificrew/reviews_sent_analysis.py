""" Getting user sentiment

:Author: Yassmine Chebaro <yassmnine.chebaro@mssm.edu>
:Date: 2019-09-29
:License: MIT
"""

# Import Libraries
import pandas as pd
import numpy as np
import gzip
import json
import itertools
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter, defaultdict



def get_reviews_data(inputdata, list_users):
	""" Extracts reviews info from json file: book_id, user_id, rating and review text
	
	Args:
		inputdata (:obj:`json`): json file of reviews per user
		list_users (:obj:`list`): list of users from rating matrix
	Returns:
		:obj:`reviews`: dict of reviews
	"""
	reviews = []
	with gzip.open(inputdata) as json_file:
		for lines in json_file:
			review = {}
			line = json.loads(lines)
			if line['user_id'] in list_users:
				review['book_id'] = line['book_id']
				review['user_id'] = line['user_id']
				review['rating'] = line['rating']
				review['review_text'] = line['review_text']
				reviews.append(review)
	return reviews


def sentiment_scores(dfin, analyser):
	""" Calculate sentiment score per user 
	
	Args:
		dfin (:obj:`DataFrame`): pandas DataFrame of user book review
		analyser (:obj:`SentimentIntensityAnalyzer`): instance of SentimentIntensityAnalyzer
	Returns:
		:obj:`user_sentiment`: dict of user and sentiment compound score
	"""	
	user_sentiment = defaultdict(list)
	for i in range(dfin.shape[0]):
		sentiment_dict = analyser.polarity_scores(dfin.iloc[i][4])
		user_sentiment[dfin.iloc[i][5]].append(sentiment_dict['compound'])
	
	return user_sentiment

def get_average_sentiment(inputdict):
	""" Calculate average sentiment score per user 
	
	Args:
		inputdict (:obj:`dict`): dict of user and sentiment compound score
	Returns:
		:obj:`outputdict`: dict of user and average sentiment compound score
	"""	
	outputdict = {}
	for k,v in inputdict.items():
		outputdict[k] = np.mean(v)
	
	return outputdict

def get_nature_avsent(inputdict):
	""" Calculate nature of average sentiment score per user 
	
	Args:
		inputdict (:obj:`dict`): dict of user and average sentiment compound score
	Returns:
		:obj:`outputdict`: dict of user and nature of average sentiment compound score
	"""	
	outputdict = {}
	for k, v in inputdict.items():
		if v >= 0.05:
			outputdict[k] = 'positive'
		elif v <= -0.05:
			outputdict[k] = 'negative'
		else:
			outputdict[k] = 'neutral'
			
	return outputdict


def main():

	# Read in clustering results from csv to get user ids
	user_clustid = pd.read_csv('user_clustid_k25.csv')

	# Ratings books matrix to get book ids
	ratings_books = pd.read_csv('ratings_books_u80_b10.csv')

	# Mapping between user is from csv to goodreads id (23 characters alphanumerical code)
	usermap = pd.read_csv('user_id_map.csv')

	# Sci Fi books dataframe
	bookssf = pd.read_csv('books-authors.csv')

	# Map user id from csv to goodreads id
	user_dict = usermap.set_index('user_id_csv').T.to_dict('list')
	ratings_books['user_id_gr'] = ratings_books['user_id'].map(user_dict)
	ratings_books['user_id_gr'] = ratings_books['user_id_gr'].str.get(0)

	# Clean up the DataFrame
	idx_idgr = ratings_books.drop(ratings_books.columns[[1, 2, 3, 5, 6]], axis=1)
	list_user_gr = list(set(idx_idgr['user_id_gr']))

	# Get reviews per user
	reviews = get_reviews_data('goodreads_reviews_dedup.json.gz', list_user_gr)

	# Reviews to DataFrame
	dfreviews = pd.DataFrame(reviews)

	# Extract books matching user-book matrix
	list_book_gr = list(set(idx_idgr['book_id_gr']))
	user_book = bookssf[bookssf['book_id'].isin(list_book_gr)]

	# Convert book id to string for further manipulation
	user_book['book_id'] = user_book['book_id'].astype(str)

	# Merge into user/book/reviews DataFrame
	u_b_r = pd.merge(user_book, dfreviews, on='book_id')
	ubr_filtered = u_b_r.drop(u_b_r.columns[[3, 4, 5, 6, 7, 8, 10]], axis=1)

	# Sentiment analysis, get average and nature of average
	analyser = SentimentIntensityAnalyzer()
	user_sentiment = sentiment_scores(ubr_filtered, analyser)

	user_sentiment_av = get_average_sentiment(user_sentiment)

	user_sent_nature = get_nature_avsent(user_sentiment_av)

	user_sent = pd.DataFrame(zip(list(user_sent_nature.keys()), 
		list(user_sent_nature.values())), columns=['User', 'Average sentiment'])

	user_sent.to_csv('users_ave_sentiment.csv', index=False)

if __name__ == '__main__':
	main()