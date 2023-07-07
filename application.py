import os
import requests

from logged import authorize
from flask import Flask, session, request, render_template, url_for, redirect, flash, session, abort, jsonify
from flask_session import Session
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from titlecase import titlecase

from dotenv import load_dotenv

app = Flask(__name__)

# Check for environment variable

if not os.getenv('DATABASE_URL'):
    load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/account")
@authorize
def account():
    user = session["username"]
    own_review = db.execute("SELECT title, review, rating, isbn FROM reviews WHERE username=:username", {"username": user})
    own_review = own_review.fetchall()
    review = own_review
    return render_template("index.html", review=review)

@app.route("/")
def index():
    if session.get('username'):
        user = session["username"]
        own_review = db.execute("SELECT title, review, rating, isbn FROM reviews WHERE username=:username", {"username": user})
        own_review = own_review.fetchall()
        review = own_review
        return render_template("index.html", review=review)
    else:
        return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"] 
        password = request.form["password"]
        if not (username and password):
            return render_template("error.html", msg="username and/or password required")
        else:
            # strip white spaces from user entered values
            username = username.strip()
            password = password.strip()
        
        hashed_pass = generate_password_hash(password, 'sha256')
        try:
            rows = db.execute("SELECT * FROM users WHERE username= :username", {"username": username.lower()})
            row = rows.fetchone()

            if row:
                return render_template("error.html", msg="that username already exists")
        
            if not request.form["password"] == request.form["confirm_password"]:
                return render_template("error.html", msg="passwords didn't match")

            # SQL command, INSERT user data from register.html
            username = username.lower()   
            db.execute("INSERT INTO users(username, hash_pass, fname, lname) VALUES (:username, :hash_pass, :fname, :lname)",
            {"username": username,
            "hash_pass": hashed_pass,
            "fname": request.form["fname"],
            "lname": request.form["lname"]
            })
            db.commit()
        except exc.SQLAlchemyError:
            db.rollback()
        finally:
            db.close()
        flash("User account created!")
        session[username] = True
        session["username"] = username
        return redirect(url_for("index"))
    else:
        return render_template("register.html")
        

@app.route("/login", methods=["GET", "POST"])
def login():
  
  if request.method == "POST":
      username = request.form["username"]
      password = request.form["password"]
      
      if not (username and password):
          return render_template("error.html", msg="No username or password entered")
      else:
          username = username.strip().lower()
          password = password.strip()
      
      rows = db.execute("SELECT * FROM users WHERE username= :username", {"username": username})
      user_row = rows.fetchone()
      
      if user_row == None or not check_password_hash(user_row[1], request.form["password"]):
          return render_template("error.html", msg="Invalid username or password")
      try:
          db.commit()
      except exc.SQLAlchemyError:
          db.rollback()
      finally:
          db.close()  
      session[username] = True
      session["username"] = user_row[0] # set session username to username from query
      return redirect(url_for("index"))
  else:
      return render_template("login.html")

@app.route("/logout/<username>")
@authorize
def logout(username):
    session.clear()
    session.pop(username, None)
    flash("You are now logged out.")
    return redirect(url_for("login"))

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/search", methods=["GET", "POST"])
@authorize
def search():
    if request.method == "POST":
        query = request.form["bookquery"]
        if query == "": 
            flash("Please type something!")
            return redirect(url_for("search"))
        query = titlecase(query)    # capitalize each letter in string except articles (but not at start of query)
        search_result = query.strip()
        # add the wildcard for LIKE queries
        query_replaced = query.replace(" ", "%")
        book = "%" + query_replaced + "%"
        if not book:
            return render_template("error.html", msg="Please type a book title, ISBN, or author")
        rows = db.execute("SELECT * FROM books WHERE isbn LIKE :book OR\
            title LIKE :book OR \
            author LIKE :book ",
            {"book": book})
        if rows.rowcount == 0:
            flash(f"No results found for {query}")
            return redirect(url_for("search"))
        results = rows.fetchall() # fetch all results instead of fetchone as used in login route
        return render_template("results.html", books=results, query=search_result)
    else:
        return render_template("search.html")

