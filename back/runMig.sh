#!/bin/bash
. env/bin/activate
python manage.py makemigrations
python manage.py makemigrations api
python manage.py migrate
python manage.py runserver
