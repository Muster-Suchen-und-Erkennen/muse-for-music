from os import environ, path
from logging import Formatter
from logging.handlers import RotatingFileHandler

from flask import Flask, logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_webpack import Webpack
from flask_cors import CORS, cross_origin


webpack = Webpack()  # type: Webpack


# Setup Config

app = Flask(__name__, instance_relative_config=True)  # type: Flask
app.config['MODE'] = environ['MODE'].upper()
if app.config['MODE'] == 'PRODUCTION':
    app.config.from_object('muse_for_music.config.ProductionConfig')
elif app.config['MODE'] == 'DEBUG':
    app.config.from_object('muse_for_music.config.DebugConfig')
elif app.config['MODE'] == 'TEST':
    app.config.from_object('muse_for_music.config.TestingConfig')

app.config.from_pyfile('/etc/muse_for_music.conf', silent=True)
app.config.from_pyfile('muse_for_music.conf', silent=True)

# TODO use nevironment variables
for env_var in ('SQLALCHEMY_DATABASE_URI', 'JWT_SECRET_KEY', 'LOG_PATH'):
    app.config[env_var] = environ.get(env_var, app.config.get(env_var))


formatter = Formatter(fmt=app.config['LOG_FORMAT'])

fh = RotatingFileHandler(path.join(app.config['LOG_PATH'], 'muse4music.log'),
                         maxBytes=104857600, backupCount=10)

fh.setFormatter(formatter)

app.logger.addHandler(fh)

app.logger.info('Connecting to database %s.', app.config['SQLALCHEMY_DATABASE_URI'])


# Setup DB and bcrypt
db = SQLAlchemy(app)  # type: SQLAlchemy
migrate = Migrate(app, db)  # type: Migrate
bcrypt = Bcrypt(app)  # type: Bcrypt

# Setup JWT
jwt = JWTManager(app)  # type: JWTManager

# Setup Headers
CORS(app)


webpack.init_app(app)


from . import models

from . import routes
