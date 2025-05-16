# MUSE4Music
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Docker

A docker image is built automatically. Docker images can be found under [Packages](https://github.com/orgs/Muster-Suchen-und-Erkennen/packages?repo_name=muse-for-music).

## First start:

This project uses poetry and npm to manage all dependencies. You must install poetry and npm first before running any script.

NOTE: Windows does not support the 'pty' module so `invoke` commandos fail at windows. If you use windows, you need to install WSL2 and set up a Linux distribution. Then you must install python, poetry and npm on your WSL Remote to run the following commandos.

After cloning the repository, you need to check out the remote `dev` branch:
```shell
git checkout dev
```

Create a `.env` file with the following content:

```bash
FLASK_APP=muse_for_music
FLASK_DEBUG=1  # to enable autoreload
MODE=debug
```

Backend:
```shell
poetry install

# create the test database
poetry run invoke create-test-db
```


## start server:

Start the build process for the frontend:
```shell
poetry run invoke start-js
```

Start the flask dev server
```shell
# create test db before first run!

# start flask server
poetry run invoke start-py --autoreload
```

Drop and recreate DB for local development:
```shell
poetry run flask drop_db
poetry run invoke create-test-db
```

## Set admin password

```shell
poetry run flask set-user-password --username admin
```

or inside the Docker container:

```shell
python -m flask set-user-password --username admin
```


## Docker
You can also build and run the project in Docker. Under windows you also need WSL2 for that. You need to have a working docker and run the following commandos:
```shell
docker build -t m4m .
docker run -it -p8000:8000 m4m
```

## Sites:

The following sites are available after starting the flask development server:

[Web-App](http://127.0.0.1:5000/)
[User API](http://127.0.0.1:5000/users/doc)
[API](http://127.0.0.1:5000/api/doc)

Only in debug mode:
[debug](http://127.0.0.1:5000/debug)



## Update DB Migrations:

The migrations use [Flask-Migrate](flask-migrate.readthedocs.io/en/latest/).

The migrations can be run with poetry.

Commands:
```shell
# create new migration after model changes:
poetry run flask db migrate

# update db to newest migration:
poetry run flask db upgrade
```

After creating a new migration file with `poetry run flask db migrate` it is neccessary to manually check the generated upgrade script. Please refer to the [alembic documentation](alembic.zzzcomputing.com/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).

## Run Unit Tests:

```shell
# run all tests (WARNING this takes a long time!)
poetry run pytest tests

# run rule based hypothesis test
# the available hypothesis profiles can be found in tests/util.py
poetry run pytest --hypothesis-profile fast ./tests/rule_based_test.py::test_muse_for_music_api

# run tests with coverage
poetry run coverage run --source=muse_for_music --omit='*/debug_routes/*' -m pytest tests

# generate overage reports
poetry run coverage report -m
poetry run coverage html
```

## Install:

WARNING: Install script is currently broken!

Prerequisites:

 *  Python >3.6, Virtualenv, Pip
 *  npm, node >8
 *  Apache2, mod-wsgi or another wsgi compatible server

Installation / Upgrade process for installations using apache:

 1. Install Prerequisites
 2. Download/Clone Repository
 3. Copy `install.sh` to a different location outside of the repository
     1. Make it executable
     2. update the variables at the top of the script
 4. execute `install.sh`

For use with MySql or other db engine:

 1. Setup Database User and scheme
     1. For MySql/Mariadb use [utf8mb4 charset](dev.mysql.com/doc/refman/5.5/en/charset-unicode-utf8mb4.html)
 2. Install a [driver](docs.sqlalchemy.org/en/latest/dialects/mysql.html) for your selected Database in the virtualenv
 3. Update the [database url](docs.sqlalchemy.org/en/latest/core/engines.html#database-urls) in the config file
     1. For MySql/Mariadb use [utf8mb4 charset](docs.sqlalchemy.org/en/latest/dialects/mysql.html?highlight=utf8mb4#charset-selection)
 4. execute `install.sh` to generate database

Troubleshooting:

 *  Check all file permissions (use `install.sh` as reference)
 *  Check AppArmor/Selinux permissions
 *  Check apache logs
 *  Check apache config
 *  Check M4M logs
 *  Check Python version (>3.6!)
