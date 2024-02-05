FROM python:3.9.18-alpine3.19

COPY requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /app
COPY . .

RUN mkdir /logs

# copy crontabs for root user
COPY cronjobs /etc/crontabs/root

# start crond with log level 8 in foreground, output to stderr
CMD ["crond", "-f", "-d", "8"]
