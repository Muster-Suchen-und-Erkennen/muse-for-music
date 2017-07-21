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
flask crate_populated_db
flask init_taxonomies taxonomies
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

