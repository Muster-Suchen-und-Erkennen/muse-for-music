FROM node:latest as builder

COPY . /

# build ui
RUN cd muse_for_music \
    && npm install \
    && npm run build

# cleanup ui source
RUN rm -rf /muse_for_music/src
RUN rm -rf /muse_for_music/e2e
RUN rm -rf /muse_for_music/node_modules
RUN rm /muse_for_music/.angular-cli.json
RUN rm /muse_for_music/karma.conf.js
RUN rm /muse_for_music/protractor.conf.js
RUN rm /muse_for_music/tsconfig.json
RUN rm /muse_for_music/tslint.json
RUN rm /muse_for_music/webpack.config.js
RUN rm /muse_for_music/package.json
RUN rm /muse_for_music/package-lock.json



FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY --from=builder ./muse_for_music /app/muse_for_music
COPY --from=builder ./taxonomies /app/taxonomies
COPY --from=builder ./uwsgi.ini /app/uwsgi.ini
COPY --from=builder ./requirements.txt /app/requirements.txt

ENV FLASK_APP muse_for_music
ENV MODE debug
ENV STATIC_URL /assets
ENV STATIC_PATH /app/muse_for_music/build

WORKDIR /app
RUN pip install -r requirements.txt
