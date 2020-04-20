FROM python:3.8

ENV FLASK_ENV=development
ENV FLASK_APP=app.py

WORKDIR /
RUN pip install flask
COPY . /

CMD flask run --host=0.0.0.0
