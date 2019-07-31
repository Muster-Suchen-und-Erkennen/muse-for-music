from invoke import task, context
from dotenv import load_dotenv
from os import environ
from shutil import rmtree
from pathlib import Path

load_dotenv()

MODULE_NAME = 'muse_for_music'

SHELL = environ.get('SHELL', 'bash')

BUILD_FOLDER = Path('./{module}/build'.format(module=MODULE_NAME))
MANIFEST_PATH = BUILD_FOLDER / Path('manifest.json')

@task
def test_for_existing_manifest_file(c):
    """Check if a manifest.json file exists and if not builds it."""
    print(MANIFEST_PATH, MANIFEST_PATH.exists())
    if not (MANIFEST_PATH.exists() and MANIFEST_PATH.is_file()):
        build(c)

@task
def clean_js_dependencies(c):
    print('Removing node_modules folder.')
    rmtree(Path('./{module}/node_modules'.format(module=MODULE_NAME)))


@task
def dependencies_py(c, production=False):
    if production:
        c.run('pipenv install --deploy', shell=SHELL)
    else:
        c.run('pipenv install', shell=SHELL)


@task
def dependencies_js(c, clean_dependencies=False):
    if clean_dependencies:
        clean_js_dependencies(c)
    with c.cd('./{module}'.format(module=MODULE_NAME)):
        c.run('npm install', shell=SHELL)


@task(dependencies_py, dependencies_js)
def dependencies(c):
    pass


@task(dependencies_js)
def build(c):
    if not BUILD_FOLDER.exists():
        BUILD_FOLDER.mkdir()
    with c.cd('./{module}'.format(module=MODULE_NAME)):
        c.run('npm run build', shell=SHELL)


@task(test_for_existing_manifest_file)
def create_test_db(c):
    c.run('flask create_populated_db', shell=SHELL, pty=True)
    c.run('flask init_taxonomies taxonomies', shell=SHELL, pty=True)

@task
def start_js(c):
    with c.cd('./{module}'.format(module=MODULE_NAME)):
        c.run('npm run start', shell=SHELL, pty=True)


@task(test_for_existing_manifest_file)
def start_py(c, with_db=False):
    if with_db:
        create_test_db(c)
    c.run('flask run', shell=SHELL, pty=True)
