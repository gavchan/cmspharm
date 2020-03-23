# Django-Postgres-Docker Template

Basic Django-Postgres template for Development using Docker

After pulling the repository, need to create two files in the `./backend` directory:

1. `dj_secret.key`: Django Secret Key File
2. `pg_settings.env`: Postgres Database Password

These will be used by to set up Django and Postgres during initialization.

To use: `docker-compose up`

Next run bash shell into backend while container is running:
```
docker-compose exec backend /bin/bash
```
After getting a bash shell in the container-service, migrate the database and create a superuser/password:
```
python manage.py migrate
python manage.py createsuperuser
```
