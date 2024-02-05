docker-compsoe.yml

```yml
version: "3.9"

services:
  db:
    restart: always
    image: postgres
    volumes:
      - data-postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres

  backup:
    restart: always
    build:
      context: https://github.com/lukaszwozny/remote-backup.git
      args:
        PGPASSWORD: ${POSTGRES_PASSWORD}
    environment:
      - DB_WEIGHT=1
      - MEDIA_WEIGHT=10
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - MEGA_ENABLE=true
      - MEGA_USERNAME=mail@gmail.com
      - MEGA_PASSWORD=mega-password
      - DOMAIN=mywebsite.com
    volumes:
      - ./volumes/logs:/app/logs
      - ./volumes/backups:/app/backups
      - ./volumes/media:/app/volumes/media
    depends_on:
      - db

volumes:
  data-postgres:
```

## Using .env file

docker-compsoe.yml

```yml
version: "3.9"

services:
  db:
    restart: always
    image: postgres
    volumes:
      - data-postgres:/var/lib/postgresql/data
    env_file:
      - ./.env

  backup:
    restart: always
    build:
      context: https://github.com/lukaszwozny/remote-backup.git
      args:
        PGPASSWORD: ${POSTGRES_PASSWORD}
    env_file:
      - ./.env
    volumes:
      - ./volumes/logs:/app/logs
      - ./volumes/backups:/app/backups
      - ./volumes/media:/app/volumes/media
    depends_on:
      - db

volumes:
  data-postgres:
```
