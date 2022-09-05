from os import environ, path, makedirs
from logging import Formatter
from logging.handlers import RotatingFileHandler
from secrets import token_urlsafe

from flask import Flask, logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.schema import MetaData
from sqlalchemy.engine import Engine
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_static_digest import FlaskStaticDigest
from flask_cors import CORS, cross_origin
from .reverse_proxy_fix import apply_reverse_proxy_fix
from pathlib import Path

from flask import g

db = None  # type: SQLAlchemy
db = SQLAlchemy(metadata=MetaData(naming_convention={
    'pk': 'pk_%(table_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(column_0_name)s',
}))

bcrypt = Bcrypt()  # type: Bcrypt

jwt = JWTManager()  # type: JWTManager


def apply_additional_db_config(app):
    if app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite://'):
        @event.listens_for(Engine, 'connect')
        def set_sqlite_pragma(dbapi_connection, connection_record):
            if app.config.get('SQLITE_FOREIGN_KEYS', True):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()


def create_app():
    FLASK_STATIC_DIGEST = FlaskStaticDigest()  # type: FlaskStaticDigest

    instance_path: str | None = environ.get("INSTANCE_PATH", None)
    if instance_path:
        if Path(instance_path).is_file():
            instance_path = None

    # Setup Config

    app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)  # type: Flask
    makedirs(app.instance_path, exist_ok=True)
    app.config['LOG_PATH'] = app.instance_path
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/test.db'.format(app.instance_path)
    app.config['MODE'] = environ['MODE'].upper()
    if app.config['MODE'] == 'PRODUCTION':
        app.config.from_object('muse_for_music.config.ProductionConfig')
    elif app.config['MODE'] == 'DEBUG':
        app.config.from_object('muse_for_music.config.DebugConfig')
    elif app.config['MODE'] == 'TEST':
        app.config.from_object('muse_for_music.config.TestingConfig')

    app.config.from_pyfile('/etc/muse_for_music.conf', silent=True)
    app.config.from_pyfile('muse_for_music.conf', silent=True)

    # TODO use environment variables
    for env_var in ('SQLALCHEMY_DATABASE_URI', 'JWT_SECRET_KEY', 'LOG_PATH', 'SQLITE_FOREIGN_KEYS'):
        app.config[env_var] = environ.get(env_var, app.config.get(env_var))

    reverse_proxy_count = environ.get('REVERSE_PROXY_COUNT', None)
    if reverse_proxy_count and reverse_proxy_count.isdigit():
        app.config['REVERSE_PROXY_COUNT'] = int(reverse_proxy_count)


    formatter = Formatter(fmt=app.config['LOG_FORMAT'])

    fileHandler = RotatingFileHandler(path.join(app.config['LOG_PATH'], 'muse4music.log'),
                            maxBytes=104857600, backupCount=10)

    fileHandler.setFormatter(formatter)

    app.logger.addHandler(fileHandler)

    app.logger.info('Connecting to database %s.', app.config['SQLALCHEMY_DATABASE_URI'])

    # apply reverse proxy fix
    apply_reverse_proxy_fix(app)

    # Setup DB and bcrypt
    db.init_app(app)
    apply_additional_db_config(app)
    migrate = Migrate(app, db)  # type: Migrate
    bcrypt.init_app(app)

    # Setup JWT
    jwt.init_app(app)

    # Setup Headers
    CORS(app)

    # Javascript stuff
    FLASK_STATIC_DIGEST.init_app(app)

    if app.config['DEBUG']:
        @app.template_filter('bustcache')
        def cache_busting_filter(url):
            return url + '?cache-bust={}'.format(token_urlsafe(16))
    else:
        @app.template_filter('bustcache')
        def cache_busting_filter(url):
            return url

    # Performance monitoring
    if app.config.get('MONITOR_REQUEST_PERFORMANCE', True):
        from .performance import register_performance_monitoring
        register_performance_monitoring(app)


    from . import models
    app.register_blueprint(models.DB_CLI)

    from .routes import register_routes
    register_routes(app, FLASK_STATIC_DIGEST)

    return app
