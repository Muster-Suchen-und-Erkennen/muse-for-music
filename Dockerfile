FROM node:16-buster as builder
COPY ./muse_for_music_ui /muse_for_music_ui
RUN cd muse_for_music_ui \
    && npm clean-install \
    && npm run build -- --configuration production --output-hashing=none --extract-licenses

FROM python:3.9

LABEL org.opencontainers.image.source="https://github.com/Muster-Suchen-und-Erkennen/muse-for-music"

# install bash and remove caches again in same layer
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends bash && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN useradd gunicorn

ENV SHELL="/bin/bash"

WORKDIR /app

ENV FLASK_APP muse_for_music
ENV MODE production

# make directories and set user rights
RUN mkdir --parents /app/instance \
    && chown --recursive gunicorn /app && chmod --recursive u+rw /app/instance

# Wait for database
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait

RUN python -m pip install poetry gunicorn

COPY --chown=gunicorn ./migrations /app/migrations
COPY --chown=gunicorn ./muse_for_music /app/muse_for_music
COPY --chown=gunicorn ./taxonomies /app/taxonomies
COPY --chown=gunicorn ./poetry.lock ./pyproject.toml ./tasks.py ./README.md /app/
COPY --chown=gunicorn --from=builder ./muse_for_music/static /app/muse_for_music/static

RUN ls -lah && python -m poetry export --without-hashes --format=requirements.txt -o requirements.txt && echo ".\n" >> requirements.txt && python -m pip install -r requirements.txt

VOLUME ["/app/instance"]

ENV INSTANCE_PATH="/app/instance"
ENV WORKERS=4

EXPOSE 8000

USER gunicorn

CMD /wait && cd /app && python -m invoke before-docker-start && python -m gunicorn -w $WORKERS -b 0.0.0.0:8000 "muse_for_music:create_app()"
