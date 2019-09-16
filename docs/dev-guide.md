# Developing Python Applications with CockroachDB

CockroachDB is compatible with some of the most popular PostgreSQL ORM's, including GORM, Hibernate, Sequelize, and SQLAlchemy. In this guide, we'll walk you through developing a Python application that uses Flask, SQLAlchemy, and CockroachDB to service customers of the fictional vehicle-sharing platform MovR.

MovR connects vehicle owners to vehicle users all over the world. To service its users, MovR needs a geo-distributed database to store information, and an application to handle requests from mobile and web clients. We'll use CockroachDB as the database engine of choice, and Python, Flask, and SQLAlchemy to create the application.

# Before you begin

Before you begin developing your application, make sure that you have installed the following:

- CockroachDB 19.2
- Python 3
- virtualenv or Docker

There are a number of Python libraries that you also need, including `sqlalchemy` and `cockroachdb`. We recommend listing all dependencies in a separate file (e.g. `requirements.txt`), and then handling this file when you create your virtual environment or Docker container.

In the sections that follow, we'll go through setting up following:

- [The database](setting-up-the-database)
- [A virtual environment](setting-up-a-virtual-environment)
- [A docker container](setting-up-a-docker-container)
- [The Python project](setting-up-the-python-project)

## Setting up the database

The `movr` database contains the following tables:

- `users`
- `vehicles`
- `rides`
- `vehicle_location_histories`
- `promo_codes`
- `user_promo_codes`

For more information about MovR, see the [Cockroach Labs website](https://www.cockroachlabs.com/docs/dev/movr.html).

The `movr` database, and an associated `movr` workload generator, are built into the CockroachDB binary. We'll map columns and relations from the built-in `movr` database to Python classes in our application, with SQLAlchemy.

To take a look at the the tables in the `movr` database, open a terminal, and run the following command:

~~~ shell
$ cockroach demo
~~~

This command opens a SQL shell to a single-node, in-memory cluster, with the `movr` database preloaded. You can use the `SHOW CREATE TABLE` command to see how each table is created:

~~~ sql
> SHOW CREATE TABLE users;
~~~
~~~
  table_name |                      create_statement
+------------+-------------------------------------------------------------+
  users      | CREATE TABLE users (
             |     id UUID NOT NULL,
             |     city VARCHAR NOT NULL,
             |     name VARCHAR NULL,
             |     address VARCHAR NULL,
             |     credit_card VARCHAR NULL,
             |     CONSTRAINT "primary" PRIMARY KEY (city ASC, id ASC),
             |     FAMILY "primary" (id, city, name, address, credit_card)
             | )
(1 row)
~~~

In production, you want to create a persistent database that is durability and optimizes performance. For instructions on starting a geo-distributed, multi-node, secure cluster, follow the instructions on the [Manual Deployment](https://www.cockroachlabs.com/docs/dev/manual-deployment.html) page of the Cockroach Labs documentation site.

<!--
## Setting up a virtual environment

## Setting up a Docker container
-->

## Setting up the Python project

The MovR application needs to handle requests from clients (a mobile application or web browser), and translate these requests as database transactions. For the purpose of this guide, our application stack will consist of the following components:

- A CockroachDB cluster in each of the localities where MovR is supported
- A Python server that handles requests from client mobile applications and web browsers

We have already set up the database. Let's start setting up our Python project. The project should have the following structure:

~~~ shell
movr
├── LICENSE
├── README.md
├── __init__.py
├── config.py
├── movr
│   ├── models.py
│   ├── movr.py
│   └── utils.py
├── requirements.txt
└── server.py
~~~

## Using the SQLAlchemy ORM

Object Relational Mappers (ORM's) map classes to tables and objects to rows. That is, for each table in a database, you define a class, and then each instance of that class represents a row in the table.

The `sqlalchemy` package includes some base classes and methods that you can use to connect to your database's server from a Python application, and then map database objects in that database (i.e. tables) to Python classes.

### Connecting to CockroachDB with SQLAlchemy

Let's start by using SQLAlchemy to create an interface that connects our application to a CockroachDB cluster. The `Engine` class defines this connection. If you haven't already, create a file named `movr.py`. This file will define our connection class.

~~~ python

~~~

### Mapping

By now you should be familiar with your CockroachDB cluster, the `movr` database, and each of the tables in the database.

Let's create a file called `models.py`

### APIs

- Querying
- Inserting

### Transactions

## Building a web application with Flask

By now you should have an idea of what components we need to connect to a running database, map our database objects to objects in Python, and then interact with the database transactionally. Let's actually build out the web application that can do this for us.


