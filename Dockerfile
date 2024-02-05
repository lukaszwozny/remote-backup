FROM python:3.9.18-alpine3.19

RUN apk update
RUN apk add --no-cache postgresql-client

COPY requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /app
COPY . .

RUN mkdir logs
RUN mkdir backups

COPY cronjobs /etc/crontabs/root

ARG PGPASSWORD
ENV PGPASSWORD=${PGPASSWORD}

CMD ["crond", "-f", "-d", "8"]
