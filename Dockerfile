FROM python:3.9.18-alpine3.19

RUN apk update
RUN apk add --no-cache postgresql-client

COPY requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /app
COPY . .

RUN mkdir logs
RUN mkdir backups

ARG PGPASSWORD
ENV PGPASSWORD=${PGPASSWORD}

ARG CRON_SCHEDULE
ENV CRON_SCHEDULE=${CRON_SCHEDULE}
RUN echo -e "$CRON_SCHEDULE python /app/main.py >> /app/logs/remote_bakup.log 2>&1\n" > /etc/crontabs/root

CMD ["crond", "-f", "-d", "8"]
