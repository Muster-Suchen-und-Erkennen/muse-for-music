FROM node:14-buster as builder

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN apt-get update || : && apt-get install python3 python3-pip -y

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install pipenv

COPY . /app

WORKDIR /app

RUN pipenv install
#RUN python3 -m pip install -r requirements.txt
#RUN pipenv install --system -v

ENV FLASK_APP muse_for_music
ENV MODE production

# build ui
RUN pipenv run build

# switch to stage 2 dockerignore to ignore angular app sources
RUN ls -lah /app/
RUN mv /app/stage2.dockerignore /app/.dockerignore


FROM python:3.8

RUN apt-get update || : && apt-get install bash -y
RUN apt-get upgrade -y

RUN python -m pip install --upgrade pip
RUN python -m pip install pipenv


# TODO speed up copy process (nested dockerignore seems not to work...)
COPY --from=builder ./app/muse_for_music /app/muse_for_music
COPY --from=builder ./app/migrations /app/migrations
COPY --from=builder ./app/taxonomies /app/taxonomies
COPY --from=builder ./app/Pipfile /app/Pipfile
COPY --from=builder ./app/setup* /app/
COPY --from=builder ./app/tasks.py /app/tasks.py
COPY --from=builder ./app/requirements-docker.txt /app/requirements-docker.txt

WORKDIR /app

RUN pipenv lock
RUN pipenv install --system --deploy
RUN python -m pip install -r requirements-docker.txt

ENV FLASK_APP muse_for_music
ENV MODE production
ENV SHELL /bin/bash

EXPOSE 8000

# TODO ensure that gunicorn runs with minimal rights in the container

CMD pipenv run invoke before-docker-start && gunicorn -w 4 -b 0.0.0.0:8000 'muse_for_music:create_app()'
