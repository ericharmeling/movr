# Developing Python Applications with CockroachDB

CockroachDB is compatible with some of the most popular PostgreSQL ORM's, including GORM, Hibernate, Sequelize, and SQLAlchemy. In this guide, we walk through developing a Python application for the fictional vehicle-sharing platform [MovR](https://www.cockroachlabs.com/docs/dev/movr.html). We use Flask to build out a web API, and then the CockroachDB dialect of SQLAlchemy to communicate with a deployed CockroachDB cluster.

## Before you begin

Before you begin, make sure that you have installed the following:

- [CockroachDB 19.2](https://www.cockroachlabs.com/docs/dev/install-cockroachdb-mac.html)
- [`pipenv`](https://docs.pipenv.org/en/latest/install/#installing-pipenv)
- [Python 3](https://www.python.org/downloads/)

There are a number of Python libraries that you also need for this tutorial, including `flask`, `sqlalchemy`, and `cockroachdb`. Rather than downloading these dependencies directly from PyPi to your machine, we recommend that you use [`pipenv`](https://github.com/pypa/pipenv) to manage your dependencies in a production-ready virtual environment.

In the sections that follow, we walk through setting up:

- [The database](setting-up-the-database)
- [A virtual environment](setting-up-a-virtual-environment)
- [The Python project](setting-up-the-python-project)

## Setting up the database

MovR serves a global user base, so latency on SQL operations can significantly affect the user experience. With CockroachDB, you can [geo-partition](https://www.cockroachlabs.com/docs/dev/training/geo-partitioning.html) your data across a global cluster to improve performance. Let's set up a distributed CockroachDB cluster, and then partition the data based on the location where users need to access the data. 

### Setting up a CockroachDB cluster

In production, you want to start a secure CockroachDB cluster, with nodes on machines located in different areas of the world. For instructions on deploying a geo-distributed, multi-node, secure cluster on multiple cloud platforms, see the [Manual Deployment](https://www.cockroachlabs.com/docs/dev/manual-deployment.html) page of the Cockroach Labs documentation site. 
For the purposes of this tutorial, we use the [`cockroach demo`](https://www.cockroachlabs.com/docs/dev/cockroach-demo.html) command with the `--geo-partitioned-replicas` tag to start up an insecure, virtual nine-node cluster with the [Geo-Partitioned Replicas](https://www.cockroachlabs.com/docs/stable/topology-geo-partitioned-replicas.html) topology pattern applied:

~~~ shell
$ cockroach demo --geo-partitioned-replicas
~~~

This command also opens a SQL shell to the virtual cluster, with a `movr` database preloaded and set as the [current database](https://www.cockroachlabs.com/docs/dev/sql-name-resolution.html#current-database). Keep this terminal window open for the duration of the tutorial. The `movr` database, and an associated `movr` workload generator, are built into the CockroachDB binary. We'll map columns and relations from the `movr` database to Python classes in our application, with SQLAlchemy.

### The `movr` database

The `movr` database contains the following tables:

- `users`
- `vehicles`
- `rides`
- `vehicle_location_histories`
- `promo_codes`
- `user_promo_codes`

Here's an entity-relationship diagram, generated with [`DBeaver`](https://github.com/dbeaver/dbeaver/):

<img src="images/MovRSchema.png"/>

To get a more detailed look, you can query the tables in the database. For example, the `SHOW CREATE TABLE` command shows how a table is defined:

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

As we mentioned earlier, after you start the cluster, you need to [partition](https://www.cockroachlabs.com/docs/dev/partitioning.html) some tables and indexes in the database to optimize performance. With the `--geo-partitioned-replicas` flag, `cockroach demo` automatically partitions the database indexes according to the [Geo-Partitioned Replicas](https://www.cockroachlabs.com/docs/stable/topology-geo-partitioned-replicas.html) topology pattern.


## Setting up a virtual environment

Now that you have your geo-partitioned database up-and-running, you can set up the development environment for your application. Let's use `pipenv`, a tool that manages dependencies with `pip` and creates virtual environments with `virtualenv`.

In your terminal window, navigate to your project directory (if you haven't created one yet, go ahead and do so), and run the following command to initialize the project's virtual environment:

~~~ shell
$ pipenv --three
~~~

`pipenv` creates a `Pipfile` in the current directory. Open this `Pipfile`, and edit it to read as follows:

~~~ toml
[[source]]
name = "pypi"
url = "https://pypi.org/simple"
verify_ssl = true

[dev-packages]

[packages]
cockroachdb = "*"
psycopg2-binary = "*"
requests = "*"
SQLAlchemy = "*"
SQLAlchemy-Utils = "*"
Flask = "*"
Flask-SQLAlchemy = "*"
Flask-WTF = "*"

[requires]
python_version = "3.7" 
~~~

Then run the following command to install the packages listed in the `Pipfile`:

~~~ shell
$ pipenv install
~~~

You will likely have some system environment variables that you want to set for the virtual environment. or example, to connect to a SQL database (including CockroachDB!) from a client, you need a SQL connection string, with includes the host, port, user, and database. You can store all of this information in environment variables. Pipenv automatically sets any variables defined in a `.env` file as environment variables in a Pipenv virtual environment. So, create a file named `.env`, and define those connection string variables.

For example:

~~~
DB_HOST = 'localhost'
DB_PORT = 26257
DB_USER = 'root'
~~~

Then activate the virtual environment:

~~~ shell
$ pipenv shell
~~~

You can exit the shell subprocess at any time with a simple `exit` command.

~~~ shell
$ exit
~~~



## Setting up the Python project

The MovR application needs to handle requests from clients like mobile applications and web browsers. To translate these kinds of requests into database transactions, the application needs several components to work together. For the purpose of this guide, our application stack will consist of the following components:

- A multi-node, geo-distributed CockroachDB cluster, with each of the localities where MovR is supported (our `cockroach demo` cluster)
- A Flask server that handles requests from client mobile applications and web browsers
- HTML files that define web pages that our Flask server can host
- A file that defines Python classes that map to databases on our CockroachDB cluster
- A backend API that defines the connection to the database and transactions

We have already set up the database and our Python environment. We can finally start developing our Python project. The project should have the following structure:

~~~ shell
movr
├── LICENSE  ## A license file for your application
├── Pipfile ## A TOML-formatted file that lists out PyPi dependencies
├── Pipfile.lock
├── README.md  ## A readme file with instructions on running the application
├── __init__.py 
├── config.py  ## A configuration file that contains secret API keys, database urls, database credentials, and other configuration information
├── movr  ## A folder than contains the files that define the models and utility functions that make up the application
│   ├── models.py  ## A Python file that contains class that map to movr tables
│   ├── movr.py  ## A Python file that defines our primary backend API
│   └── utils.py  ## A Python file that contains utility functions for the server
└── server.py  ## A Python file that defines a Flask web application that to handle requests from clients
~~~

## Using the SQLAlchemy ORM

Object Relational Mappers (ORM's) map classes to tables, class instances to rows, and class methods to transactions on the rows of a table. The `sqlalchemy` package includes some base classes and methods that you can use to connect to your database's server from a Python application, then map tables in that database to Python classes. In this tutorial, we'll use SQLAlchemy's [Declarative](https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/) extension, which is built on the `mapper()` and `Table` functions.

### Connecting to CockroachDB with SQLAlchemy

Let's start by using SQLAlchemy to create an interface that connects the application to the running CockroachDB cluster.

If you haven't already, create a file named `movr.py`. This file defines the `MovR` class, which handles connections to CockroachDB using SQLAlchemy's `Engine` and `Session` classes. At the top of this file, import `create_engine` and `sessionmaker` from the `sqlalchemy` library. To handle requests to the server as transactions to the database, we then define `__enter__` and `__exit__` functions, in addition to the common `__init__` constructor.

~~~ python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class MovR:

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()

    def __init__(self, conn_string, init_tables = False, echo = False):


        self.engine = create_engine(conn_string, convert_unicode=True, echo=echo)


        if init_tables:
            logging.info("Initializing tables")
            Base.metadata.drop_all(bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
            logging.debug("Tables dropped and created")

        self.session = sessionmaker(bind=self.engine)()
~~~

When called, the constructor creates an instance of the `Engine` class using an input connection string that specifies the database dialect and connection arguments. The constructor then creates a `Session` object that binds to the active `Engine` object. The `__enter__` function simply returns the object itself, so, after the class is initialized, `MovR` attributes and methods can access the session. The `__exit__` function closes any active engine sessions.

For now, we've only imported `create_engine` and `sessionmaker`, as these are the two functions required to construct the database connection in our application. After we map the tables in the `movr` database to classes, we can import and use those in order to create methods that map to transactions.

### Mapping tables to classes

By now you should be familiar with your CockroachDB cluster, the `movr` database, and each of the tables in the database.

If you haven't done so already, create a file named `models.py`. This file contains the class definitions that map to tables in the `movr` database. Import `declarative_base`, SQLALchemy's base table class, built on the Declarative extension. You also need to import some other standard SQLAlchemy classes that represent database objects (like columns and indexes), data types, and constraints.

~~~ python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Index, String, DateTime, Integer, Float, \
    PrimaryKeyConstraint, ForeignKeyConstraint, CheckConstraint
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.postgresql import UUID, JSONB

Base = declarative_base()
~~~

You can now start defining the table classes from `Base`. Recall that each instance of a table class represents a row in the table, so let's name our table classes as if they were individual rows of their parent table, since that's what they'll become when called. Let's start with `User`:

~~~ python
class User(Base):
    __tablename__ = 'users'
    id = Column(UUID, primary_key=True)
    city = Column(String, primary_key=True)
    name = Column(String)
    address = Column(String)
    credit_card = Column(String)

    def __repr__(self):
        return "<User(city='%s', id='%s', name='%s')>" % (self.city, self.id, self.name)
~~~

We've defined the `User` class to contain the following attributes: 

- `__tablename__`, which holds the stored name of the table in the database. SQLAlchemy requires this attribute for all classes that map to tables.
- `id`, `city`, `name`, `address`, and `credit_card`, all of which are stored as `Column` objects that represent columns in a database table. The constructor for each `Column` takes the column data type as its argument. To help define column objects, SQLAlchemy also includes some classes that correspond to SQL data types. For the columns in this table, we just use `UUID` and `String`.

After you define the `User` table class, you can go ahead and define classes for the rest of the tables in the `movr` database.

### Defining APIs as transactions

After you create a class for each table in the database, you can start defining some functions that bundle together common SQL operations as transactions. These transaction functions will make up the API resources that the front-end will interface with.

#### Querying

Let's start with some basic read transactions. A very common query that a client might want to run is to read the `vehicles` table.

#### Inserting

Let's move on to some the slightly more advanced write transactions. A good place to start would be writes to the `rides` table.

## Building a web application with Flask

By now you should have an idea of what components we need to connect to a running database, map our database objects to objects in Python, and then interact with the database transactionally. Let's actually build out the web application that can do this for us.

### Configuring the server environment

Flask offers some pretty robust configuration options, and you can take several different approaches to setting those options. Let's use configuration classes to define different configurations that we want to use (and reuse when making new ones!). 

Make a file named `config.py`, and then define the configuration classes as simple data-storing `object`s. We can use the `os` library to pull security-sensitive information (like the `SECRET_KEY` Flask variable) into these.

~~~ python
# This file defines classes for flask configuration
import os

class Config(object):
    DEBUG = True
    TESTING = True
    ENV = 'development'
    SECRET_KEY = os.urandom(16)
    DB_HOST = 'localhost'
    DB_PORT = 26257
    DB_USER = 'root'
    DATABASE_URI= 'cockroachdb://{}@{}:{}/movr'.format(DB_USER, DB_HOST, DB_PORT)

class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ['SECRET_KEY']
    DB_HOST = os.environ['DB_SERVER']
    DB_PORT = os.environ['DB_PORT']
    DB_USER = os.environ['DB_USER']
    DATABASE_URI= 'cockroachdb://{}@{}:{}/movr'.format(DB_USER, DB_HOST, DB_PORT)

class DevConfig(Config):
    SECRET_KEY = os.environ['SECRET_KEY']
    DB_HOST = os.environ['DB_SERVER']
    DB_PORT = os.environ['DB_PORT']
    DB_USER = os.environ['DB_USER']
    DATABASE_URI= 'cockroachdb://{}@{}:{}/movr'.format(DB_USER, DB_HOST, DB_PORT)
~~~

### Routing


