#!/bin/bash
# rebuilds and repopulates the database for aurora on unchained

# stop uwsgi so we don't get any activity while we work
sudo service uwsgi stop

# dump current state, we might need it
sudo -u postgres pg_dump aurora > ~/aurora_$(date +%F-%H%M).psql

# drop current database
sudo -u postgres dropdb aurora

# create new database
sudo -u postgres createdb --owner=aurora_dbuser aurora

# create db schema
../../envs/aurora/bin/python manage.py syncdb

# populate demo data
../../envs/aurora/bin/python manage.py populate_demo_data

# collect static
../../envs/aurora/bin/python manage.py collectstatic

# restart uwsgi and nginx
sudo service uwsgi start
sudo service nginx restart
