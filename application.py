import os

from logged import authorize
from flask import Flask, session, request, render_template, url_for, redirect, flash, session, abort, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from titlecase import titlecase

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
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

        rows = db.execute("SELECT * FROM users WHERE username= :username", {"username": username.lower()})
        row = rows.fetchone()

        if row:
            return render_template("error.html", msg="that username already exists")
       
        if not request.form["password"] == request.form["confirm_password"]:
            return render_template("error.html", msg="passwords didn't match")

         # SQL command, INSERT user data from register.html   
        db.execute("INSERT INTO users(username, hash_pass, fname, lname) VALUES (:username, :hash_pass, :fname, :lname)",
        {"username": username,
        "hash_pass": hashed_pass,
        "fname": request.form["fname"],
        "lname": request.form["lname"]
        })
        
        db.commit()
        flash("User account created!")
        return redirect(url_for("index"))
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  
  msg = ""
  # accessed when method is POST
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
      
      # use when we hash the passwords
      #if user_row == None or not (user_row[1] == request.form["password"]):
      if user_row == None or not check_password_hash(user_row[1], request.form["password"]):
          return render_template("error.html", msg="Invalid username or password")
        
      session[username] = True
      session["username"] = user_row[0]
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
        # capitalize each letter in string except articles (but not at start of query)
        query = titlecase(query)
        print(query)
        # add the wildcard for LIKE queries
        book = "%" + query + "%"
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
        return render_template("results.html", books=results, query=query)
    else:
        return render_template("search.html")


@app.route("/api/<isbn>")
@authorize
def isbn_api(isbn):
    pass
    #res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "KEY", "isbns": "9781632168146"})

if __name__ ==  "__main__":
    app.run(debug=True, port=5000)