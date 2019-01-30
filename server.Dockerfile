from python:3.6.8

WORKDIR /usr/src

RUN pip install --upgrade pip

RUN pip install --no-cache-dir flask
RUN pip install --no-cache-dir gunicorn
RUN pip install --no-cache-dir lxml
RUN pip install --no-cache-dir pycrypto
RUN pip install --no-cache-dir psycopg2
RUN pip install --no-cache-dir requests
RUN pip install --no-cache-dir python-dateutil

COPY ./server /usr/src

RUN python -c 'import RSA; RSA.BuildKey()'

#ENV FLASK_RUN app.py

# CMD ["pip", "list"]
#CMD ["flask", "run"]
#CMD "ls"

CMD ["gunicorn", "-w 4", "-b 127.0.0.1:5000", "app:app"]
