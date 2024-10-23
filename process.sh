#!/bin/bash

. ~/.venv/main/bin/activate
cd ~/main
export DJANGO_SETTINGS_MODULE=www.settings
./manage.py reviews_import
./manage.py reviews_approve
./manage.py reviews_generate
./manage.py reviews_review
./manage.py reviews_reply
