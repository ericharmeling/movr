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
