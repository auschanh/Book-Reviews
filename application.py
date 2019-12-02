import os

from flask import Flask, session, request, render_template, url_for, redirect, flash, session, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash

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
            flash("Please enter a username and password")
        else:
            # strip white spaces from user entered values
            username = username.strip()
            password = password.strip()
        
        hashed_pass = generate_password_hash(password, 'sha256')

        # Create a new user and add the session
        new_user = User(username=username, pass_hash=hashed_pass)
        db.session.add(new_user)

        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            flash(f"Username {username} already exists")
            return redirect(url_for("register"))
        
        flash("User account created!")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
  
  msg = ""
  # accessed when method is POST
  if request.method == "POST":
      username = request.form["username"]
      password = request.form["password"]
      
      if not (username and password):
          flash("Please enter a username and/or password")
          return render_template("error.html", msg="No username or password entered")
      else:
          username = username.strip()
          password = password.strip()
      
      rows = db.execute("SELECT * FROM users WHERE username= :username", {"username": username})
      user_row = rows.fetchone()

      if user_row == None or check_password_hash(user_row[2], request.form["password"]):
          return render_template("error.html", msg="Invalid username or password")
        
      session[username] = True
      return redirect("./")
  else:
      return render_template("login.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")




if __name__ ==  "__main__":
    app.run(debug=True, port=5000)