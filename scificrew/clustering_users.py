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
from collections import Counter




class ClusteringUsersStep1(object):
	""" K-means clustering of users using book ratings 
		This is the first step of the clustering

	"""

	def clustering_users_ratings(self, df_ratings):
		""" Cluster users books ratings matrix
		After evaluation of the optimal number of k for this sparse matrix, the k chosen at this 
		stage is 25
	
		Args:
			df_ratings (:obj:`DataFrame`): pandas DataFrame of user books ratings
		Returns:
			:obj:`user_clustid`: pandas DataFrame with clustered used in 'group' column
		"""
		user_book_ratings = pd.pivot_table(df_ratings, index='user_idx', columns='book_idx', values='rating')

		# Conversion to sparse csr matrix
		sparse_ratings = csr_matrix(pd.SparseDataFrame(user_book_ratings).to_coo())
		# 25 clusters
		predictions = KMeans(n_clusters=25).fit_predict(sparse_ratings)

		clustered = pd.concat([user_book_ratings.reset_index(), pd.DataFrame({'group':predictions})], axis=1)

		user_clustid = clustered.drop(clustered.columns[1:10269], axis=1)

		return user_clustid


	def draw_movies_heatmap(user_book_ratings, axis_labels=True):
		
		fig = plt.figure(figsize=(15,4))
		ax = plt.gca()
	
		# Draw heatmap
		heatmap = ax.imshow(user_book_ratings,  interpolation='nearest', vmin=0, vmax=5, aspect='auto')
		if axis_labels:
			ax.set_yticks(np.arange(user_book_ratings.shape[0]) , minor=False)
			ax.set_xticks(np.arange(user_book_ratings.shape[1]) , minor=False)
			ax.invert_yaxis()
			ax.xaxis.tick_top()
			ax.set_yticklabels(user_book_ratings.index, minor=False)

		ax.set_ylabel('User idx')
		# Separate heatmap from color bar
		divider = make_axes_locatable(ax)
		cax = divider.append_axes("right", size="5%", pad=0.05)
		# Color bar
		cbar = fig.colorbar(heatmap, ticks=[5, 4, 3, 2, 1, 0], cax=cax)
		plt.show()
	

class ClusteringUsersStep2(object):
	""" K-means clustering of users using book publication year and most populated tag
		This is the second step of the clustering for more specifity

	"""

	def get_publication_year(self, user_clusters, book_year, ratings_books):
		""" Getting book publication and including it in the matrix (since initially I 
		did not consider the year, these entries are missing...)
	
		Args:
			users_clusters (:obj:`DataFrame`): pandas DataFrame of users clusters from Step1
			book_year (:obj:`DataFrame`): pandas DataFrame of books year and most populated tags
			ratings_books (:obj:`DataFrame`): pandas DataFrame of 

		Returns:
			:obj:`user_all`: pandas DataFrame with user_idx, group (cluster) number, publication year
			and most popular shelf appended to book ratings/users DataFrame
		"""
		listbooks_ratings = list(set(ratings_books['book_id_gr']))
		listbooks_ratings_idx = list(set(ratings_books['book_idx']))
		listbooks_year = list(set(book_year['book_id']))

		book_year.rename(columns={'book_id':'book_id_gr', 'publication_year':'pub_year'}, inplace=True)
		book_year.drop(book_year.columns[[2, 3, 4, 7, 8]], axis=1, inplace=True)

		# Get books publication year from books_sci-fi, matching book_id from rated and reviewed data
		ratings_book_year = ratings_books[ratings_books['book_id_gr'].isin(listbooks_year)]
		ratings_book_year = pd.merge(ratings_books, book_year, on='book_id_gr')
		user_all = pd.merge(user_clusters, ratings_book_year, on='user_idx')
		user_all.dropna(inplace=True)

		return user_all

	def get_cluster_group(self, dfin, clustid):
		""" Getting cluster group matrix with publication years and tag
	
		Args:
			dfin (:obj:`DataFrame`): pandas DataFrame with user group, publication year and popular shelve 
			appended to book ratings/user DataFrame
			clustid (:obj:`int`): number of the cluster from Step 1

		Returns:
			:obj:`tag_year`: pandas DataFrame pivotted with tag and shelve for desired cluster
		"""
		df_clust = dfin[dfin['group'] == clustid]
		df_clust_filtered = df_clust.drop(df_clust.columns[[1, 2, 3, 4, 5, 6, 7, 8, 10]], axis=1)  
		
		count_user_year = df_clust_filtered.groupby(['user_idx', 'pub_year']).size().reset_index(name ='year_count')
		user_year_pivot = pd.pivot_table(count_user_year, index='user_idx', columns= 'pub_year', values='year_count')
	
		count_user_tag = df_clust_filtered.groupby(['user_idx', 'popular_shelves']).size().reset_index(name ='tag_count')
		listtags = Counter(count_user_tag['popular_shelves'])
		listtags_freq = [k for k,v in listtags.items() if v>=10]
		df_u_tags = count_user_tag[count_user_tag['popular_shelves'].isin(listtags_freq)]
		user_tag_pivot = pd.pivot_table(df_u_tags, index='user_idx', columns= 'popular_shelves', values='tag_count')

		tag_year = pd.merge(user_year_pivot, user_tag_pivot, on='user_idx')
		tag_year.fillna(0, inplace=True)

		return tag_year

	def compute_clusters(self, tag_year, k):
		""" Compute clusters of users matrix with publication years and tag
	
		Args:
			tag_year (:obj:`DataFrame`): pandas DataFrame pivotted with tag and shelve for desired cluster from Step 1 
			k (:obj:`int`): number of k clusters for k-means

		Returns:
			:obj:`clustered`: pandas DataFrame of user_idx and resulting cluster number
		"""			

		predictions = KMeans(n_clusters= k).fit_predict(tag_year)
		clustered = pd.concat([tag_year.reset_index(), pd.DataFrame({'group':predictions})], axis=1)

		return clustered

