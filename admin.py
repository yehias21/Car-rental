import datetime

import flask
import psycopg2
from flask import (Blueprint, flash, redirect, render_template, request, url_for, session, jsonify)
# from auth import login_required
import carSQL as sql

bp = Blueprint('admin', __name__, url_prefix='/admin')
conn = sql.conn
db = sql.db


@bp.route("/register_car", methods=["GET", "POST"])
# @login_required
def register_car():
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
        error = None
        try:
            db.execute(sql.car_register, (plateID, year, brand, model, color, rate))
            db.execute(sql.car_image_register, (plateID, image))
            conn.commit()
        except psycopg2.IntegrityError:
            error = f"Car {plateID} is already registered"
            flash(error)
        else:
            return redirect(url_for("admin"))
    return render_template('admin/register_car.html')


@bp.route("/search_car", methods=["GET", "POST"])
def search_car():
    if request.method == 'POST':
        content = request.form
        plateID = content['plateID']
        year = content['modelYear']
        year = datetime.date(int(year), 1, 1)
        brand = content['brand']
        model = content['model']
        color = content['color']
        active = content['active']
        rate = content['rate']
        db.execute(sql.car_search, (plateID, year, brand, model, color, active, rate))
        cars = db.fetchall()
        # TODO: Render returned cars somehow
        # return render_template('admin/')


@bp.route('/cars/<string:plateid>', methods=('GET', 'POST'))
def view_car(plateid):
    db.execute(sql.car_search_plate, (plateid))
    car = db.fetchone()
    if request.method == 'POST':
        new_state = request.form['active']
        new_rate = request.form['rate']
        if new_state != car['active'] or car['rate'] != new_rate:
            try:
                db.execute(sql.update_car, (new_state, new_rate, plateid))
                conn.commit()
            except psycopg2.IntegrityError:
                return redirect(url_for('cars/' + plateid))
    return render_template('admin/car', car=car)


@bp.route('/reports/reservations', method=["POST"])
def reservations():
    content = request.json
    start = content['start_date']
    end = content['end_date']
    db.execute(sql.all_reservations, (start, end))
    results = db.fetchall
    return jsonify(results=results, size=len(results))


@bp.route('/reports/car_reservations', method=["POST"])
def car_reservations():
    content = request.json
    start = content['start_date']
    end = content['end_date']
    car = content['car']
    db.execute(sql.car_search_plate, (car,))
    car = db.fetchone
    db.execute(sql.all_reservations, (car, start, end))
    results = db.fetchall
    return jsonify(car=car, results=results, size=len(results))


@bp.route('/reports/customer_reservations', method=["POST"])
def customer_reservations():
    content = request.json
    customer = content['customer']
    db.execute(sql.search_customer, (customer,))
    customer = db.fetchone
    db.execute(sql.customer_reservations, (customer,))
    results = db.fetchall
    return jsonify(customer=customer, results=results, size=len(results))


@bp.route('/reports/payments', method=["POST"])
def customer_payments():
    content = request.json
    customer = content['customer']
    db.execute(sql.search_customer, (customer,))
    customer = db.fetchone
    db.execute(sql.customer_payments, (customer,))
    results = db.fetchall
    return jsonify(customer=customer, results=results, size=len(results))


@bp.route('/reports/status', method=['POST'])
def cars_status():
    content = request.json
    date = content['date']
    db.execute(sql.car_status, date)
    results = db.fetchall
    results = [(r['plateid'], r['status']) for r in results]
    return jsonify(results=results, size=len(results))


@bp.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
