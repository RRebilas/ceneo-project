# import libraries
from bs4 import BeautifulSoup
from .module.Opinion import Opinion
from ceneo.db import get_db
import json
from flask import (flash, redirect, url_for, Blueprint, render_template, request)
import requests

bp = Blueprint('scrapper', __name__)


@bp.route('/extraction', methods=['GET', 'POST'])
def extract():
    if request.method == "POST":
        product_id = request.form.get('product-id')
        if product_id == '':
            flash("Podaj kod produktu!")
        else:
            return Scrapper(product_id).scrap()
    return render_template('extraction.html')


class ProductPage:
    prefix = "https://ceneo.pl/"
    postfix = "tab=reviews"

    def __init__(self, product_id):
        self.product_id = product_id
        self.opinions = []
        self.product_name = ''
        self.page_tree = None
        self.page_response = None

    # should be from database

    def to_json_file(self):
        with open(self.product_id + '.json', 'w', encoding='utf-8') as fp:
            json.dump(list(map(lambda obj: obj.__dict__, self.opinions)), fp, ensure_ascii=False,
                      indent=2, separators=(',', ': '))


class Product(ProductPage):

    def __init__(self, product_id):
        super().__init__(product_id)
        self.url = Product.prefix + self.product_id + Product.postfix

    #     function for adding opinion to db

    def if_product_exists(self):
        db = get_db()

        if db.execute('SELECT product_id FROM products WHERE product_id = ?', (self.product_id,)
                      ).fetchone() is not None:
            return True

        return False

    def db_insert_product(self):
        db = get_db()

        if not self.if_product_exists():
            db.execute('Insert INTO products Values (?, ?)',
                       (int(self.product_id), self.product_name))
            db.commit()

    def db_insert_opinions(self, element):
        db = get_db()

        db.execute('INSERT INTO opinions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (element.opinion_id, element.author, element.stars, element.useful, element.useless,
                    element.date_of_issue, element.recommendation, element.purchased, element.date_of_purchase,
                    element.cons, element.pros, element.content, self.product_id))
        db.commit()


class Scrapper(Product):

    def connection(self):
        self.page_response = requests.get(self.url)
        if self.page_response.status_code == 200:
            self.page_tree = BeautifulSoup(self.page_response.text, "html.parser")
            return True
        return False

    def scrap(self):

        if self.connection():

            self.product_name = self.page_tree.find('h1', 'product-name').string

            if not self.if_product_exists():
                self.db_insert_product()
                # probably that will be a function to call
                while self.url:
                    if self.connection():
                        opinions_all = self.page_tree.find_all("li", "js_product-review")
                        for element in opinions_all:
                            # Call object and append to list
                            self.db_insert_opinions(Opinion(element))
                        try:
                            self.url = Product.prefix + self.page_tree.find('a', 'pagination__next')['href']
                        except TypeError:
                            self.url = None
                    else:
                        flash("Błąd połączenia")
                        break
                return redirect(url_for('products.product', id=self.product_id))
            else:
                # redirect to product page
                return redirect(url_for('products.product', id=self.product_id))
        else:
            flash("Brak danego produktu lub błąd połączenia")
            return render_template('extraction.html')
