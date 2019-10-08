""" Cleaning book entries from GoodReads
and extracting relevant books with the most populated tag
    Unit Testing 

:Author: Yassmine Chebaro <yassmnine.chebaro@mssm.edu>
:Date: 2019-09-20
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
import unittest
from cleaning_books import CleaningBooks


class CleaningBooksTestCase(unittest.TestCase):

	def test_methods(self):

		df_scifi = pd.read_csv(os.path.join('tests', 'fixtures', 'books_scifi_test.csv'))

		# need to add tests for all these parts
		popnew, cnew = CleaningBooks().clean_data_bad_tags(df_scifi)
		new_column_p = pd.Series(popnew, name='popular_shelves', index=range(len(popnew)))
		new_column_c = pd.Series(cnew, name='count_shelves', index=range(len(cnew)))
		df_scifi.update(new_column_p)
		df_scifi.update(new_column_c)

		popnew, cnew = CleaningBooks().replace_tags(df_scifi)
		new_column_p = pd.Series(popnew, name='popular_shelves', index=range(len(popnew)))
		new_column_c = pd.Series(cnew, name='count_shelves', index=range(len(cnew)))
		df_scifi.update(new_column_p)
		df_scifi.update(new_column_c)
	
		popnew, cnew =CleaningBooks().remove_sf_tags(df_scifi)
		new_column_p = pd.Series(popnew, name='popular_shelves', index=range(len(popnew)))
		new_column_c = pd.Series(cnew, name='count_shelves', index=range(len(cnew)))
		df_scifi.update(new_column_p)
		df_scifi.update(new_column_c)

		popnew, cnew, sum_tags = CleaningBooks().merge_similar_tags(df_scifi)
		new_column_p = pd.Series(popnew, name='popular_shelves', index=range(len(popnew)))
		new_column_c = pd.Series(cnew, name='count_shelves', index=range(len(cnew)))
		df_scifi.update(new_column_p)
		df_scifi.update(new_column_c)

		# for now just testing the final result
		popclean, cclean = CleaningBooks().get_first_tags(df_scifi, 1)

		self.assertEqual(popclean, ['horror', 'young-adult', 'dystopia', 'historical-fiction', 'historical-fiction', 'fantasy'])
		self.assertEqual(cclean, [1526, 160, 13, 22, 977, 4315])

