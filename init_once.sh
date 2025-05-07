#!/bin/bash

docker start oracle-xe
docker start redis

source venv/bin/activate

python manage.py create_periodic_task

