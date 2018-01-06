#!/bin/bash

. venv/bin/activate
export FLASK_APP=muse_for_music
export FLASK_DEBUG=1  # to enable autoreload
export MODE=debug

# create and init debug db:
flask create_populated_db

# load taxonomies:
flask init_taxonomies taxonomies

# start server
flask run
