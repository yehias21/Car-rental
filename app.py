# from flask import Flask, render_template, request, flash, redirect, url_for, session
# from werkzeug.security import check_password_hash, generate_password_hash
# import psycopg2
# import carSQL as sql
# import psycopg2.extras
#
# app = Flask(__name__)
# app.config.from_mapping(
#     SECRET_KEY='dev'
# )
#
# DB_HOST = "localhost"
# DB_NAME = "carsystem"
# DB_USER = "postgres"
# DB_PASS = "postgres"
#
# conn = sql.conn
# db = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#
#
# @app.route("/")
# def index():
#     return render_template("index.html")
#
#
# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         role = request.form['role']
#         role = 'admin' if role == 'admin' else 'customer'
#         error = None
#         db.execute(sql.login_query(role), (username,))
#         user = db.fetchone()
#         if user is None:
#             error = 'Incorrect Username'
#         elif not check_password_hash(user['password'], password):
#             error = 'Incorrect Password'
#         if error is None:
#             session.clear()
#             session['role'] = role
#             session['user_id'] = user['id']
#             return redirect(url_for('home'))
#         flash(error)
#
#     return render_template("auth/login.html")
#
#
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == 'POST':
#         fname = request.form.get("firstname")
#         lname = request.form.get("lastname")
#         username = request.form.get("username")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         country = request.form.get("country")
#         city = request.form.get("city")
#         address = request.form.get("address")
#         password = generate_password_hash(password)
#         try:
#             db.execute(sql.customer_register, (username, password, fname, lname, email, country, city, address))
#             conn.commit()
#             return redirect(url_for('login'))
#         except psycopg2.IntegrityError:
#             error = f"User {username} is already registered."
#             flash(error)
#
#     return render_template("auth/register.html")
#
#
# @app.route("/cars")
# def cars():
#     query = "SELECT * FROM CAR"
#     db.execute(query)
#     cars = db.fetchall()
#     return render_template("cars.html", cars=cars)
#
#
# @app.route("/home", methods=["GET", "POST"])
# def home():
#     return render_template("home.html")