@app.route("/books/<isbn>", methods=["GET", "POST"])
@authorize
def books(isbn):
    # user submitted a review
    if request.method == "POST":
        # grab necessary variables/info
        user = session["username"]
        rating = request.form["rating"]
        message = request.form.get("message", None)

        if not message:
            flash("Please write a review!")
            return redirect(request.url)
        try:
            check = db.execute("SELECT username, isbn FROM reviews \
                WHERE username=:username\
                AND isbn=:isbn",
                {"username": user, "isbn": isbn})
            db.commit()
        except exc.SQLAlchemyError:
            db.rollback()
        finally:
            db.close()
        check = check.fetchone()
        # prevent a user from submitting a review for something they already reviewed
        if check is not None:
            flash("You've already reviewed this book!")
            return redirect(request.url) # returns to same page
        
        # grab title 
        try:
            get_title = db.execute("SELECT title FROM books WHERE isbn=:isbn", {"isbn": isbn})
            get_title = get_title.fetchone()
        
            title = get_title["title"]
            query = db.execute("INSERT INTO reviews(username, title, review, rating, isbn) VALUES\
                (:username, :title, :review, :rating, :isbn)",
                {"username": user, "title": title, "review": message, "rating": rating, "isbn": isbn})
            db.commit()
        except exc.SQLAlchemyError:
            db.rollback()
        finally:    
            db.close()
        flash(f"Review submitted for {title}")
        return redirect(request.url)
        
    else: 
        # user clicked on book from results page GET
        try:
            check = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn=:isbn", {"isbn": isbn})
            check = check.fetchall()
        except exc.SQLAlchemyError:
            db.rollback()
        finally: 
            db.close()
        if check is None:
            return render_template("error.html", msg=f"there is no book with ISBN {isbn}")

        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=details&format=json"

        payload={}
        headers = {}

        res = requests.request("GET", url, headers=headers, data=payload)
        response = res.json()
        response = response[f"ISBN:{isbn}"]["details"]
        check.append(response)

        url = f"https://openlibrary.org/search.json?isbn={isbn}&fields=rating*"
        ratings = requests.request("GET", url, headers=headers, data=payload)
        ratings = ratings.json()
        ratings = ratings["docs"]
        check.append(ratings)
        print(check)
        books_list = check

        # fetch our own reviews (submitted on my website, on my database), query with SQLalchemy
        try:
            own_review = db.execute("SELECT books.isbn, review, rating, username FROM books JOIN reviews\
                ON books.isbn = reviews.isbn WHERE books.isbn=:isbn", {"isbn":isbn})
            own_review = own_review.fetchall()
            review = own_review
            db.commit()
        except exc.SQLAlchemyError:
            db.rollback()
        finally:
            db.close()

        return render_template("books.html", response=books_list, review=review)

# removing custom API for now
# @app.route("/api/<isbn>")
# @authorize
# def isbn_api(isbn):
    
#     check = db.execute("SELECT isbn FROM books WHERE isbn= :isbn", {"isbn": isbn})
#     if check.fetchone() == None:
#         return jsonify({"error": "Invalid ISBN"}), 404
    
#     # call goodreads API for review data
#     key = "notactuallymykey"
#     res = requests.get(f"https://www.goodreads.com/book/review_counts.json", params={"key": key, "isbns": isbn})
#     response = res.json()
#     response = response["books"][0]

#     # fetch review count and average score
#     review_count = response["reviews_count"]
#     average_rating = response["average_rating"]

#     # fetch title, author, isbn, year from our DB
#     query = db.execute("SELECT * FROM books WHERE isbn=:isbn", {"isbn": isbn})
#     book_info = query.fetchone()
#     return jsonify({
#         "title": book_info["title"],
#         "author": book_info["author"],
#         "year": book_info["year"],
#         "isbn": book_info["isbn"],
#         "review_count": review_count,
#         "average_score": average_rating
#     })

if __name__ ==  "__main__":
    app.run(debug=False, port=8080)