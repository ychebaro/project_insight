import pandas as pd
import numpy as np
import gzip
import json
import re
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from subprocess import check_call

class CleaningBooks(object):
	""" Cleaning books from Goodreads database 
	Mengting Wan, Julian McAuley, "Item Recommendation on Monotonic Behavior Chains", in RecSys'18 """
	
	
	def get_genre(self, inputjson, outputjson):
		""" Selects books from main genres
		
		Args:
			inputjson (:obj:`str`): name of input json file

		Returns:
			:obj:`outputjson`: name of output json file
		"""

		wanted = ['classics', 'classic', 'fantasy', 'romance', 'mystery', 'science-fiction', 'sci-fi',
			 'scifi', 'business', 'economics']

		output = open(outputfile, 'w')
	
		with open(inputdata) as json_file:
			for line in json_file:
				book = json.loads(line)
				names = [elm['name'] for elm in book['popular_shelves'] if \
			bool(re.match('[^\x00-\x7F\x80-\xFF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]', elm['name'])) == False]
				if set(wanted).isdisjoint(names) == False:
					output.write('{}\n'.format(json.dumps(book)))

		output.close()

	def clean_data_language(self, inputdata, outputfile):
		""" Removes children books and non-english books from json file
		
		Args:
			inputdata (:obj:`str`): name of input json file

		Returns:
			:obj:`outputfile`: name of output json file
		"""
		
		eng_lan = ['en', 'enm', 'en-US', 'en-GB', '']
		child_books = ['child', 'children', 'children-s', 'childrens', 'kids-books', 'childrens-s-books']

		output = open(outputfile, 'w')
		with gzip.open(inputdata) as json_file:
			for line in json_file:
				book = json.loads(line)
				names = [elm['name'] for elm in book['popular_shelves']]
				if (book['language_code'] in eng_lan) and (not set(child_books).isdisjoint(names[:6]) == False):
					output.write('{}\n'.format(json.dumps(book)))
		output.close()



	def get_scifi(self, inputjson, outputjson):
		""" Selects books from sci-fi genre
		
		Args:
			inputjson (:obj:`str`): name of input json file

		Returns:
			:obj:`outputjson`: name of output json file
		"""

		wanted = [ 'science-fiction', 'sci-fi', 'scifi']

		output = open(outputjson, 'w')
	
		with gzip.open(inputjson) as json_file:
			for line in json_file:
				book = json.loads(line)
				names = [elm['name'] for elm in book['popular_shelves']]
				if set(wanted).isdisjoint(names) == False:
					output.write('{}\n'.format(json.dumps(book)))

		output.close()

	def clean_data_nasty_tags(self, dfin):
		""" Removes book tags from datafram which are irrelevant
		ex: to_read, must_read, 2018-read...
		
		Args:
			dfin (:obj:`str`): name of the dataframe
 
		Returns:
			:obj:`popnew`: list with removed irrelevant tag names
			:obj:`cnew`: list with removed count of irrelevant tag names
		"""

		popular_shelves = dfin['popular_shelves']
		count_shelves = dfin['count_shelves']
	
		popnew = []
		cnew = []

		for elm, elmc in zip(popular_shelves, count_shelves):    
			to_remove = []
			for i in range(len(elm)):
				if (len(elm[i]) == 1) or (bool(re.match('.*book*', elm[i])) == True)\
				or (bool(re.match('.*read*', elm[i])) == True) or (bool(re.match('.*favorite*', elm[i])) == True)\
				or (bool(re.match('.*need*', elm[i])) == True) or (bool(re.match('.*own*', elm[i])) == True)\
				or (bool(re.match('.*shelve*', elm[i])) == True) or (bool(re.match('.*like*', elm[i])) == True)\
				or (bool(re.match('.*shelf*', elm[i])) == True) or (bool(re.match('.*buy*', elm[i])) == True)\
				or (bool(re.match('tbr', elm[i])) == True) or (bool(re.match('.*finish*', elm[i])) == True)\
				or (bool(re.match('.*kindle*', elm[i])) == True) or (bool(re.match('.*list*', elm[i])) == True)\
				or (bool(re.match('.*year*', elm[i])) == True) or (bool(re.match('.*audio*', elm[i])) == True)\
				or (bool(re.match('.*library*', elm[i])) == True) or \
				(bool(re.match('[^\x00-\x7F\x80-\xFF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]', elm[i])) == True):
					to_remove.append(i) 
		
			popnew.append([elm[e] for e in range(len(elm)) if e not in to_remove])
			cnew.append([elmc[e] for e in range(len(elmc)) if e not in to_remove])
 
		return popnew, cnew

	def replace_tags(dfin):
		""" Replaces some needed tag names with homogeneous tags
		ex: scifi to science-fiction
		
		Args:
			dfin (:obj:`str`): name of the dataframe
 
		Returns:
			:obj:`popnew`: list with removed irrelevant tag names
			:obj:`cnew`: list with removed count of irrelevant tag names
		"""

		popular_shelves = dfin['popular_shelves']
		count_shelves = dfin['count_shelves']    
	
		popnew = []
		cnew = []

		for elm, elmc in zip(popular_shelves, count_shelves):    
			for i in range(len(elm)):
				elm[i].replace('classics', 'classic')
				elm[i].replace('scifi', 'science-fiction')
				elm[i].replace('sci-fi', 'science-fiction')
				elm[i].replace('ya', 'young-adult')

			popnew.append([elm[e] for e in range(len(elm))])
			cnew.append([elmc[e] for e in range(len(elmc))])
	
		return popnew, cnew

	def update_dataframe(self, popular_shelves, count_shelves, inputdf):
		""" Updates dataframe with new values for popular_shelves and respective counts
		
		Args:
			popular_shelves (:obj:`list`): list of popular shelves to use
			count_shelves (:obj:`list`): list of count of respective popular shelves to use
			dfin (:obj:`str`): name of the dataframe
 
		Returns:
			:obj:`dfout`: pandas DataFrame with removed irrelevant tag names and their counts
		"""

		popnew, cnew = self.clean_data_nasty_tags(inputdf)
		
		# convert lists to pandas Series
		new_column_p = pd.Series(popnew, name='popular_shelves', index=range(len(popnew)))
		new_column_c = pd.Series(cnew, name='count_shelves', index=range(len(cnew)))

		# update dataframe
		inputdf.update(new_column_p)
		inputdf.update(new_column_c)


	def get_books_data(self, inputdata):
		""" Extract needed keys from json file:
		isbn, book_id, popular_shelves, count_shelves, title, 
		num_pages, publication_year, average_rating, ratings_count
		
		Args:
			inputdata (:obj:`str`): name of the input json file
 
		Returns:
			:obj:`books`: json file of relevant entries
		"""

		books = []
		with gzip.open(inputdata) as json_file:
			for lines in json_file:
				book = {}
				line = json.loads(lines)
				names = []
				counts = []         
				names = [elm['name'] for elm in line['popular_shelves']] 
				counts = [elm['count'] for elm in line['popular_shelves']]
				book['isbn'] = line['isbn']
				book['book_id'] = line['book_id']
				book['popular_shelves'] = names
				book['count_shelves'] = counts
				book['title'] = line['title']
				book['num_pages'] = line['num_pages']
				book['publication_year'] = line['publication_year']
				book['average_rating'] = line['average_rating']
				book['ratings_count'] = line['ratings_count']
				books.append(book)
		return books

	def load_data(self, inputdata):
		""" Extract json entry from concatenated json file

		Args:
			inputdata (:obj:`str`): name of the input json file
 
		Returns:
			:obj:`books`: list of json dict type
		"""
	
		books = []
		with gzip.open(inputdata) as json_file:
			for line in json_file:
				book = json.loads(line)
				books.append(book)
		return books


def main():

	books_json = CleaningBooks().clean_data_language('goodreads_books.json.gz', 'books_en_nochild-30-09.json')

	with open('books_en_nochild-30-09.json', 'rb') as fin, gzip.open('books_en_nochild-30-09.json.gz', 'wb') as fout:
		fout.writelines(fin)

	CleaningBooks().get_scifi('books_en_nochild.json.gz', 'books_scifi.json')

if __name__ == '__main__':
	main()

