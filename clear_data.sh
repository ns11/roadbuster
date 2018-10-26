#!/bin/bash
rm project.db
./manage.py clear_index --noinput
cp project.db.empty project.db
./manage.py bootstrap
./manage.py runserver
