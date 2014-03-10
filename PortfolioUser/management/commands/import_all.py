from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Populates database with demo data'

    def handle(self, *args, **options):
        import_all()


def import_all():
    print("import all")
    call_command('import_courses')
    call_command('import_tutors')
    call_command('import_students')