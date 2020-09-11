# MUSE4Music


## First start:

This project uses pipenv and npm to manage all dependencies. You must install pipenv and npm first before running any script.

Create a `.env` file with the following content:

```bash
FLASK_APP=muse_for_music
FLASK_DEBUG=1  # to enable autoreload
MODE=debug
```

Backend:
```shell
pipenv install

# create the test database
pipenv run create-test-db
```


## start server:

Start the build process for the frontend:
```shell
pipenv run start-js
```

Start the flask dev server
```shell
pipenv run start
```

Drop and recreate DB:
```shell
pipenv run drop-db
pipenv run create-test-db
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

The migrations can be run with pipenv.

Commands:
```shell
# create new migration after model changes:
pipenv run create-migration

# update db to newest migration:
pipenv run upgrade-db
```

After creating a new migration file with `pipenv run create-migration` it is neccessary to manually check the generated upgrade script. Please refer to the [alembic documentation](alembic.zzzcomputing.com/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).


## Install:

Prerequisites:

 *  Python >3.5, Virtualenv, Pip
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
 *  Check Python version (>3.5!)
