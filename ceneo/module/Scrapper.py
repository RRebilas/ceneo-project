# import libraries
import requests
from bs4 import BeautifulSoup
from .Opinion import Opinion
from ceneo.db import get_db
import json


class ProductPage:
    prefix = "https://ceneo.pl/"
    postfix = "tab=reviews"

    def __init__(self, product_id):
        self.product_id = product_id
        self.opinions = []
        self.product_url = ProductPage.prefix + product_id + ProductPage.postfix
        self.product_name = ''

    def to_json_file(self):
        with open(self.product_id + '.json', 'w', encoding='utf-8') as fp:
            json.dump(list(map(lambda obj: obj.__dict__, self.opinions)), fp, ensure_ascii=False,
                      indent=2, separators=(',', ': '))


class Scrapper(ProductPage):

    def __init__(self, product_id):
        super().__init__(product_id)
        self.url = Scrapper.prefix + self.product_id + Scrapper.postfix

    def scrap(self):
        while self.url:

            page_response = requests.get(self.url)
            if page_response.status_code == 200:
                page_tree = BeautifulSoup(page_response.text, "html.parser")
                opinions_all = page_tree.find_all("li", "js_product-review")
                self.product_name = page_tree.find('h1','product-name').string

                for element in opinions_all:
                    # Call object and append to list
                    self.db_insert_opinions(Opinion(element))
                try:
                    self.url = Scrapper.prefix + page_tree.find('a', 'pagination__next')['href']
                except TypeError:
                    self.url = None
            else:
                break
            self.db_insert_product()

    #     function for adding opinion to db
    def db_insert_product(self):
        error = None
        db = get_db()
        if db.execute('Select product_id FROM products WHERE product_id = ?', (self.product_id,)
                      ).fetchone() is not None:
            #                 redirect to product page
            error = 'Product already exists'
        if error is None:
            db.execute('Insert INTO products Values (?, ?, ?)',
                       (int(self.product_id), self.product_name, self.product_url))
            db.commit()

    def db_insert_opinions(self, element):
        db = get_db()
        db.execute('INSERT INTO opinions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (element.opinion_id, element.author, element.stars, element.useful, element.useless,element.content,
                    element.date_of_issue, element.recommendation, element.purchased,element.date_of_purchase,
                    element.cons, element.pros, self.product_id))
        db.commit()
