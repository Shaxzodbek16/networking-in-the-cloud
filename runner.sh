#!/bin/bash

python manage.py makemigrations

sleep 1

python manage.py migrate

sleep 1

python manage.py ca

sleep 1

python manage.py feed_db

sleep 1

python manage.py runserver
