import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import mpld3
import pandas as pd
from flask import (
    Blueprint, render_template, url_for, request, send_from_directory, abort)
from flask_table import Col, Table
from ceneo.db import get_db


bp = Blueprint('products', __name__, url_prefix='/products')


@bp.route('/')
def products():
    Product.products_list = []
    db = get_db()
    query = db.execute('SELECT product_id FROM products').fetchall()
    for el in query:
        p = ProductStats(el['product_id'])
        p.get_values_from_db()
        Product.products_list.append(p)

    return render_template('products.html', products_list=Product.products_list)


@bp.route('/<int:id>')
def product(id):
    sort = request.args.get('sort', 'id')
    reverse = (request.args.get('direction', 'asc') == 'desc')
    p = Product(id)
    data = p.data.to_dict(orient='records')
    if sort != 'id':
        data = p.data.sort_values(by=sort, ascending=reverse).to_dict(orient='records')
    table = OpinionsTable(data, sort_by=sort,
                          sort_reverse=reverse)
    return render_template('product_page.html', table=table, id=p.product_id, name=p.product_name)


@bp.route('/<int:id>/json')
def json_file(id):
    import pathlib
    Product(id).save_to_file()
    return send_from_directory(pathlib.Path().absolute().joinpath('download'),
                               filename=str(id) + '.json', as_attachment=True)


@bp.route('/<int:id>/wykresy')
def diagrams(id):
    p = Product(id)
    # rates chart
    rates = p.data['stars'].value_counts()
    fig, ax = plt.subplots()
    rates.plot.bar()
    plot1 = mpld3.fig_to_html(fig)
    # recommendation chart
    recommendation = p.data[(p.data['recommendation']) != '']['recommendation'].value_counts()
    fig, ax = plt.subplots()
    recommendation.plot.pie(startangle=90, autopct='%1.1f%%')
    plot = mpld3.fig_to_html(fig)
    plt.close()
    return render_template('diagrams.html', plot=plot, plot1=plot1, id=p.product_id)


class Product:
    products_list = []

    def __init__(self, product_id):
        self.product_id = product_id
        self.data = self.get_values_from_db()
        self.product_name = self.data['product_name'].head(1).to_string(index=False)

    def get_values_from_db(self):
        db = get_db()
        # inner join with another table to get product name
        sql = 'select opinions.*, product_name from opinions' \
              ' inner join products p on opinions.product_id = p.product_id' \
              ' where opinions.product_id = ' + str(self.product_id)
        return pd.read_sql_query(sql, db)

    def save_to_file(self):
        with open('./download/' + str(self.product_id) + '.json', 'w', encoding='utf8') as fp:
            fp.write(self.data.drop(columns=['product_id', 'product_name'])
                     .to_json(orient='records', force_ascii=False, indent=4))


class ProductStats(Product):
    def __init__(self, product_id):
        super().__init__(product_id)
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


class OpinionsTable(Table):
    def sort_url(self, col_id, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for(request.endpoint, **dict(request.view_args, sort=col_id, direction=direction))

    opinion_id = Col("id opinii")
    author = Col('autor')
    content = Col('treść')
    stars = Col('ocena')
    useful = Col('przydatne')
    useless = Col('nieprzydatne')
    date_of_issue = Col('data wystawienia')
    purchased = Col('Zakup')
    date_of_purchase = Col('data zakupu')
    pros = Col('zalety')
    cons = Col('wady')
    recommendation = Col('recommendation')
    classes = ['table', 'table-striped', 'table-dark']
    allow_sort = True