class GetAllClusters(object):
	""" In this step clusters from Step 1 which are preserved and not used in Step 2 because of their
	appropriate size are combined with clusters from Step 2.
	The group numbers are reassigned so as to maintain a consecutive and non-redundant count

	"""

	def remap_clusters_step1(self, user_clusters):
		""" Remap cluster group number from Step 1
	
		Args:
			users_clusters (:obj:`DataFrame`): pandas DataFrame of users clusters from Step1

		Returns:
			:obj:`clust1`: pandas DataFrame of user_idx and group number from cluster 1
			:obj:`clust2`: pandas DataFrame of user_idx and group number from cluster 2
			:obj:`clust3`: pandas DataFrame of user_idx and group number from cluster 3
			:obj:`clust4`: pandas DataFrame of user_idx and group number from cluster 4
		"""			

		clust1 = user_clusters[user_clusters['group'] == 2]
		clust1['group'] = clust1['group'].map({2: 1})
		clust2 = user_clusters[user_clusters['group'] == 10]
		clust2['group'] = clust2['group'].map({10: 2})
		clust3 = user_clusters[user_clusters['group'] == 13]
		clust3['group'] = clust3['group'].map({13: 3})
		clust4 = user_clusters[user_clusters['group'] == 20]
		clust4['group'] = clust4['group'].map({20: 4})

		return clust1, clust2, clust3, clust4

	def get_clusters_prop(self, dfcluster, start):
		""" Extract clusters from Step 2
	
		Args:
			dfcluster (:obj:`DataFrame`): pandas DataFrame of cluster from Step 2

		Returns:
			:obj:`dfclean`: pandas DataFrame of user_idx and group number for subcluster
		"""			
		# copy just in case :)
		dfclean = dfcluster.copy()
	
		# count the number of groups
		count = len(dfclean.groupby('group').count())
	
		# renumber group id according to start 
		for i in range(count):
			dfclean['new_group'] = dfclean['group']+start

		dfclean['new_group'] = dfclean['new_group'].astype(int)
		
		# do some cleaning
		dfclean.drop('group', axis=1, inplace=True)
		dfclean.rename(columns={'user_idx': 'user_idx', 'new_group': 'group'}, inplace=True)
		
		return dfclean

	def get_merged_clusters(self, clust1, clust2, clust3, clust4, clustered_gp4, clustered_gp11,
		clustered_gp12, clustered_gp14):
		""" Merge all clusters and subclusters
	
		Args:
			clust1 (:obj:`DataFrame`): pandas DataFrame of user_idx and group number from cluster 1
			clust2 (:obj:`DataFrame`): pandas DataFrame of user_idx and group number from cluster 2
			clust3 (:obj:`DataFrame`): pandas DataFrame of user_idx and group number from cluster 3
			clust4 (:obj:`DataFrame`): pandas DataFrame of user_idx and group number from cluster 4

		Returns:
			:obj:`final_sup10`: pandas DataFrame of user_idx and group number for all
		"""			
		clust5 = self.get_clusters_prop(clustered_gp4.loc[:, ['user_idx','group']], 5)
		clust6 = self.get_clusters_prop(clustered_gp11.loc[:, ['user_idx','group']], 17)
		clust7 = self.get_clusters_prop(clustered_gp12.loc[:, ['user_idx','group']], 19)
		clust8 = self.get_clusters_prop(clustered_gp14.loc[:, ['user_idx','group']], 26)

		final_clusters = pd.concat([clust1, clust2, clust3, clust4, clust5, clust6, 
			clust7, clust8], ignore_index=True)

		count_user_clust_final = final_clusters.groupby(['group']).size().reset_index(name ='gp_count')
		sup10 = count_user_clust_final[count_user_clust_final['gp_count'] >= 10]
		listsup10 = sup10['group'].to_list()
		final_sup10 = final_clusters[final_clusters['group'].isin(listsup10)]

		return final_sup10


def main():

	book_year = pd.read_csv('book_year_1tag-5-10.csv')
	ratings_books = pd.read_csv('ratings_books_u80_b10.csv')

	users_clusters = ClusteringUsersStep1().clustering_users_ratings(ratings_books)

	#user_clusters = pd.read_csv('user_clustid_k25.csv')

	user_all = ClusteringUsersStep2().get_publication_year(user_clusters, book_year, ratings_books)

	#user_all.to_csv("testusersall.csv",index=False)
	tag_year_gp4 = ClusteringUsersStep2().get_cluster_group(user_all, 4)
	tag_year_gp11 = ClusteringUsersStep2().get_cluster_group(user_all, 11)
	tag_year_gp12 = ClusteringUsersStep2().get_cluster_group(user_all, 12)
	tag_year_gp14 = ClusteringUsersStep2().get_cluster_group(user_all, 14)

	clustered_gp4 = ClusteringUsersStep2().compute_clusters(tag_year_gp4, 12)
	clustered_gp11 = ClusteringUsersStep2().compute_clusters(tag_year_gp11, 2)
	clustered_gp12 = ClusteringUsersStep2().compute_clusters(tag_year_gp12, 7)
	clustered_gp14 = ClusteringUsersStep2().compute_clusters(tag_year_gp14, 12)


	clust1, clust2, clust3, clust4 = GetAllClusters().remap_clusters_step1(user_clusters)
	final = GetAllClusters().get_merged_clusters(clust1, clust2, clust3, clust4, clustered_gp4, clustered_gp11,
		clustered_gp12, clustered_gp14)

	final.to_csv('users-clustered-final.csv', index=False)


if __name__ == '__main__':
	main()