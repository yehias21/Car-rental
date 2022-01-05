import datetime

import psycopg2
from flask import (Blueprint, flash, redirect, render_template, request, url_for, session)
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


@bp.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
