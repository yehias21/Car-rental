from flask import (Blueprint, flash, render_template, request, session)
from auth import login_required
import datetime

import carSQL as sql
import car as car

bp = Blueprint('customer', __name__, url_prefix='/customer')
conn = sql.conn
db = sql.db


@bp.route('/customer_home', methods=["GET", "POST"])
def home():
    return render_template("Customer.html")


@bp.route('/customer_search', methods=["GET", "POST"])
def search_car():
    if request.method == "POST":
        content = request.json
        where = " WHERE "
        if (request.form['brand']): where += f" brand={request.form['brand']} and"
        if (request.form['model']): where += f" model={request.form['model']} and"
        if (request.form['color']): where += f" color={request.form['color']} and"
        if (request.form['start_date']): where += f"pickup_date not between " \
                                             f"'{request.form['start_date']}' and '{request.form['end_date']}' and '{request.form['start_date']}' not between " \
                                             f"pickup_date and return_date and"
        query = "SELECT  brand,model,rate,extract(year from car.modelyr),encode(car_image.image,'hex') img " \
                "FROM car natural join car_image left join reservation on car.plateid=reservation.carid" \
                + where + " active=true;"
        db.execute(query)
        cars = db.fetchall()
        return render_template("cars.html", cars=cars)
    return render_template("customer/customer_search_car.html")


@bp.route('/customer_reserve', methods=["GET", "POST"])
def reserve_car():
    if request.method == "POST":
        content = request.json
        custid = session['id']
        carid = 'CAI83'
        reserve_date = datetime.date.today()
        pickup_date = request.form['start_date']
        return_date = request.form['end_date']
        bill = datetime.datetime.strptime(f"{pickup_date} 11:11AM", '%Y-%m-%d %I:%M%p').date() - datetime.datetime.strptime(f"{return_date} 11:11AM", '%Y-%m-%d %I:%M%p').date()
        bill = bill.days * 50
        paid = True
        db.execute(sql.car_reserve, (custid, carid, reserve_date, pickup_date, return_date, bill, paid))
        # cars = db.fetchall()
        conn.commit()
        return render_template("customer/reserve.html")
    return render_template("customer/reserve.html")

