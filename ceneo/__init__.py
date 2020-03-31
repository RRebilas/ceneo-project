import os
from . import db
from flask import (
    Flask, Blueprint, flash, g, redirect, render_template, request
)
from .module.Scrapper import Scrapper


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'ceneo.sqlite'),
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('index.html')

    db.init_app(app)

    @app.route('/extraction', methods=['GET', 'POST'])
    def extract():
        if request.method == "POST":
            product_id = request.form.get('product-id')
            if product_id is '':
                flash("Podaj kod produktu")
            else:
                Scrapper(product_id).scrap()

        return render_template('extraction.html')

    @app.route('/products')
    def products():
        return "product page"

    @app.route('/opinions')
    def opinions():
        return "opinions page"

    @app.route('/about')
    def about():
        return "about author"

    return app
