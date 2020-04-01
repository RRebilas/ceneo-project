from ceneo.db import get_db
from flask import (
    Blueprint, render_template
)
import pandas as pd

bp = Blueprint('products', __name__, url_prefix='/products')


@bp.route('/')
def products():
    Product.products_list = []
    db = get_db()
    query = db.execute('SELECT product_id FROM products').fetchall()
    for el in query:
        p = Product(el['product_id'])
        p.product_values()
        Product.products_list.append(p)

    return render_template('products.html', products_list=Product.products_list)


@bp.route('/produkt/<int:id>')
def product(id):
    p = Product(id)
    p.product_values()

    return render_template('product_page.html', p=p)


class Product:
    products_list = []

    def __init__(self, product_id):
        self.product_id = product_id
        self.product_name = ""
        self.product_pros = 0
        self.product_cons = 0
        self.product_mean = 0
        self.product_opinions_count = 0
        self.data = None

    def product_values(self):
        db = get_db()
        # inner join with another table to get product name
        sql = 'select opinions.*, product_name from opinions' \
              ' inner join products p on opinions.product_id = p.product_id' \
              ' where opinions.product_id = ' + str(self.product_id)
        self.data = pd.read_sql_query(sql, db)
        self.product_name = self.data['product_name'].head(1).to_string(index=False)
        self.product_mean = self.data["stars"].mean().round(2)
        self.product_opinions_count = self.data['content'].count()
        self.product_pros = self.pros_and_cons('pros')
        self.product_cons = self.pros_and_cons('cons')

    def pros_and_cons(self, element):
        number = 0
        data = self.data[element].transform(lambda x: x.str.split('\n'))
        for elem in data:
            if elem is not None:
                number += len(list(filter(None, elem)))
        return number
