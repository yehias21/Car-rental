import datetime

from flask import (Blueprint, flash, redirect, render_template, request, url_for, session)
from auth import login_required
import carSQL as sql

bp = Blueprint('admin', __name__, url_prefix='/admin')
conn = sql.conn
db = sql.db


@bp.route("/admin/register_car", methods=["GET", "POST"])
@login_required
def register_car():
    if request.method == 'POST':
        content = request.form
        plateID = content['plateID']
        year = content['modelYear']
        year = datetime.date(int(year), 1, 1)
        brand = content['brand']
        model = content['model']
        color = content['color']
        image = content['image']
        error = None
        try:
            db.insert('INSERT INTO car (plateid,modelyr,brand,model,color) values (%s,%s,%s,%s,%s)',
                      (plateID, year, brand, model, color))
            conn.commit()
        except db.IntegrityError:
            error = f"Car {plateID} is already registered"
            flash(error)
        else:
            return redirect(url_for("admin"))
    return render_template('admin/register_car.html')


@bp.route('/admin/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
