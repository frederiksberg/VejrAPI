#from python:3.6.8
FROM python:3.6.8-alpine3.8

WORKDIR /usr/src

# Gets purged
RUN apk add --no-cache --virtual .build-deps musl-dev postgresql-dev libc-dev gcc

# Doesn't get purged
RUN apk add --no-cache postgresql-libs libxslt-dev

RUN pip install --upgrade pip

RUN pip install --no-cache-dir flask
RUN pip install --no-cache-dir gunicorn
RUN pip install --no-cache-dir lxml
RUN pip install --no-cache-dir pycrypto
RUN pip install --no-cache-dir psycopg2
RUN pip install --no-cache-dir requests
RUN pip install --no-cache-dir python-dateutil
RUN pip install --no-cache-dir redis

RUN apk --purge del .build-deps

COPY ./server /usr/src

CMD ["gunicorn", "-w 4", "-b 0.0.0.0:5000", "app:app"]
