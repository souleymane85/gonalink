import os

from django.contrib.auth import get_user_model
from django.db import OperationalError, ProgrammingError


def create_admin():
    User = get_user_model()

    username = os.environ.get("ADMIN_USERNAME")
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")

    if not all([username, email, password]):
        print("ADMIN_USERNAME, ADMIN_EMAIL ou ADMIN_PASSWORD manquant.")
        return

    try:
        if User.objects.filter(username=username).exists():
            print(f"Le compte admin '{username}' existe déjà.")
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        print(f"Superutilisateur '{user.username}' créé avec succès.")

    except (OperationalError, ProgrammingError) as e:
        print(f"Base de données indisponible : {e}")


if __name__ == "__main__":
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agromarket.settings")
    django.setup()

    create_admin()

