import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

User = get_user_model()

superuser_username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
superuser_email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
superuser_password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if not User.objects.filter(username=superuser_username).exists():
    User.objects.create_superuser(username=superuser_username, email=superuser_email, password=superuser_password)
    print(f"Superuser '{superuser_username}' created.")
else:
    print(f"Superuser '{superuser_username}' already exists.")

staff_username = os.environ.get("DJANGO_STAFF_USERNAME")
staff_password = os.environ.get("DJANGO_STAFF_PASSWORD")

if staff_username and staff_password:
    if not User.objects.filter(username=staff_username).exists():
        User.objects.create_user(username=staff_username, password=staff_password, is_staff=True)
        print(f"Staff user '{staff_username}' created.")
    else:
        print(f"Staff user '{staff_username}' already exists.")
else:
    print("Skipping staff user creation: DJANGO_STAFF_USERNAME or DJANGO_STAFF_PASSWORD not set.")


normal_username = os.environ.get("DJANGO_NORMAL_USERNAME")
normal_password = os.environ.get("DJANGO_NORMAL_PASSWORD")

if normal_username and normal_password:
    if not User.objects.filter(username=normal_username).exists():
        User.objects.create_user(username=normal_username, password=normal_password)
        print(f"Regular user '{normal_username}' created.")
    else:
        print(f"Regular user '{normal_username}' already exists.")
else:
    print("Skipping regular user creation: DJANGO_NORMAL_USERNAME or DJANGO_NORMAL_PASSWORD not set.")
