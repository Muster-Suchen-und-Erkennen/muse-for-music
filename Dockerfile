FROM node:14-buster as builder

RUN apt-get update || : && apt-get install python3 python3-pip -y

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="${PATH}:/root/.poetry/bin"
ENV SHELL="/bin/bash"

COPY ./ /app
WORKDIR /app

ENV FLASK_APP=muse_for_music
ENV FLASK_DEBUG=1
ENV MODE=debug

RUN poetry install
RUN poetry run invoke create-test-db

CMD poetry run invoke start-js & poetry run flask run --host=0.0.0.0
