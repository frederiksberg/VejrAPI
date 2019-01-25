from python:3.6.8

WORKDIR /usr/src

RUN pip install --no-cache-dir flask
RUN pip install --no-cache-dir waitress
RUN pip install --no-cache-dir lxml

COPY ./server /usr/src

RUN python -c 'import RSA; RSA.BuildKey()'

CMD ["pip", "list"]
# CMD ["waitress-serve", "--call 'app:create_app'"]