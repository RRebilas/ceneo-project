DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS opinions;

CREATE TABLE products (
                          product_id INTEGER PRIMARY KEY NOT NULL UNIQUE,
                          product_name VARCHAR (255) NOT NULL
);

CREATE TABLE opinions (
                          opinion_id INTEGER PRIMARY KEY NOT NULL UNIQUE,
                          author TEXT NOT NULL,
                          stars INTEGER NOT NULL,
                          useful INTEGER NOT NULL,
                          useless INTEGER NOT NULL,
                          content TEXT NOT NULL,
                          date_of_issue TEXT NOT NULL,
                          recommendation TEXT,
                          purchased TEXT,
                          date_of_purchase TEXT,
                          cons TEXT,
                          pros TEXT,
                          product_id int NOT NULL,
                          FOREIGN KEY(product_id) REFERENCES products(product_id)
)