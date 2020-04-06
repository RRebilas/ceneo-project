import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt
import mpld3
from flask import (
    Blueprint, render_template, request, send_from_directory, jsonify)
from .module.Product import OpinionsTable, Product, ProductStats
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
def product(id, data=None):
    p = Product(id)
    table = data if data is not None else render_html(p.data)
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
    ax.set_title('Oceny')
    plot1 = mpld3.fig_to_html(fig)
    # recommendation chart
    recommendation = p.data[(p.data['recommendation']) != '']['recommendation'].value_counts()
    fig, ax = plt.subplots()
    recommendation.plot.pie(startangle=90, autopct='%1.1f%%')
    plot = mpld3.fig_to_html(fig)
    plt.close()
    return render_template('diagrams.html', plot=plot, plot1=plot1, id=p.product_id)


def render_html(data):
    sort = request.args.get('sort')
    reverse = (request.args.get('direction', 'asc') == 'desc')
    table = data.to_dict(orient='records')
    if sort is not None:
        table = data.sort_values(by=sort, ascending=reverse).to_dict(orient='records')
    table = OpinionsTable(table, sort_by=sort, sort_reverse=reverse)
    return table
