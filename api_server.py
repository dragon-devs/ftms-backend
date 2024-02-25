# api_server.py
import os
from django.core.management import execute_from_command_line

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "football_tournaments_management_system.settings")


def run_api_server():
    execute_from_command_line(["manage.py", "runserver"])


if __name__ == "__main__":
    run_api_server()
