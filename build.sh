#!/usr/bin/env bash
# exit on error
set -o errexit

npm install

npm run start

pip install -r requirements.txt

python manage.py collectstatic --no-input

python manage.py migrate

# create superuser if missing
cat <<EOF | python manage.py shell
import os
from django.contrib.auth import get_user_model

User = get_user_model()

User.objects.filter(username=os.environ["DJANGO_SUPERUSER_USERNAME"]).exists() or \
    User.objects.create_superuser(os.environ["DJANGO_SUPERUSER_USERNAME"], os.environ["DJANGO_SUPERUSER_EMAIL"], os.environ["DJANGO_SUPERUSER_PASSWORD"])
EOF