# docker build -t seal-reconciliation .
# docker run -p 8050:8050 -v "local/path/to/data:/app/data" --env PROPERTIES_FILE=/app/data/server.properties --env ENCRYPTION_KEY=sessiondatabasenecryptionkey --name seal-reconciliation seal-reconciliation:latest

FROM python:latest

MAINTAINER Universitat Jaume I
LABEL Author="Francisco Aragó"
LABEL E-mail="farago@uji.es"
LABEL version="0.0.1e"

ENV PROPERTIES_FILE "server.properties"
ENV ENCRYPTION_KEY "sessiondatabasenecryptionkey"
ENV MSPORT 8050
ENV WTHREADS 4

# Prevent generating .pyc files # TODO: allow pyc?
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV FLASK_APP "app.py"
# ENV FLASK_ENV "development"
# ENV FLASK_DEBUG True

RUN mkdir /app
WORKDIR /app

COPY . /app/

RUN pip install --upgrade pip && \
    #pip install pipenv && \
    #pipenv install --dev --system --deploy -r requirements.txt
    pip install -r requirements.txt

# TODO: Make sure this is not copied on the image: remove the key file and see if it fails, and then works when specifying the container voluem
VOLUME ./data /app/data


EXPOSE $MSPORT

# For debug, run with flask
#CMD flask run --host=0.0.0.0

# Production

# To run with SSL
CMD gunicorn -w 4 -b 0.0.0.0:8050 --certfile=/app/data/ssl_cert.pem --keyfile=/app/data/ssl_cert.key app:app

# To run without SSL
#CMD gunicorn -w $WTHREADS -b 0.0.0.0:$MSPORT app:app
