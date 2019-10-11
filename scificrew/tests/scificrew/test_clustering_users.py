""" Clustering users with k-means algorithm

:Author: Yassmine Chebaro <yassmnine.chebaro@mssm.edu>
:Date: 2019-09-25
:License: MIT
"""

# Import Libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error
import itertools
import os
from collections import Counter
import unittest
from clustering_users import ClusteringUsersStep1, ClusteringUsersStep2, GetAllClusters



class CleaningBooksTestCase(unittest.TestCase):

	def test_methods(self):

		book_year = pd.read_csv(os.path.join('tests', 'fixtures', 'book_year_1tag_test.csv'))
		ratings_books = pd.read_csv(os.path.join('tests', 'fixtures', 'ratings_books_u80-b10_test.csv'))

		df_ratings = pd.pivot_table(ratings_books, index='user_idx', columns='book_idx', values='rating')

		spm = csr_matrix(pd.SparseDataFrame(df_ratings).to_coo())

		spm.todense()
		spm_test = spm[df_ratings.index.get_loc(1), :].toarray()

		self.assertEqual(spm_test[df_ratings.index.get_loc(1)].item(df_ratings.columns.get_loc(597)), 5)



