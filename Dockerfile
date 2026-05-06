# syntax=docker/dockerfile:1
FROM python:3.10-slim AS base

RUN apt-get clean \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends \
       python3-dev wget unzip build-essential libpq-dev \
       uwsgi-plugin-python3 gcc iputils-ping \
    && ln -fs /usr/share/zoneinfo/Europe/Athens /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*

FROM base AS builder
WORKDIR /install
COPY src/app/requirements.txt /requirements.txt
RUN pip install --upgrade pip \
    && pip3 install -r /requirements.txt --root /install/ \
       --prefer-binary --no-warn-script-location

FROM base
COPY --from=builder /install /install
COPY src/app /app

RUN cp -r /install/usr/local/bin/* /usr/local/bin/ \
    && cp -r /install/usr/local/lib/python3.10/site-packages/* \
             /usr/local/lib/python3.10/site-packages/

WORKDIR /app
EXPOSE 8000
ENTRYPOINT ["/bin/bash", "/app/entrypoint_prod.sh"]
