#!/bin/bash
cd ../frontend
npm install
npm run build

cd ../backend
python -m venv env
. env/bin/activate
pip install -r requirements.txt

rm -rf static
./manage.py collectstatic
rm -rf static/admin
rm -rf static/rest_framework

python manage.py makemigrations
python manage.py migrate
