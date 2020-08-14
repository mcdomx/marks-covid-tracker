import git
import json

from django.http import JsonResponse
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Trigger a git pull on the COVID dataset. Can be called via `python manage.py git_refresh`. No arguments are supported with this command.
    """
    # def add_arguments(self, parser):
    #     pass
    #     # parser.add_argument('-mycommand', nargs='?', type=str, default=None)

    def handle(self, *args, **options):
        """
        Called by invoking the command class with `python manage.py git_refresh`.
        """
        try:
            g = git.cmd.Git('covid_tracker/COVID-19')
            rv = g.pull()
        except Exception as e:
            rv = {'response': "Git sync in process..."}

        print(rv)
