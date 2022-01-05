from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.config.from_mapping(
        SECRET_KEY='dev'
    )

DB_HOST = "localhost"
DB_NAME = "carsystem"
DB_USER = "postgres"
DB_PASS = "postgres"

conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    db = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        role = 'admin' if role == 'admin' else 'customer'
        error = None
        db.execute('SELECT * FROM %s WHERE username = %s', (role, username,))
        user = db.fetchone()
        if user is None:
            error = 'Incorrect Username'
        elif password != user['password']:
            error = 'Incorrect Password'
        if error is None:
            session.clear()
            session['role'] = role
            session['user_id'] = user['id']
            return redirect(url_for('home'))
        flash(error)

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        db = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        fname = request.form.get("firstname")
        lname = request.form.get("lastname")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        country = request.form.get("country")
        city = request.form.get("city")
        address = request.form.get("address")
        # db.execute("SELECT * FROM customer")
        # customers = db.fetchall()
        # customer_usernames = [row[1] for row in customers]
        # customer_emails = [row[5] for row in customers]
        #
        # if username in customer_usernames or email in customer_emails:
        #     return redirect(url_for('register'))
        #
        # cars = db.fetchall()
        try:
            db.execute(
                "INSERT INTO customer (username, password, fname, lname, email, country, city, address) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (username, password, fname, lname, email, country, city, address))
            conn.commit()
            return redirect(url_for('login'))
        except psycopg2.IntegrityError:
            error = f"User {username} is already registered."
            flash(error)

    return render_template("register.html")


@app.route("/cars")
def cars():
    db = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "SELECT * FROM CAR"
    db.execute(query)
    cars = db.fetchall()
    return render_template("cars.html", cars=cars)


@app.route("/home", methods=["GET", "POST"])
def home():
    # db = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # fname = request.form.get("firstname")
    # lname = request.form.get("lastname")
    # username = request.form.get("name")
    # email = request.form.get("email")
    # password = request.form.get("pass")
    # country = request.form.get("country")
    # city = request.form.get("city")
    # address = request.form.get("address")
    #
    # db.execute("SELECT * FROM customer")
    # customers = db.fetchall()
    # customer_usernames = [row[1] for row in customers]
    # customer_emails = [row[5] for row in customers]
    #
    # if username in customer_usernames or email in customer_emails:
    #     return redirect(url_for('register'))
    #
    # cars = db.fetchall()
    # db.execute(
    #     "INSERT INTO customer (username, password, fname, lname, email, country, city, address) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
    #     (username, password, fname, lname, email, country, city, address))
    # conn.commit()
    return render_template("home.html")
