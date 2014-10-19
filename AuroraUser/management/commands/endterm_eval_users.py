from django.core.management.base import NoArgsCommand
from AuroraUser.models import  AuroraUser

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        for user in AuroraUser.objects.filter(is_staff=False):
            s = "\t".join(["{}"] * 7).format(user.matriculation_number, \
                                             user.nickname, \
                                             user.first_name, \
                                             user.last_name, \
                                             user.study_code, \
                                             str(user.last_activity), \
                                             user.statement)

            print(s)
