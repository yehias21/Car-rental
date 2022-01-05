from flask import (Blueprint, flash, redirect, render_template, request, url_for, session)
from auth import login_required

import carSQL as sql

bp = Blueprint('customer', __name__, url_prefix='/customer')
conn = sql.conn
db = sql.db


@bp.route('/customer_home', methods=["GET", "POST"])
def home():
    return render_template("customer/customer_home.html")


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
