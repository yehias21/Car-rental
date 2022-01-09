from flask import Flask, render_template, session, redirect, url_for, flash
from auth import login_required


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )
    from . import auth, admin, customer, car
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(customer.bp)
    app.register_blueprint(car.bp)

    @app.route("/home")
    @app.route("/")
    def index():
        if "username" in session:
            return redirect(('/auth/home'))
        return render_template("index.html")

    @app.route('/logout')
    def logout():
        if "username" in session:
            flash(f"{session['username']} hae been log out successfuly!", "info")
        session.clear()
        return redirect(url_for('index'))

    return app
