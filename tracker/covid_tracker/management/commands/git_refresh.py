import git
import json

from django.http import JsonResponse
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass
        # parser.add_argument('-mycommand', nargs='?', type=str, default=None)

    def handle(self, *args, **options):

        try:
            g = git.cmd.Git('covid_tracker/COVID-19')
            rv = g.pull()
        except Exception as e:
            rv = {'response': "Git sync in process..."}

        print(rv)
