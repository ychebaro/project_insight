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

	with open(inputdata) as json_file:
		for line in json_file:
			book = json.loads(line)
			names = [elm['name'] for elm in book['popular_shelves']]
			if (book['language_code'] in eng_lan) and (not set(child_books).isdisjoint(names[:6]) == False):
				output.write('{}\n'.format(json.dumps(book)))

	output.close()

def load_data_table(inputdata):
	book_titles = []
	book_isbns = []
	book_popshelves_names = []
	book_popshelves_count = []
	count = 0 
	books = []

	with open(inputdata) as json_file:
		for line in json_file:
			book = json.loads(line)
			count += 1
			book_titles.append(book['title'])
			book_isbns.append(book['isbn'])
			book_popshelves_names.append([elm['name'] for elm in book['popular_shelves']])
			book_popshelves_count.append([elm['count'] for elm in book['popular_shelves']])

	return count, book_titles, book_isbns, book_popshelves_names, book_popshelves_count


def main():

	# books_out = split_data(sys.argv[1], 600000)
	# save_data(books_out, '600Kbooks.json')

	# books_in = load_data('goodreads_books.json.gz')

	# english_books = clean_data_language(books_in)
	# clean_data_language('10Kbooks.json', '10K-english-nochild.json')
	count, book_titles, book_isbns, book_popshelves_names, book_popshelves_count = load_data_table('all-english-nochild.json')

	print(len(book_titles), len(book_isbns), len(book_popshelves_names), len(book_popshelves_count))

	# print(count)
	# with open('analyse_tags-all.dat', 'w') as fileout:
		# for i in range(count):
			# fileout.write('{} {} {} {} {}\n'.format(i, book_titles[i], book_isbns[i], book_popshelves_names[i], book_popshelves_count[i]))

	# with open('analyse_tags-all-count.dat', 'w') as fileout:
	# 	for i in range(count):
	# 		fileout.write('{} {}\n'.format(i, book_popshelves_count[i]))


	# with open('analyse_tags-all-names.dat', 'w') as fileout:
	# 	for i in range(count):
	# 		fileout.write('{} {}\n'.format(i, book_popshelves_names[i]))

	flat_names = [item for sublist in book_popshelves_names for item in sublist]
	flat_count = [item for sublist in book_popshelves_count for item in sublist]

	with open('tags-count-2col-all-no1.dat', 'w') as fileout:
		for i,j in zip(flat_names, flat_count):
			if j > 1:
				fileout.write('{} {}\n'.format(i,j))

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


