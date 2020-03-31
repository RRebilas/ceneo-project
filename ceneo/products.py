from ceneo.db import get_db
from flask import (
    Blueprint, render_template
)
import pandas as pd


bp = Blueprint('products', __name__, url_prefix='/products')


@bp.route('/')
def products():
    db = get_db()
    query = db.execute('SELECT * FROM products').fetchall()
    products_list = []
    for el in query:
        p = Product(el['product_id'], el['product_name'])
        p.product_values()
        products_list.append(p)

    return render_template('products.html', products_list=products_list)


class Product:
    def __init__(self, product_id, product_name):
        self.product_id = product_id
        self.product_name = product_name
        self.product_pros = 0
        self.product_cons = 0
        self.product_mean = 0
        self.data = None

    def product_values(self):
        db = get_db()
        # inner join with another table to get product name
        sql = 'select stars, cons, pros product_name from opinions inner join' \
              ' products p on opinions.product_id = p.product_id'
        self.data = pd.read_sql_query(sql, db)
        self.product_mean = self.data["stars"].mean().round(2)
