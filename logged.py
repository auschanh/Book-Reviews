from flask import render_template, session, redirect, url_for, flash
from functools import wraps

# wrapper function that prevents certain routes if user is not logged in --> no session
# https://pythonprogramming.net/decorator-wrappers-flask-tutorial-login-required/
def authorize(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get("username") is None:
            flash("You need to be logged in")
            return redirect(url_for("login"))
        else:
            return f(*args, **kwargs)
    return wrap



