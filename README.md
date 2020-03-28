# cmsMan: CMS Manager

Add-on to support legacy CMS app

Three files need to be created in the `./backend` directory:

1. `dj_secret.key`: Django Secret Key File
2. `pg_settings.env`: POSTGRES_PASSWORD=*password*
3. `cms.key`: MySQL database password to access legacy CMS App db

To use: `docker-compose up`

To initialize:
```
docker-compose exec backend /bin/bash
```
Migrate the database and create a superuser/password:
```
python manage.py migrate
python manage.py createsuperuser
```
