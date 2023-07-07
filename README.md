# Checkout the Website
https://bookreviews-app.fly.dev/

1) Sign up
2) Search for books (try searching for "money" and look for "making money" to see a book with some comments/reviews)
3) Leave a comment and rating

Note: your **reviews** will show under your **username** in the **navbar**. When revisiting the site, sometimes your reviews won't show - just refresh in this case.
# About this Book Reviews Website
This website allows you to **register** and **search** for a book from a small set of data (5000 random book entries in the db). <br>

Registered users can then **search** for a book title or ISBN, click on the desired result from the results page and view the book cover, isbn, title, author, ratings etc. <br>

The resulting data associated with the book was taken from a books.csv file from CS50W (inserted with my script into a postgres db), and combined with the Openlibrary API.

# Purpose and Learning Objectives

The purpose of this project was to learn and understand:
1) Handling of sessions (login and logout) with flask
2) Querying for data in a fly.io hosted postgresSQL database
3) Registration system with data insertion into a postgres database hosted by fly.io
4) Using data through API calls to the Openlibrary api and displaying it on the site
5) Deploying and configuring a web project with a database

# Demo of Website
## Registering for an Account
![Registering for an Account](https://imgur.com/H1xd9Gh.gif "register page") <br>

## Searching for a Book
![Searching for a book](https://imgur.com/rQjfVIw.gif "searching functionality") <br>

## Leaving a Review and Rating
![Leaving a Review and Rating](https://imgur.com/4x2GmAA.gif "reviewing and rating a book") <br>

## Sorting Results Table
![Sorting the Results Table](https://imgur.com/IFbeeZc.gif "sorting functionality after book search") <br>

## Account Page
![Account Page](https://imgur.com/xxyZ7R4.gif "account page showing reviews")


