import psycopg2
import functools
from flask import (Blueprint, flash, redirect, render_template, request, url_for, session, g, jsonify)
from werkzeug.security import check_password_hash, generate_password_hash
import carSQL as sql

bp = Blueprint('auth', __name__, url_prefix='/auth')
conn = sql.conn
db = sql.db
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        data=request.get_json()
        print(data)
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
            return jsonify(ok=1)
        return jsonify(ok=0)


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
            flash(error)

    return render_template("auth/register.html")


@bp.route("/home", methods=["GET", "POST"])
def home():
    if session['role'] == 'admin':
        return redirect(url_for('admin.home'))
    elif session['role'] == 'customer':
        return redirect(url_for('customer.home'))
    return redirect(url_for('index'))

