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
@login_required(role='admin')
def home():
    if request.method == "GET":
        db.execute(sql.all_cars_admin)
        cars = db.fetchall()
        for car in cars:
            car['img'] = bytestoimg((car['img']))
            car['active'] = 'Active' if car['active'] else 'Out of Service'
        return render_template("addAndManageCars.html", cars=cars)
    return redirect(url_for('admin.view_car', plateid=request.form['CarPlate']))


@bp.route('/Reports', methods=["GET", "POST"])
@login_required(role='admin')
def records():
    return render_template("Reports.html")


@bp.route("/register_car", methods=["GET", "POST"])
@login_required(role='admin')
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
        officeloc = str.lower(content['officeloc'])
        error = None
        try:
            db.execute(sql.car_register, (plateID, year, brand, model, color, rate, officeloc))
            db.execute(sql.car_image_register, (plateID, image))
            conn.commit()
        except psycopg2.IntegrityError:
            print('fail')
            error = f"Car {plateID} is already registered"
            db.execute("ROLLBACK")
            flash(error)
        else:
            return redirect(url_for("admin.home"))
    return render_template('addCar.html')


@bp.route("/search_car", methods=["GET", "POST"])
@login_required(role='admin')
def search_car():
    if request.method == 'POST':
        content = request.json
        print(content)
        plateID = content.get('plateID')
        year = content.get('modelYear')
        print(year)
        year = 1970 if year == '' else year
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
        new_cards = render_template("carbody.html", cars=cars)
        return jsonify(new=new_cards)


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
    for result in results:
        result['reserve_date'] = str(result['reserve_date'])
        result['pickup_date'] = str(result['pickup_date'])
        result['return_date'] = str(result['return_date'])
    report = render_template('Reports_show.html', title=[], kind='Reservations',
                             headings=['Reserve Date', 'Pickup Date'
                                 , 'Return Date', 'Cutomer Name', 'PlateID', 'Bill', 'Paid'],
                             data=results)
    return jsonify(report=report)


@bp.route('/reports/car_reservations', methods=["POST"])
@login_required(role='admin')
def car_reservations():
    content = request.json
    start = content['start_date']
    end = content['end_date']
    car = content['car']
    db.execute(sql.car_search_plate, (car,))
    car = db.fetchone()
    car['img'] = ''
    car['active'] = 'Active' if car['active'] else 'Out of Service'
    car = [car['plateid'], car['brand'], car['model'], int(car['year']), car['color'], car['active'], car['rate'],
           car['officeloc']]
    db.execute(sql.car_reservations_date, (content['car'], start, end))
    results = db.fetchall()
    results = [(r['reserve_date'], r['pickup_date'], r['return_date'], r['bill'], r['paid']) for r in results]
    print(results)
    for result in results:
        for entry in result:
            entry = str(entry)
    report = render_template('Reports_show.html', kind='Car Reservations', title=car,
                             headings=['Reserve Date', 'Pickup Date', 'Return Date', 'Bill', 'Paid'], data=results)
    return jsonify(report=report)


@bp.route('/reports/customer_reservations', methods=["POST"])
@login_required(role='admin')
def customer_reservations():
    content = request.json
    customer = content['customer']
    db.execute(sql.search_customer, (customer,))
    customer = db.fetchone()
    customer = [customer['fname'], customer['lname'], customer['email'], customer['country'], customer['city'],
                customer['address']]
    db.execute(sql.customer_reservations, (content['customer'], content['customer'],))
    results = db.fetchall()
    for result in results:
        result['reserve_date'] = str(result['reserve_date'])
        result['pickup_date'] = str(result['pickup_date'])
        result['return_date'] = str(result['return_date'])

    results = [(r['reserve_date'],r['pickup_date'],r['return_date'],r['bill'],r['paid'],r['carid'],r['car_model']) for r in results]
    report = render_template('Reports_show.html',title = customer,headings=['Reseve Date','Pickup Date','Return Date','Bill','Paid','Car ID','Car'],kind='Customer Reservations',data=results)
    return jsonify(report=report)


@bp.route('/reports/payments', methods=["POST"])
@login_required(role='admin')
def customer_payments():
    content = request.json
    customer = content['customer']
    db.execute(sql.search_customer, (customer,))
    customer = db.fetchone()
    print(customer)
    customer = [customer['fname'],customer['lname'],customer['email'],customer['country'],customer['city'],customer['address']]
    db.execute(sql.customer_payments, (content['customer'],))
    results = db.fetchall()
    results = [(r['carid'],r['reserve_date'],r['amount'],r['date']) for r in results]
    print(results)
    for result in results:
        for entry in result:
            entry = str(entry)
    report = render_template('Reports_show.html',title=customer, kind='Customer Payments', headings=['Plate ID', 'Reserve Date','Amount','Payment Date'], data=results)
    return jsonify(report=report)


@bp.route('/reports/status', methods=['POST'])
@login_required(role='admin')
def cars_status():
    content = request.json
    date = content['date']
    db.execute(sql.car_status, (date,))

    results = db.fetchall()
    print(results)

    results = [(r['plateid'], r['status']) for r in results]
    report = render_template('Reports_show.html', title=[], kind='Car Status', headings=['Plate ID', 'Status'],
                             data=results)
    return jsonify(report=report)


@bp.route('/reports/available_cars', methods=['POST'])
@login_required(role='admin')
def available_cars():
    content = request.json
    date = content['date']
    db.execute(sql.available_cars, (date, date, date))
    results = db.fetchall()
    results = [(r['plateid'], r['state']) for r in results]
    report = render_template('Reports_show.html', title=[], kind='Car Availability', headings=['Plate ID', 'State'],
                             data=results)
    return jsonify(report=report)


def bytestoimg(data):
    base = "data:image/jpeg;base64,"
    base += base64.b64encode(bytes.fromhex(data)).decode()
    return base
