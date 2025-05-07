#!/bin/bash

docker start oracle-xe
docker start redis

source venv/bin/activate

python manage.py runserver &
celery -A music_controller worker --loglevel=info &
celery -A music_controller beat --loglevel=info &

wait

