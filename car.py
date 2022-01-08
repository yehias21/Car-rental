from flask import (Blueprint, flash, redirect, render_template, request, url_for, session)
from auth import login_required

import carSQL as sql

bp = Blueprint('car', __name__, url_prefix='/car')
conn = sql.conn
db = sql.db

@bp.route("/cars", methods=["GET", "POST"])
def show_all_cars():
    db.execute(sql.all_cars)
    cars = db.fetchall()
    return render_template("cars.html", cars=cars)