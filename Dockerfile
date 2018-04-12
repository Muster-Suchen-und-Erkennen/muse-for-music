
FROM tiangolo/uwsgi-nginx-flask:python3.6

COPY ./muse_for_music /app/muse_for_music
COPY ./taxonomies /app/taxonomies
COPY ./uwsgi.ini /app/uwsgi.ini
COPY ./requirements.txt /app/requirements.txt
COPY ./setup.py /app/setup.py
COPY ./muse_for_music/build /app/muse_for_music/build

ENV FLASK_APP muse_for_music
ENV MODE debug
ENV STATIC_URL /assets
ENV STATIC_PATH /app/muse_for_music/build

WORKDIR /app
RUN pip install -r requirements.txt
