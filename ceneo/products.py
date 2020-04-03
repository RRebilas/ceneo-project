from ceneo.db import get_db
from flask import (
    Blueprint, render_template,
    send_file, current_app)
import pandas as pd
import os

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


@bp.route('/<int:id>')
def product(id):
    p = Product(id)

    data = p.data.drop(columns=['id produktu', 'nazwa']).to_html(classes=['table', 'table-striped', 'table-dark'],
                                                                 index=False, justify='center',
                                                                 escape=False)
    return render_template('product_page.html', data=data, name=p.product_name, id=p.product_id)


@bp.route('/<int:id>/json')
def json_file(id):
    p = Product(id)
    p.save_to_file()
    return send_file('./downloads/' + str(p.product_id) + '.json', as_attachment=True, attachment_filename=str(p.product_id) + '.json')


@bp.route('/<int:id>/wykresy')
def diagrams(id):
    p = Product(id)
    return render_template('diagrams.html', id=p.product_id)


class Product:
    products_list = []

    def __init__(self, product_id):
        self.product_id = product_id
        self.data = self.product_values()
        self.product_name = self.data['product_name'].head(1).to_string(index=False)
        self.product_mean = self.data["stars"].mean().round(2)
        self.product_opinions_count = self.data['content'].count()
        self.product_pros = self.pros_and_cons('pros')
        self.product_cons = self.pros_and_cons('cons')
        self.data.columns = ['id opinii', 'autor', 'ocena', 'przydatne', 'nieprzydatne', 'komentarz',
                             'data wystawienia',
                             'rekomendacja', 'Zakup', 'data zakupu', 'wady', 'zalety', 'id produktu', "nazwa"]

    def product_values(self):
        db = get_db()
        # inner join with another table to get product name
        sql = 'select opinions.*, product_name from opinions' \
              ' inner join products p on opinions.product_id = p.product_id' \
              ' where opinions.product_id = ' + str(self.product_id)
        return pd.read_sql_query(sql, db)

    def pros_and_cons(self, element):
        number = 0
        data = self.data[element].transform(lambda x: x.str.split('\n'))
        for elem in data:
            if elem is not None:
                number += len(list(filter(None, elem)))
        return number

    def save_to_file(self):
        fp = open('./downloads/' + str(self.product_id) + '.json', 'w', encoding='utf8')
        self.data.drop(columns=['id produktu', 'nazwa']).to_json(fp, orient='records', force_ascii=False, indent=4)

