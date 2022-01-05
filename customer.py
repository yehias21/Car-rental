from flask import (Blueprint, flash, redirect, render_template, request, url_for, session)
# from auth import login_required

import carSQL as sql

bp = Blueprint('customer', __name__, 'customer.py')
conn = sql.conn
db = sql.db


@bp.route('/customer')
def index():
    # TODO
    # Show sth for customer
    return render_template('customer/index.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
