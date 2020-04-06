from pathlib import Path

import pandas as pd
from flask import url_for, request
from flask_table import Table, Col

from ceneo.db import get_db


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
        Path("./download").mkdir(parents=True, exist_ok=True)
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
        return url_for(request.endpoint,
                       **dict(request.view_args, column=request.args.get('column'), query=request.args.get('query'),
                              sort=col_id, direction=direction))

    classes = ['table', 'table-striped', 'table-dark']
    table_id = 'opinions'
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
    recommendation = Col('rekomendacja')
    allow_sort = True
