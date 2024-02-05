FROM python:3.9.18-alpine3.19

RUN apk update
#RUN apk add --no-cache openssh
RUN apk add --no-cache postgresql-client

COPY requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /app
COPY . .

RUN mkdir /logs
RUN mkdir /backups

# copy crontabs for root user
COPY cronjobs /etc/crontabs/root

ARG PGPASSWORD
ENV PGPASSWORD=${PGPASSWORD}

# start crond with log level 8 in foreground, output to stderr
CMD ["crond", "-f", "-d", "8"]
