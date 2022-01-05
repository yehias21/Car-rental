from flask import Flask, render_template


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev'
    )
    from . import auth, admin, customer
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(customer.bp)
    app.add_url_rule('/',endpoint='index')

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
