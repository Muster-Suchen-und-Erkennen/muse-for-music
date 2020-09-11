from invoke import task, context
from dotenv import load_dotenv
from os import environ, urandom
from shutil import rmtree
from pathlib import Path
from textwrap import dedent

load_dotenv()

MODULE_NAME = 'muse_for_music'

SHELL = environ.get('SHELL', 'bash')

INSTANCE_FOLDER = Path('./instance')
CONFIG_PATH = INSTANCE_FOLDER / Path('{module}.conf'.format(module=MODULE_NAME))
BUILD_FOLDER = Path('./{module}/static'.format(module=MODULE_NAME))
MANIFEST_PATH = BUILD_FOLDER / Path('manifest.json')

@task
def clean(c):
    print('Removing ui build output.')
    if BUILD_FOLDER.exists():
        rmtree(BUILD_FOLDER)

@task
def clean_js_dependencies(c):
    print('Removing node_modules folder.')
    rmtree(Path('./{module}/node_modules'.format(module=MODULE_NAME)))


@task
def dependencies_py(c, from_lockfile=False):
    if from_lockfile:
        c.run('pipenv install --deploy', shell=SHELL)
    else:
        c.run('pipenv install', shell=SHELL)


@task
def dependencies_js(c, clean_dependencies=False, from_lockfile=False, unsafe_permissions=False):
    if clean_dependencies:
        clean_js_dependencies(c)
    with c.cd('./{module}'.format(module=MODULE_NAME)):
        cmd_flags = ' --unsafe-perm' if unsafe_permissions else ''
        if from_lockfile:
            c.run('npm ci' + cmd_flags, shell=SHELL)
        else:
            c.run('npm install' + cmd_flags, shell=SHELL)


@task(dependencies_py, dependencies_js)
def dependencies(c):
    pass


@task()
def before_build(c, clean_build=False):
    if clean_build:
        clean(c)
    if not BUILD_FOLDER.exists():
        BUILD_FOLDER.mkdir()


@task(dependencies, before_build)
def build(c, production=False, deploy_url='/static/', base_href='/'):
    c.run('flask digest clean', shell=SHELL)
    with c.cd('./{module}'.format(module=MODULE_NAME)):
        attrs = [
            '--',
            '--extract-css',
            "--deploy-url='{}'".format(deploy_url),
            "--base-href='{}'".format(base_href),
        ]
        if production:
            attrs.append('--prod')
        c.run('npm run build ' + ' '.join(attrs), shell=SHELL)
    c.run('flask digest compile', shell=SHELL)


@task()
def create_start_config(c):
    if not INSTANCE_FOLDER.exists():
        INSTANCE_FOLDER.mkdir(parents=True)

    if CONFIG_PATH.exists():
        print('Config already exists. It will not be overwritten.')
        return

    print('Writing new config to', CONFIG_PATH.absolute())

    secret = repr(urandom(32))

    with CONFIG_PATH.open(mode='w') as conf:
        conf.write(dedent('''\
            # Default config for MUSE4Music

            ### Security settings
            SECRET_KEY = {secret}
            JWT_SECRET_KEY = {secret}
            # See https://flask-jwt-extended.readthedocs.io/en/stable/options/
            # BCRYPT_HANDLE_LONG_PASSWORDS = True # Changing this will BREAK ALL EXISTING PASSWORDS!
            # BCRYPT_LOG_ROUNDS = 12

            ### SQLAlchemy Settings
            # SQLALCHEMY_DATABASE_URI = sqlite:////tmp/test.db
            # SQLALCHEMY_ECHO = True
            # See https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/

            ### Log settings
            # LOG_PATH = '/tmp'
            # LOG_FORMAT = '%(asctime)s [%(levelname)s] [%(name)-20s] %(message)s <%(module)s, %(funcName)s, %(lineno)s; %(pathname)s>'
            # AUTH_LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
        ''').format(secret=secret))


@task
def upgrade_db(c):
    current = c.run('flask db current', hide=True, warn=True, shell=SHELL)
    last_line = current.stdout.strip().split('\n')[-1]  # type: str
    db_exists = last_line.endswith('(head)')
    if db_exists:
        print('Upgrading existing db.')
    else:
        print('Creating a new db and loading inital data into the database.')
    c.run('flask db upgrade', shell=SHELL, pty=True)
    if not db_exists:
        print('Add standard admin user and load taxonomies.')
        fill_db(c)


@task(create_start_config, upgrade_db)
def before_docker_start(c):
    pass


@task
def fill_db(c):
    c.run('flask init_db', shell=SHELL, pty=True)
    c.run('flask init_taxonomies taxonomies', shell=SHELL, pty=True)


@task
def create_test_db(c):
    c.run('flask create_populated_db', shell=SHELL, pty=True)
    c.run('flask init_taxonomies taxonomies', shell=SHELL, pty=True)


@task(dependencies_js, before_build)
def start_js(c, deploy_url='/static/'):
    with c.cd('./{module}'.format(module=MODULE_NAME)):
        attrs = [
            '--',
            '--extract-css',
            "--deploy-url='{}'".format(deploy_url),
            "--watch",
        ]
        c.run('npm run build ' + ' '.join(attrs), shell=SHELL, pty=True)


@task
def start_py(c, with_db=False, autoreload=False):
    if with_db:
        create_test_db(c)
    if autoreload:
        c.run('FLASK_DEBUG=1 flask run', shell=SHELL, pty=True)
    else:
        c.run('flask run', shell=SHELL, pty=True)
