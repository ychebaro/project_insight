# Insight Data Science Project Fall session 2019

This is a repository of the code for the Insight Project developed during the first weeks and contains Python scripts for preprocessing the data, computing the clusters and the web application.

## Preprocessing the data

cleaning_books.py

The first steps consists of cleaning up the GoodReads book data, specifically extracting meaningful tags and science-fiction related books. 

users_books_ratings.py

Getting the matrix of users x books ratings from the database

## Clustering users

clustering.py

A two step clustering based on user-book ratings and publication year/secondary theme tag

## Matching users

find_users.py

Matching users for a specific user according to similarity matrix within each cluster


# Unit testing
The folder tests contains unit testing code for the python scripts and some mock data to try the unit tests
