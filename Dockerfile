# docker build -t seal-reconciliation .
# docker run -p 8080:8080 -v "local/path/to/data:/app/data" --env PROPERTIES_FILE=/app/data/server.properties --env ENCRYPTION_KEY=sessiondatabasenecryptionkey --name seal-reconciliation seal-reconciliation:latest

FROM python:latest

MAINTAINER Universitat Jaume I
LABEL Author="Francisco Aragó"
LABEL E-mail="farago@uji.es"
LABEL version="0.0.1a"

ENV PROPERTIES_FILE "server.properties"
ENV ENCRYPTION_KEY "sessiondatabasenecryptionkey"

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


EXPOSE 8080

# For debug, run with flask
#CMD flask run --host=0.0.0.0

# Production

# To run with SSL
#CMD gunicorn -w 4 -b 0.0.0.0:8080 --certfile=server.crt --keyfile=server.key app:app

# To run without SSL
CMD gunicorn -w 4 -b 0.0.0.0:8080 app:app
