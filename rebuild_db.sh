> database.db && echo no | python manage.py syncdb && python manage.py populate_demo_data
python manage.py collectstatic


### for Postgres ###

#rsync dude@unchained:/home/dude/aurora_backup_latest* ~

#cd
#gunzip aurora_backup_latest.db.psql.gz
#sed -i 's/_postgres/postgres/g' aurora_backup_*.db.psql
#sudo -u postgres sh -c "cat aurora_backup_*.db.psql | psql aurora"

#tar -xzf aurora_backup_latest.files.tar.gz
