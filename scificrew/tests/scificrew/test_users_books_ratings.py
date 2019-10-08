""" Getting user books ratings for 
users with minreviews (80)
books with minratings (10)
	Unit testing

:Author: Yassmine Chebaro <yassmnine.chebaro@mssm.edu>
:Date: 2019-09-26
:License: MIT
"""

# Import Libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import itertools
import unittest
import os
from users_books_ratings import get_users_books

## Important note: testing is not clean here
## Need to use more explicitly function in the code
## To be modified in the future

class UsersBooksRatingsTestCase(unittest.TestCase):

	def test_methods(self):

		books_sci = pd.read_csv(os.path.join('tests', 'fixtures', 'books_scifi_test.csv'))
		ratings = pd.read_csv(os.path.join('tests', 'fixtures', 'goodreads_interactions_test.csv'))
		bookmap = pd.read_csv(os.path.join('tests', 'fixtures', 'book_id_map.csv'))
		users_ratings = pd.read_csv(os.path.join('tests', 'fixtures', 'ratings_books_u80-b10_test.csv'))

		# first get user 1272 from ratings
		user = ratings['user_id'][ratings['user_id'] == 1272].item()

		# get the book id csv from ratings
		book_csv = ratings['book_id'][ratings['user_id'] == 1272].item()

		# get the goodreads id for this book
		book_id_gr = bookmap['book_id'][bookmap['book_id_csv'] == 35166].item()

		# check if all ids are good
		self.assertEqual(user, 1272)
		self.assertEqual(book_csv, 35166)
		self.assertEqual(book_id_gr, 44688)
