#!/bin/zsh

set -e

python manage.py wait_for_db
python manage.py migrate

uwasgi --socket :9000 --workers 4 --master --enable-threads --module app.wasgi