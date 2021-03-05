#!/bin/bash
while true; do
    python3 manage.py makemigrations account \--settings=adverts_collector.prod_settings
    python3 manage.py makemigrations adverts \--settings=adverts_collector.prod_settings
    python3 manage.py migrate \--settings=adverts_collector.prod_settings
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Init command failed, retrying in 5 secs...
    sleep 5
done
python3 manage.py runserver 0.0.0.0:8000 \--settings=adverts_collector.prod_settings
