""" Cleaning book entries from GoodReads
and extracting relevant books with the most populated tag

:Author: Yassmine Chebaro <yassmnine.chebaro@mssm.edu>
:Date: 2019-09-16
:License: MIT
"""

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
	Mengting Wan, Julian McAuley, "Item Recommendation on Monotonic Behavior Chains", in RecSys'18 
	"""
	
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

	def clean_data_bad_tags(self, dfin):
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

		for elm_str, elmc_str in zip(popular_shelves, count_shelves):    
			to_remove = []
			elmlist=eval('['+elm_str+']')
			elmclist=eval('['+elmc_str+']')
			elm = [i for all in elmlist for i in all]
			elmc = [i for all in elmclist for i in all]

			for i in range(len(elm)):
				if (len(elm[i]) == 1) or (bool(re.match('.*book*', elm[i])) == True)\
				or (bool(re.match('.*read*', elm[i])) == True) or (bool(re.match('.*favorite*', elm[i])) == True)\
				or (bool(re.match('.*need*', elm[i])) == True) or (bool(re.match('.*own*', elm[i])) == True)\
				or (bool(re.match('.*shelve*', elm[i])) == True) or (bool(re.match('.*like*', elm[i])) == True)\
				or (bool(re.match('.*shelf*', elm[i])) == True) or (bool(re.match('.*buy*', elm[i])) == True)\
				or (bool(re.match('tbr', elm[i])) == True) or (bool(re.match('.*finish*', elm[i])) == True)\
				or (bool(re.match('.*kindle*', elm[i])) == True) or (bool(re.match('.*list*', elm[i])) == True)\
				or (bool(re.match('.*year*', elm[i])) == True) or (bool(re.match('.*audio*', elm[i])) == True)\
				or (bool(re.match('.*library*', elm[i])) == True):
					to_remove.append(i) 
		
			popnew.append([elm[e] for e in range(len(elm)) if e not in to_remove])
			cnew.append([elmc[e] for e in range(len(elmc)) if e not in to_remove])

		return popnew, cnew


	def replace_tags(self, dfin):
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
				elm[i]= elm[i].replace('classics', 'classic')
				elm[i]= elm[i].replace('scifi', 'science-fiction')
				elm[i]= elm[i].replace('sci-fi', 'science-fiction')
				elm[i] = elm[i].replace('ya', 'young-adult')

			popnew.append([elm[e] for e in range(len(elm))])
			cnew.append([elmc[e] for e in range(len(elmc))])
	
		return popnew, cnew

	def merge_similar_tags(self, dfin):
		""" Merge similar tags, needed after replacing ya with young-adult for example
		
		Args:
			dfin (:obj:`str`): name of the dataframe
 
		Returns:
			:obj:`popnew`: list with merged tag names
			:obj:`cnew`: list with removed count of merged tag names
		"""

		popular_shelves = dfin['popular_shelves']
		count_shelves = dfin['count_shelves']    
	
		popnew = []
		cnew = []
		sum_tags = []

		for elm, elmc in zip(popular_shelves, count_shelves):  
			to_remove = []
			elmc_int = np.array([int(i) for i in elmc])
			rep = [item for item, count in Counter(elm).items() if count > 1]
			if rep:
				to_remove = [elm.index(tag) for tag in rep]
				for r in rep:
					rep_idx = [i for i,d in enumerate(elm) if d==r]
					sum_rep = (np.sum(elmc_int[rep_idx]))
					elmc_int[rep_idx[1]] = sum_rep
			
			popnew.append([elm[e] for e in range(len(elm)) if e not in to_remove])
			cnew.append([elmc_int[e] for e in range(len(elmc_int)) if e not in to_remove])
			sum_tags.append(sum([elmc_int[e] for e in range(len(elmc_int)) if e not in to_remove]))
		
		return popnew, cnew, sum_tags


	def remove_sf_tags(self, dfin):
		""" Remove science-fiction tags to extract other subgenre tags
		
		Args:
			dfin (:obj:`str`): name of the dataframe
 
		Returns:
			:obj:`popnew`: list with removed science-fiction tag names
			:obj:`cnew`: list with removed count of science-fiction tag names
		"""

		popular_shelves = dfin['popular_shelves']
		count_shelves = dfin['count_shelves']
	
		popnew = []
		cnew = []

		for elm, elmc in zip(popular_shelves, count_shelves):    
			to_remove = []
			for i in range(len(elm)):
				if (bool(re.match('.*science-fiction*', elm[i])) == True):
					to_remove.append(i) 
			popnew.append([elm[e] for e in range(len(elm)) if e not in to_remove])
			cnew.append([elmc[e] for e in range(len(elmc)) if e not in to_remove])
 
		return popnew, cnew

	def get_first_tags(self, dfin, cutoff):
		""" Keep only first n tags, using cutoff as value
		
		Args:
			dfin (:obj:`str`): name of the dataframe
			cutoff (:obj:`int`): cutoff for the number of first tags to keep
 
		Returns:
			:obj:`popnew`: list with most populated tag names using cutoff for the number of tags
			:obj:`cnew`: list with most populated tag names using cutoff for the number of tags
		"""
		popular_shelves = dfin['popular_shelves']
		count_shelves = dfin['count_shelves']    
		
		popnew = []
		cnew = []

		for elm, elmc in zip(popular_shelves, count_shelves):    
			listp = [elm[e] for e in range(len(elm))][0:int(cutoff)]
			listc = [elmc[e] for e in range(len(elmc))][0:int(cutoff)]
			if len(listp) == 0:
				popnew.append('none')
				cnew.append(0)
			else:
				popnew.append(listp[0])
				cnew.append(listc[0])

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
		
		# convert lists to pandas Series
		new_column_p = pd.Series(popular_shelves, name='popular_shelves', index=range(len(popular_shelves)))
		new_column_c = pd.Series(count_shelves, name='count_shelves', index=range(len(count_shelves)))

		# update dataframe
		dfin.update(new_column_p)
		dfin.update(new_column_c)



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
		with open(inputdata) as json_file:
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

	# Read in json file of book entries and output
	books_json = CleaningBooks().clean_data_language('goodreads_books.json.gz', 'books_en_nochild.json')

	# Gzip the json file for space
	with open('books_en_nochild-30-09.json', 'rb') as fin, gzip.open('books_en_nochild.json.gz', 'wb') as fout:
	 	fout.writelines(fin)

	# Extracting scifi books from the database and putting them in a pandas DataFrame
	CleaningBooks().get_scifi('books_en_nochild.json.gz', 'books_scifi.json')
	scifi_books = CleaningBooks().get_books_data('books_scifi.json')
	df_scifi_books = pd.DataFrame(scifi_books)
	df_scifi_books.to_csv('books_scifi.csv', index=False)

	# Removing irrelevant tags from scifi books
	popnew, cnew = CleaningBooks().clean_data_bad_tags(dfin)
	new_column_p = pd.Series(popnew, name='popular_shelves', index=range(len(popnew)))
	new_column_c = pd.Series(cnew, name='count_shelves', index=range(len(cnew)))
	dfin.update(new_column_p)
	dfin.update(new_column_c)

	# Replace repetitive tag names
	popnew, cnew = CleaningBooks().replace_tags(dfin)
	new_column_p = pd.Series(popnew, name='popular_shelves', index=range(len(popnew)))
	new_column_c = pd.Series(cnew, name='count_shelves', index=range(len(cnew)))
	dfin.update(new_column_p)
	dfin.update(new_column_c)
	
	# Remove science-fiction tags to get subgenre tags
	popnew, cnew =CleaningBooks().remove_sf_tags(dfin)
	new_column_p = pd.Series(popnew, name='popular_shelves', index=range(len(popnew)))
	new_column_c = pd.Series(cnew, name='count_shelves', index=range(len(cnew)))
	dfin.update(new_column_p)
	dfin.update(new_column_c)

	# Merge similar tags
	popnew, cnew, sum_tags = CleaningBooks().merge_similar_tags(dfin)
	new_column_p = pd.Series(popnew, name='popular_shelves', index=range(len(popnew)))
	new_column_c = pd.Series(cnew, name='count_shelves', index=range(len(cnew)))
	dfin.update(new_column_p)
	dfin.update(new_column_c)

	# Get first populated tags, here I chose 1
	popnew, cnew = CleaningBooks().get_first_tags(dfin, 1)
	new_column_p = pd.Series(popnew, name='popular_shelves', index=range(len(popnew)))
	new_column_c = pd.Series(cnew, name='count_shelves', index=range(len(cnew)))
	dfin.update(new_column_p)
	dfin.update(new_column_c)

	dfin.to_csv('book_year_1tag.csv', index=False)


if __name__ == '__main__':
	main()

