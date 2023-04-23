## PostgreSQL Database Design for E-commerce Sales Transactions

This document describes the design and implementation of a PostgreSQL database for an e-commerce company. 
The database is hosted in the Docker.

### Prerequisites
- Docker version 20.10.24, build 297e128
- PostgreSQL 15.2

### Database Overview

The database consists of the following six tables:

* orders
* customers
* items
* order_status
* item_stock
* manufactures

by designing this table, different teams can perform different functions

logistic team:

* total item weight
* how long is the shipping process
* update order shipping status
* optimal shipping routine

business insight team:

* popular items (index on item_name)
* frequent shoppers

warehouse team

* inventory status

Entity Relationship Diagram

![result image](./images/erd.png)

Dbeaver database view

![result image](./images/dbeaver.png)

Docker view

![result image](./images/docker.png)


