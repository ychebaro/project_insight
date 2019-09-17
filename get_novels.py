import gzip
import json
import re
import os
import sys
import numpy as np
import pandas as pd
from django.http import JsonResponse


# get popular_shelves, book names and isbn from json file
def get_attributes(inputdata):
	popular_shelves = []
	isbn = []
	book_titles = []
	for p in inputdata:
		popular_shelves.append(p['popular_shelves'])
		isbn.append(p['isbn'])
		book_titles.append(p['title'])

	return popular_shelves, isbn, book_titles

# find novels genre in popular_shelves:
def get_novels(inputdata):
	count = 0
	novels = []	
	name_shelves = []

	for elm in inputdata:
		names = [e['name'] for e in elm]
		name_shelves.append(names[:6])

	for i in range(len(name_shelves)):
		if 'novel' in name_shelves[i]:
			count += 1
			novels.append(i)
	return count, novels, name_shelves

def get_count_genre(inputdata):
	count = 0
	child_books = ['child', 'children', 'children-s', 'childrens', 'kids-books', 'childrens-s-books']
	ids_child_books = []

	for i in range(len(inputdata)):
		if not set(child_books).isdisjoint(inputdata[i]) == False:
			count += 1
			print(inputdata[i])
			# ids_child_books.append(i)

	return count, ids_child_books

def split_data(inputdata, maxentries):
	books = []
	count = 0
	with gzip.open(inputdata) as json_file:
		for line in json_file:
			if count <= maxentries:
				book = json.loads(line)
				count += 1
				books.append(book)
	return books

def load_data(inputdata):
	books = []
	count = 0
	with open(inputdata) as json_file:
		for line in json_file:
			book = json.loads(line)
			count += 1
			books.append(book)
	return books

def save_data(inputdata, outputfile):
	with open(outputfile,'a') as sample:
		for dict in inputdata:
			sample.write('{}\n'.format(json.dumps(dict)))
	
def clean_data_language(inputdata, outputfile):
	eng_lan = ['en', 'enm', 'en-US', 'en-GB', '']
	child_books = ['child', 'children', 'children-s', 'childrens', 'kids-books', 'childrens-s-books']

	output = open(outputfile, 'a')

	with gzip.open(inputdata) as json_file:
		for line in json_file:
			book = json.loads(line)
			names = [elm['name'] for elm in book['popular_shelves']]
			if (book['language_code'] in eng_lan) and (not set(child_books).isdisjoint(names[:6]) == False):
				output.write('{}\n'.format(json.dumps(book)))

	output.close()

	# with open(inputdata) as json_file:
		# for line in json_file:
			# book = json.loads(line)
			# names = [elm['name'] for elm in book['popular_shelves']]
			# if (book['language_code'] in eng_lan):
			 # and (not set(child_books).isdisjoint(names) == False):
				# output.write('{}\n').format(json.dumps(book))

	# with open(outputfile, 'a') as output:
		# for p in inputdata:
			# if p['language_code'] in eng_lan:
				# output.write('{}\n'.format(json.dumps(p)))
		# if p['isbn'] != '':
			# english.append([p['language_code'], p['isbn'], p['title']])

	# return english


def main():

	# books_out = split_data(sys.argv[1], 600000)
	# save_data(books_out, '600Kbooks.json')

	# books_in = load_data('goodreads_books.json.gz')

	# english_books = clean_data_language(books_in)
	clean_data_language('goodreads_books.json.gz', 'all-english-nochild.json')

	# for elm in english_books:
		# print(elm)

	# print(len(english_books))
	# popular_shelves, isbn, book_titles = get_attributes(books_in)
	# count, novels, name_shelves = get_novels(popular_shelves)
	# print('Number of books: {}'.format(len(isbn)))
	# print('Number of novels: {}'.format(count))

	# save_data(popular_shelves, 'testpop.dat')

	# with open('names6_shelves.dat','w') as output:
		# for pop in name_shelves:
			# output.write(str(pop)+'\n')
	# print(len(name_shelves))
	# count, ids_child_books = get_count_genre(name_shelves)
	# print('Number of children books: {}'.format(count_children))

if __name__ == '__main__':
	main()


