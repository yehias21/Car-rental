from flask import (Blueprint, flash, redirect, render_template, request, url_for, session)
from auth import login_required
import datetime

import carSQL as sql
import car as car

bp = Blueprint('customer', __name__, url_prefix='/customer')
conn = sql.conn
db = sql.db


@bp.route('/customer_home', methods=["GET", "POST"])
@login_required(role='customer')
def home():
    return render_template("customer/customer_home.html")


@bp.route('/customer_search', methods=["GET", "POST"])
def search_car():
    if request.method == "POST":
        #     content = request.form
        #     brand = content["brand"]
        #     model = content["model"]
        #     model_year = content["model_year"]
        #     model_year = model_year if model_year != '' else '1970'
        #     model_year = datetime.date(int(model_year), 1, 1)
        #     color = content["color"]
        #     plateID = ''
        #     active = True
        #     rate = ''
        #     db.execute(sql.car_search_customer, (plateID, model_year, brand, model, color, rate, active))
        #     cars = db.fetchall()
        #     return render_template("cars.html", cars=cars)
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
        print(query)
        db.execute(query)
        cars = db.fetchall()
        return render_template("cars.html", cars=cars)
    return render_template("customer/customer_search_car.html")


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
