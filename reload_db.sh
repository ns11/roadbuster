#!/bin/bash
[ -e project.db ] && rm project.db 
./manage.py migrate
./manage.py bootstrap
./manage.py collectstatic
./manage.py runserver
