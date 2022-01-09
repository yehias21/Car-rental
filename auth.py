import psycopg2
import functools
from flask import (Blueprint, flash, redirect, render_template, request, url_for, session, g, jsonify)
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
        requesting_role = role
        if g.user is None or (requesting_role == 'customer' and g.user.get('city') is None) or (requesting_role == 'admin' and g.user.get('city') is not None):
            return redirect(url_for('auth.login'))
        return func(**kwargs)

    return wrapped_view


bp = Blueprint('auth', __name__, url_prefix='/auth')
conn = sql.conn
db = sql.db


@bp.before_app_request
def load_logged_in_user():
    print(session)
    username = session.get('username')
    if username is None:
        g.user = None
    else:
        print(session)
        db.execute(sql.login_query(session['role']), (username,))
        g.user = db.fetchone()


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        data=request.get_json()
        username = data['username']
        password = data['password']
        role = data['role']
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
            session['country'] = user.get('country')
            return jsonify(ok=1)
        return jsonify(ok=0)
    return render_template("login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        data=request.get_json()
        print(data)
        fname = data["name"]
        lname = data["lname"]
        username = data["username"]
        email = data["email"]
        password = data["password"]
        country = data["country"]
        city = data["city"]
        address = data["address"]
        password = generate_password_hash(password)
        try:
            db.execute(sql.customer_register, (username, password, fname, lname, email, country, city, address))
            conn.commit()
            return jsonify(ok=1)
        except psycopg2.IntegrityError:
            db.execute("ROLLBACK")
            return jsonify(ok=0)
    return render_template("register.html")


@bp.route("/home", methods=["GET", "POST"])
def home():
    if session['role'] == 'admin':
        return redirect(url_for('admin.home'))
    elif session['role'] == 'customer':
        return redirect(url_for('customer.home'))
    return redirect(url_for('index'))

