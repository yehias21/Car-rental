import base64
import datetime

import flask
import psycopg2
from flask import (Blueprint, flash, redirect, render_template, request, url_for, session, jsonify)
from auth import login_required
import carSQL as sql

bp = Blueprint('admin', __name__, url_prefix='/admin')
conn = sql.conn
db = sql.db


@bp.route('/admin_home', methods=["GET", "POST"])
# @login_required(role='admin')
def home():
    if request.method == "GET":
        db.execute(sql.all_cars_admin)
        cars = db.fetchall()
        for car in cars:
            car['img'] = bytestoimg((car['img']))
            car['active'] = 'Active' if car['active'] else 'Out of Service'
        carBody = render_template("carbody.html",cars=cars)
        return render_template("addAndManageCars.html", carBody=carBody)
    return redirect(url_for('admin.view_car', plateid=request.form['CarPlate']))


@bp.route('/Reports', methods=["GET", "POST"])
@login_required(role='admin')
def records():
    return render_template("Reports.html")


@bp.route("/register_car", methods=["GET", "POST"])
# @login_required(role='admin')
def register_car():
    print("here")
    if request.method == 'POST':
        image = request.files['image'].read()
        content = request.form
        plateID = content['plateID']
        year = content['modelYear']
        year = datetime.date(int(year), 1, 1)
        brand = content['brand']
        model = content['model']
        color = content['color']
        rate = content['rate']
        officeloc = str.lower(content['officeloc'])
        error = None
        try:
            db.execute(sql.car_register, (plateID, year, brand, model, color, rate, officeloc))
            db.execute(sql.car_image_register, (plateID, image))
            conn.commit()
        except psycopg2.IntegrityError:
            error = f"Car {plateID} is already registered"
            db.execute("ROLLBACK")
            flash(error)
        else:
            return redirect(url_for("admin"))
    return render_template('addCar.html')


@bp.route("/search_car", methods=["GET", "POST"])
@login_required(role='admin')
def search_car():
    if request.method == 'POST':
        content = request.form
        print(content)
        plateID = content.get('plateID')
        year = content.get('modelYear')
        print(year)
        year = 1970 if year is '' else year
        year = datetime.date(int(year), 1, 1)
        brand = content.get('brand')
        model = content.get('model')
        color = content.get('color')
        active = content.get('active')
        rate = content.get('rate')
        officeloc = content.get('officeloc')
        officeloc = None if officeloc is None else str.lower(officeloc)
        query = sql.car_search
        inputs = (plateID, year, brand, model, color, rate, officeloc)
        if active != '':
            query += " or active = %s::bool"
            inputs = (plateID, year, brand, model, color, rate, officeloc, active)
        db.execute(query, inputs)
        cars = db.fetchall()
        for car in cars:
            car['img'] = bytestoimg((car['img']))
            car['active'] = 'Active' if car['active'] else 'Out of Service'
        print(cars)
        return render_template("carbody.html", cars=cars)
        # return render_template('admin/')


@bp.route('/car/<string:plateid>', methods=['GET', 'POST'])
@login_required(role='admin')
def view_car(plateid):
    print(plateid)
    db.execute(sql.car_search_plate, (plateid,))
    car = db.fetchone()
    content = request.form
    if request.method == 'POST':
        print("hhhhhhh")
        new_state = content['active'] == 'True'
        new_rate = content['rate']
        if new_rate != car['rate']:
            try:
                db.execute(sql.update_car_rate, (new_rate, plateid))
                conn.commit()
            except psycopg2.IntegrityError:
                db.execute("ROLLBACK")
                # TODO THROW ERROR
        try:
            if (new_state, car['active']) == (False, True):
                db.execute(sql.update_car_state, (new_state, plateid))
                db.execute(sql.car_out_service, (plateid, str(datetime.date.today())))
                conn.commit()
            elif (new_state, car['active']) == (True, False):
                db.execute(sql.update_car_state, (new_state, plateid))
                db.execute(sql.car_in_service, (str(datetime.date.today()), plateid))
                conn.commit()
        except psycopg2.IntegrityError:
            db.execute("ROLLBACK")
            # TODO THROW ERROR
    db.execute(sql.car_search_plate, (plateid,))
    car = db.fetchone()
    car['img'] = bytestoimg((car['img']))
    car['active'] = 'Active' if car['active'] else 'Out of Service'
    return render_template('carDetails.html', car=car)


@bp.route('/reports/reservations', methods=["POST"])
@login_required(role='admin')
def reservations():
    content = request.json
    start = content['start_date']
    end = content['end_date']
    db.execute(sql.all_reservations, (start, end))
    results = db.fetchall()
    return jsonify(results=results, size=len(results))


@bp.route('/reports/car_reservations', methods=["POST"])
@login_required(role='admin')
def car_reservations():
    content = request.json
    start = content['start_date']
    end = content['end_date']
    car = content['car']
    db.execute(sql.car_search_plate, (car,))
    car = db.fetchone
    db.execute(sql.all_reservations, (car, start, end))
    results = db.fetchall()
    return jsonify(car=car, results=results, size=len(results))


@bp.route('/reports/customer_reservations', methods=["POST"])
@login_required(role='admin')
def customer_reservations():
    content = request.json
    customer = content['customer']
    db.execute(sql.search_customer, (customer,))
    customer = db.fetchone
    db.execute(sql.customer_reservations, (customer, customer, customer))
    results = db.fetchall()
    return jsonify(customer=customer, results=results, size=len(results))


@bp.route('/reports/payments', methods=["POST"])
@login_required(role='admin')
def customer_payments():
    content = request.json
    customer = content['customer']
    db.execute(sql.search_customer, (customer,))
    customer = db.fetchone
    db.execute(sql.customer_payments, (customer,))
    results = db.fetchall()
    return jsonify(customer=customer, results=results, size=len(results))


@bp.route('/reports/status', methods=['POST'])
@login_required(role='admin')
def cars_status():
    content = request.json
    date = content['date']
    db.execute(sql.car_status, date)
    results = db.fetchall()
    results = [(r['plateid'], r['status']) for r in results]
    return jsonify(results=results, size=len(results))


def bytestoimg(data):
    base = "data:image/jpeg;base64,"
    base += base64.b64encode(bytes.fromhex(data)).decode()
    return base
