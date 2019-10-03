from flask import render_template, request, redirect
from application_folder import app
import pandas as pd
import random


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])

def scifi_input():
    return render_template("input.html")

@app.route('/output')
def scifi_output():
    user_id = request.args.get('user_id')
    nb_users = request.args.get('nb_users')

	# read in our csv file    
    dbname = './application_folder/static/data/clusters.csv'
    users_db = pd.read_csv(dbname)

    # select cluster to which the user belongs to
    user_clust = users_db['group_y'][users_db['user_id_csv'] == int(user_id)].item()
    cluster_all = users_db[users_db['group_y'] == user_clust]
    users_id = random.sample(cluster_all['user_id_csv'].tolist(), int(nb_users))
    users_idx = [cluster_all.index[cluster_all['user_id_csv'] == i].tolist()[0]
     for i in users_id ]

    users = []
    for i in users_idx:
    	users.append(dict(name=cluster_all.loc[i]['names'], 
    		reviewing_style=cluster_all.loc[i]['Average sentiment'],
    		title=cluster_all.loc[i]['title'],
    		user_gr_id=cluster_all.loc[i]['user_id_csv']))


    return render_template("output.html", users=users)
