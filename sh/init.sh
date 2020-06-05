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

# python vue2djangoTemplate.py (자동화 - 작성예정, 어캐함??ㅠ)

# 현재 vue index를 django template으로 자동화 하는 코드를 작성하지 못하여,
# 수동으로 바꿔야 합니다.
# 이 스크립트를 실행 후에 생기는 static/index.html의 
# href, src 링크를 templates/index.html의 href, src로 변경하면 정상적으로 작동합니다.