"""Module containing default config values."""

from random import randint


class Config(object):
    DEBUG = False
    TESTING = False
    RESTPLUS_VALIDATE = True
    BCRYPT_HANDLE_LONG_PASSWORDS = True
    JWT_SECRET_KEY = ''.join(hex(randint(0, 255))[2:] for i in range(16))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WEBPACK_MANIFEST_PATH = './build/manifest.json'
    LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(name)-20s] %(message)s <%(module)s, \
                 %(funcName)s, %(lineno)s; %(pathname)s>'
    AUTH_LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'

    # Monitor request performance
    MONITOR_REQUEST_PERORMANCE = True
    LONG_REQUEST_THRESHHOLD = 1

    # for better json performance
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    RESTPLUS_JSON = {'indent': None}


class ProductionConfig(Config):
    pass


class DebugConfig(Config):
    DEBUG = True
    JWT_SECRET_KEY = 'debug'  # FIXME
    LOG_PATH = '/tmp'
    #SQLALCHEMY_ECHO = True
    LONG_REQUEST_THRESHHOLD = 0.5


class TestingConfig(Config):
    TESTING = True
    LOG_PATH = '/tmp'
