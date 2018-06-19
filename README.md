# MUSE4Music


## First start:

Backend:
```shell
# setup virtualenv
virtualenv venv
. venv/bin/activate


# install requirements
pip install -r requirements_developement.txt
pip install -r requirements.txt

pip install -e .
```

Frontend:

```shell
cd muse_for_music

npm install
```


## start server:

Start the webpack developement server:
```shell
cd muse_for_music
npm run start
```

First start:
```shell
. venv/bin/activate
export FLASK_APP=muse_for_music
export FLASK_DEBUG=1  # to enable autoreload
export MODE=debug
# export MODE=production
# export MODE=test

# create and init debug db:
flask create_populated_db

# load taxonomies:
flask init_taxonomies taxonomies

# start server
flask run
```

Subsequent starts:
```shell
flask run
```

Drop and recreate DB:
```shell
flask drop_db
flask create_populated_db
flask init_taxonomies taxonomies

# flask drop_db && flask create_populated_db && flask init_taxonomies taxonomies
```


Reload taxonomies:
```shell
flask init_taxonomies -r taxonomies
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

Commands:
```shell
# create new migration after model changes:
flask db migrate

# update db to newest migration:
flask db upgrade

# get help for db operations:
flask db --help
```

After creating a new migration file with `flask db migrate` it is neccessary to manually check the generated upgrade script. Please refer to the [alembic documentation](alembic.zzzcomputing.com/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect).


## Install:

Prerequisites:

 *  Python >3.5, Virtualenv, Pip
 *  npm, node >8
 *  Apache2, mod-wsgi

Installation / Upgrade process:

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
 *  Check TTF logs
 *  Check Python version (>3.5!)
