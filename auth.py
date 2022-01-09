import psycopg2
import functools
from flask import (Blueprint, flash, redirect, render_template, request, url_for, session, g)
from werkzeug.security import check_password_hash, generate_password_hash
import carSQL as sql


def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)

        return repl

    return layer


@parametrized
def login_required(func, role):
    @functools.wraps(func)
    def wrapped_view(**kwargs):
        print(g.user)
        requesting_role = role
        if g.user is None or (requesting_role == 'customer' and g.user.get('city') is None):
            return redirect(url_for('auth.login'))
        return func(**kwargs)

    return wrapped_view


bp = Blueprint('auth', __name__, url_prefix='/auth')
conn = sql.conn
db = sql.db


@bp.before_app_request
def load_logged_in_user():
    username = session.get('username')
    if username is None:
        g.user = None
    else:
        db.execute(sql.login_query(session['role']), (username,))
        g.user = db.fetchone()


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        role = 'admin' if role == 'admin' else 'customer'
        error = None
        db.execute(sql.login_query(role), (username,))
        user = db.fetchone()
        if user is None:
            error = 'Incorrect Username'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect Password'
        if error is None:
            session.clear()
            session['role'] = role
            session['username'] = user['username']
            session['id'] = user['id']
            print(user)
            print(user['country'])
            session['country'] = user['country']
            print(session['country'])
            return redirect(url_for('auth.home'))
        flash(error)
    return render_template("auth/login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        country = request.form.get("country")
        city = request.form.get("city")
        address = request.form.get("address")
        password = generate_password_hash(password)
        try:
            db.execute(sql.customer_register, (username, password, fname, lname, email, country, city, address))
            conn.commit()
            return redirect(url_for('auth.login'))
        except psycopg2.IntegrityError:
            error = f"User {username} is already registered."
            db.execute("ROLLBACK")
            flash(error)

    return render_template("auth/register.html")


@bp.route("/home", methods=["GET", "POST"])
def home():
    if session['role'] == 'admin':
        return redirect(url_for('admin.home'))
    elif session['role'] == 'customer':
        return redirect(url_for('customer.home'))
    return render_template("home.html")
