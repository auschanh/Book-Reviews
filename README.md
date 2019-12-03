
# Book Reviews Website

Web Programming with Python(Flask) and SQL

This is Project 1 for CS50W.

The purpose of this project is to demonstrate and show my understanding of:
1) Handling of sessions (login and logout) with flask
2) Querying for data in a Heroku hosted SQL database
2) Registration system with data insertion into an SQL database hosted by Heroku
3) Searching data through API calls to GoodReads Book Reviews
4) Creating my own API function for user created reviews

# Setup for Windows

1) Download repository
2) Type this in terminal:
    - set FLASK_APP=application.py
    - set FLASK_DEBUG=1
    - set DATABASE_URL=postgres://aakqukwkqtzfek:7e548b822c3117b3de31f6fbb8c9d4155ce98fbe540f16ced6eaab3cc42a675d@ec2-23-21-160-38.compute-1.amazonaws.com:5432/dd8eanln6b1fr
3) Run the flask app by typing:
    py -m flask run
4) Navigate to http://127.0.0.1:5000/

