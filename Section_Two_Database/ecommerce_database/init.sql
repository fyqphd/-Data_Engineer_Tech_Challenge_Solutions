CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    membership_id VARCHAR NOT NULL,
    item_id INTEGER NOT NULL,
    orderstatus_id INTEGER NOT NULL,
    total_price FLOAT NOT NULL,
    total_weight FLOAT NOT NULL,
    items_bought INTEGER NOT NULL,
    order_date TIMESTAMP NOT NULL
);

CREATE TABLE order_status (
    orderstatus_id SERIAL PRIMARY KEY,
    status VARCHAR NOT NULL,
    last_update TIMESTAMP NOT NULL
);

CREATE TABLE customers (
    membership_id VARCHAR PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    date_of_birth TIMESTAMP NOT NULL,
    mobile_no VARCHAR NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR NOT NULL
);

CREATE TABLE items (
    item_id SERIAL PRIMARY KEY,
    manufacturer_id INTEGER NOT NULL,
    item_name VARCHAR NOT NULL,
    item_price FLOAT NOT NULL,
    item_weight FLOAT NOT NULL,
    item_category VARCHAR NOT NULL
);

CREATE TABLE item_stock (
    stock_id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    last_update TIMESTAMP NOT NULL
);

CREATE TABLE manufacturers (
    manufacturer_id SERIAL PRIMARY KEY,
    manufacture_name VARCHAR NOT NULL,
    manufacture_address VARCHAR NOT NULL
);

ALTER TABLE orders ADD CONSTRAINT fk_orders_membership_id FOREIGN KEY(membership_id)
REFERENCES customers (membership_id);

ALTER TABLE orders ADD CONSTRAINT fk_orders_item_id FOREIGN KEY(item_id)
REFERENCES items (item_id);

ALTER TABLE orders ADD CONSTRAINT fk_orders_orderstatus_id FOREIGN KEY(orderstatus_id)
REFERENCES order_status (orderstatus_id);

ALTER TABLE items ADD CONSTRAINT fk_items_manufacturer_id FOREIGN KEY(manufacturer_id)
REFERENCES manufacturers (manufacturer_id);

ALTER TABLE item_stock ADD CONSTRAINT fk_item_stock_item_id FOREIGN KEY(item_id)
REFERENCES items (item_id);

CREATE INDEX idx_items_item_name
ON items (item_name);

CREATE INDEX idx_manufacturers_manufacture_name
ON manufacturers (manufacture_name);
