import base64
import decimal

from flask import (Blueprint, flash, render_template, request, url_for, redirect, session, jsonify)
from auth import login_required
import psycopg2
import datetime

import carSQL as sql
import car as car

bp = Blueprint('customer', __name__, url_prefix='/customer')
conn = sql.conn
db = sql.db


@bp.route('/customer_home', methods=["GET", "POST"])
@login_required(role='customer')
def home():
    if request.method == "POST":
        if request.form['submit_type'] == 'search':
            content = request.json
            db.execute(sql.search_car(request.form))
            cars = db.fetchall()
            for car in cars:
                car['img'] = bytestoimg((car['img']))
            return render_template("Customer.html", cars=cars)
        elif request.form['submit_type'] == 'reserve':
            return redirect(url_for('customer.reserve_car', carid=request.form['carid']))

    db.execute(sql.all_cars, (session['country'],))
    cars = db.fetchall()
    for car in cars:
        car['img'] = bytestoimg((car['img']))
    return render_template("Customer.html", cars=cars)

# todo:optimize search car
@bp.route('/customer_search', methods=["GET", "POST"])
@login_required(role='customer')
def search_car():
    if request.method == "POST":
        content = request.json
        db.execute(sql.search_car(request.form))
        cars = db.fetchall()
        return render_template("cars.html", cars=cars)
    return render_template("customer/customer_search_car.html")

#todo: reserve car optimization
@bp.route('/customer_reserve/<string:car_id>', methods=["GET", "POST"])
@login_required(role='customer')
def reserve_car(car_id):
    if request.method == "POST":
        if request.form['reserve'] == 'no_pay':
            content = request.json
            custid = session['id']
            carid = str(car_id)
            reserve_date = datetime.date.today()
            pickup_date = request.form['start_date']
            return_date = request.form['end_date']
            db.execute(sql.get_car_rate, (carid,))
            rate = db.fetchone()
            bill = datetime.datetime.fromisoformat(return_date) - datetime.datetime.fromisoformat(pickup_date)
            bill = bill.days * decimal.Decimal(rate['rate'][1:])
            paid = False
            db.execute(sql.get_reserved_cars_between_date, (pickup_date, pickup_date, return_date))
            reserved_cars = db.fetchall()
            if carid not in [c['plateid'] for c in reserved_cars]:
                try:
                    db.execute(sql.car_reserve, (custid, carid, reserve_date, pickup_date, return_date, bill, paid))
                    conn.commit()
                    return redirect(url_for('customer.home'))
                except psycopg2.IntegrityError:
                    error = f"Car {carid} is already reserved."
                    db.execute("ROLLBACK")
                    flash(error)
            else:
                error = "Car is unavailable in this period."
                flash(error)
        elif request.form['reserve'] == 'with_pay':
            content = request.json
            custid = session['id']
            carid = str(car_id)
            current_date = datetime.date.today()
            pickup_date = request.form['start_date']
            return_date = request.form['end_date']
            db.execute(sql.get_car_rate, (carid,))
            rate = db.fetchone()
            bill = datetime.datetime.fromisoformat(return_date) - datetime.datetime.fromisoformat(pickup_date)
            bill = bill.days * decimal.Decimal(rate['rate'][1:])
            paid = True
            db.execute(sql.get_reserved_cars_between_date, (pickup_date, pickup_date, return_date))
            reserved_cars = db.fetchall()
            if carid not in [c['plateid'] for c in reserved_cars]:
                try:
                    db.execute(sql.car_reserve, (custid, carid, current_date, pickup_date, return_date, bill, paid))
                    conn.commit()
                    db.execute(sql.get_rid, (custid, carid, current_date))
                    rid = db.fetchall()
                    rid = max([r['rid'] for r in rid])
                    db.execute(sql.submit_payment, (rid, custid, bill, current_date))
                    conn.commit()
                    return redirect(url_for('customer.home'))
                except psycopg2.IntegrityError:
                    error = f"Car {carid} is already reserved."
                    db.execute("ROLLBACK")
                    flash(error)
            else:
                error = "Car is unavailable in this period."
                flash(error)
    return render_template("reserve.html")

# todo send the files reservations
@bp.route("/reservations")
@login_required(role='customer')
def view_reservations():
    return render_template("Reservations.html")


@bp.route("/reservations/past")
@login_required(role='customer')
def past_reservations():
    custid = session['id']
    current_date = datetime.date.today()
    db.execute(sql.past_reservations, (custid, current_date))
    reservations = db.fetchall()
    for res in reservations:
        res['img'] = bytestoimg((res['img']))
    return render_template("reservation_table.html", reservations=reservations, period='past')


@bp.route("/reservations/current", methods=["GET", "POST"])
@login_required(role='customer')
def current_reservations():
    custid = session['id']
    if request.method == "POST":
        rid = request.form['rid']
        db.execute(sql.get_reservation_data, (rid,))
        reservation_data = db.fetchone()
        amount = reservation_data['bill']
        current_date = datetime.date.today()
        db.execute(sql.submit_payment, (rid, custid, amount, current_date))
        conn.commit()
        db.execute(sql.update_paid_car, (rid,))
        conn.commit()
        return redirect(url_for('customer.current_reservations'))

    current_date = datetime.date.today()
    db.execute(sql.current_reservations, (custid, current_date))
    reservations = db.fetchall()
    for res in reservations:
        res['img'] = bytestoimg((res['img']))
    return render_template("reservation_table.html", reservations=reservations, period='current')


@bp.route("/reservations/pending", methods=["GET", "POST"])
@login_required(role='customer')
def pending_reservations():
    custid = session['id']
    if request.method == "POST":
        rid = request.form['rid']
        db.execute(sql.get_reservation_data, (rid,))
        reservation_data = db.fetchone()
        amount = reservation_data['bill']
        current_date = datetime.date.today()
        db.execute(sql.submit_payment, (rid, custid, amount, current_date))
        conn.commit()
        db.execute(sql.update_paid_car, (rid,))
        conn.commit()
        return redirect(url_for('customer.pending_reservations'))

    current_date = datetime.date.today()
    db.execute(sql.pending_reservations, (custid, current_date))
    reservations = db.fetchall()
    for res in reservations:
        res['img'] = bytestoimg((res['img']))
    return render_template("reservation_table.html", reservations=reservations, period='pending')



def bytestoimg(data):
    base = "data:image/jpeg;base64,"
    base += base64.b64encode(bytes.fromhex(data)).decode()
    return base
