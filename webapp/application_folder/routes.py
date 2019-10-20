from flask import render_template, request, redirect
from application_folder import app
import pandas as pd
import random
import sqlite3

@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])

def scifi_input():
	return render_template("input.html")

@app.route('/output')
def scifi_output():
	user_id = request.args.get('user_id')
	nb_users = request.args.get('nb_users')
	negative = request.args.get('review_type')

	# read in our csv file    
	dbname = './application_folder/static/data/db.sqlite'
	dbsimname = './application_folder/static/data/user_user_similarity.csv'
	users_sim = pd.read_csv(dbsimname)

	conn = sqlite3.connect(dbname)
	cur = conn.cursor()
	users_db = pd.read_sql_query("select * from users", conn)

	if negative == 'Yes':
		cluster_all = cluster_all[cluster_all['Average sentiment'] != 'negative']

	print(users_db[users_db['user_id_csv'] == int(user_id)])
	# check if user_id entered is in the data
#	if len(users_db[users_db['user_id_csv'].astype(str).str.contains(user_id)]) == 0:
	if len(users_db[users_db['user_id_csv'] == int(user_id)]) == 0:
		error = 'Invalid user id'
		print('entering')
		return render_template('output-error.html', error=error)
	elif nb_users.isdigit() == False: 
		error = 'Invalid number of users'
		return render_template('output-error-nb_users.html', error=error)
	elif negative not in ['Yes', 'No']:
		error = 'Invalid review answer'
		return render_template('output-error-review.html', error=error)
	else:
		# select cluster to which the user belongs to
		result = cur.execute("select group_y from users where user_id_csv=(?)", [user_id]).fetchall()
		user_clust = result[0][0]
		cluster_all = users_db[users_db['group_y'] == user_clust]

		if int(nb_users) >= len(cluster_all):
			error = 'Invalid number of users'
			return render_template('output-error-nb_users.html', error=error)

		# get user idx for similarity matrix
		user_idx = users_db['user_idx'][users_db['user_id_csv'] == int(user_id)].item()
		# get similar users
		similar_users = users_sim[users_sim['User1'] == user_idx].sort_values(by='Similarity', ascending=False)

		# find the most similar x users according to input form
		list_wanted = [similar_users['User2'].iloc[i] for i in range(int(nb_users))]

		users = []
		print(list_wanted)
		for i in list_wanted:
			users.append(dict(name=cluster_all['names'][cluster_all['user_idx'] == i].item(), 
				reviewing_style=cluster_all['Average sentiment'][cluster_all['user_idx'] == i].item(),
				title=cluster_all['title'][cluster_all['user_idx'] == i].item(),
				user_gr_id=cluster_all['user_id_csv'][cluster_all['user_idx'] == i].item()))


	return render_template("output.html", users=users)
