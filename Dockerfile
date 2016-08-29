FROM python:3.5-alpine

# adding code
WORKDIR /app/prom-exporter
ADD requirements.txt /app/prom-exporter

# install
RUN apk add --update openssl bash \
    && apk --update add --no-cache --virtual build-dependencies libc-dev autoconf gcc \
    && pip install --no-cache-dir -r requirements.txt \
    \ 
    && rm -rf ~/.cache \
    && apk del build-dependencies

ADD . /app/prom-exporter
RUN python3 setup.py install

EXPOSE 9191
ENTRYPOINT ["finagle-exporter"]
