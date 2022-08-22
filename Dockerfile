FROM node:14-buster as builder
COPY ./muse_for_music_ui /muse_for_music_ui
RUN cd muse_for_music_ui \
    && npm install \
    && npm run build

FROM python:3.9

LABEL org.opencontainers.image.source="https://github.com/Muster-Suchen-und-Erkennen/muse-for-music"

RUN apt-get update || : && apt-get install bash -y
RUN apt-get upgrade -y

# install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="${PATH}:/root/.poetry/bin"

COPY ./migrations /app/migrations
COPY ./muse_for_music /app/muse_for_music
COPY ./taxonomies /app/taxonomies
COPY ./poetry.lock /app/poetry.lock
COPY ./pyproject.toml /app/pyproject.toml
COPY ./tasks.py /app/tasks.py
COPY ./README.md /app/README.md
COPY --from=builder ./muse_for_music/static /app/muse_for_music/static

ENV SHELL="/bin/bash"

WORKDIR /app

ENV FLASK_APP muse_for_music
ENV MODE production

RUN poetry install --no-dev

EXPOSE 8000

# Wait for database
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.7.3/wait /wait
RUN chmod +x /wait

# TODO ensure that gunicorn runs with minimal rights in the container
CMD /wait && poetry run invoke before-docker-start && poetry run gunicorn -w 4 -b 0.0.0.0:8000 "muse_for_music:create_app()"
