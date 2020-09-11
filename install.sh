#!/usr/bin/bash

SOURCE="/usr/src/muse-for-music"
PACKAGE=muse_for_music
NAME=muse-for-music
PYTHON=/usr/bin/python3
PIP="$PYTHON -m pip"
PIP_VENV="python -m pip"
PIPENV="python -m pipenv"
VENV="virtualenv --python=$PYTHON"
VENV_DIR=/usr/lib/
VENV_FOLDER=muse-for-music

CONFIG_FILE=/etc/${PACKAGE}.conf
LOG_PATH=/var/log/$NAME

HTTP_ROOT=/var/www
WSGI_FILE=${NAME}.wsgi

APACHE_CONFIG=/etc/apache2

#Asset deploy url
#DEPLOY_URL=./assets/

if [ ! -d $VENV_DIR ]; then
    mkdir $VENV_DIR
fi

pushd $VENV_DIR

if [ ! -d $VENV_FOLDER ]; then
    $VENV $VENV_FOLDER
fi

pushd $VENV_FOLDER

chmod a+x bin/activate*

# Activate venv, everything after is happening in venv!
source bin/activate

# Ensure that pipenv is installed
$PIP_VENV install --upgrade pipenv

popd
popd


pushd $SOURCE

MODE=production
FLASK_APP=$PACKAGE

$PIPENV run build --production --clean-build --unsafe-permissions

$PIPENV run upgrade-db

popd


pushd $HTTP_ROOT

if [ ! -f $WSGI_FILE ]; then
    echo "import sys" >> $WSGI_FILE
    echo "from os import environ" >> $WSGI_FILE
    echo "" >> $WSGI_FILE
    echo "activate_this = '$VENV_DIR$VENV_FOLDER/bin/activate_this.py'" >> $WSGI_FILE
    echo "with open(activate_this) as file_:" >> $WSGI_FILE
    echo "    exec(file_.read(), dict(__file__=activate_this))" >> $WSGI_FILE
    echo "" >> $WSGI_FILE
    echo "sys.path.insert(0, '$SOURCE')" >> $WSGI_FILE
    echo "environ['MODE'] = 'production'" >> $WSGI_FILE

    echo -n "environ['JWT_SECRET_KEY'] = '" >> $WSGI_FILE
    hexdump -n 32 -e '4/4 "%08X" 1 ""' /dev/urandom >> $WSGI_FILE
    echo "'" >> $WSGI_FILE

    echo "" >> $WSGI_FILE
    echo "from $PACKAGE import app as application" >> $WSGI_FILE
    echo "" >> $WSGI_FILE
fi

popd

if [ ! -f $CONFIG_FILE ]; then
    echo "SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/apache.db'" >> $CONFIG_FILE
    echo "LOG_PATH = '$LOG_PATH'" >> $CONFIG_FILE
fi

if [ ! -d $LOG_PATH ]; then
    mkdir $LOG_PATH
    chmod a+r+w $LOG_PATH
fi

pushd $APACHE_CONFIG

if [ ! -d sites-available ]; then
    mkdir sites-available
fi

pushd sites-available

if [ ! -f ${NAME}.conf ]; then
    echo "<VirtualHost *>" >> ${NAME}.conf
    echo "    ServerName example.com" >> ${NAME}.conf
    echo "    WSGIDaemonProcess $NAME processes=2 threads=15" >> ${NAME}.conf
    echo "    WSGIProcessGroup $NAME" >> ${NAME}.conf
    echo "    WSGIScriptAlias / $HTTP_ROOT/$WSGI_FILE" >> ${NAME}.conf
    echo "    WSGIPassAuthorization on" >> ${NAME}.conf
    echo "</VirtualHost>" >> ${NAME}.conf
fi

popd

if [ ! -d sites-enabled ]; then
    mkdir sites-enabled
fi

if [ ! -f sites-enabled/${NAME}.conf ]; then
    ln -s sites-available/${NAME}.conf sites-enabled/${NAME}.conf
fi

popd

pushd $HTTP_ROOT
    touch $WSGI_FILE
popd
