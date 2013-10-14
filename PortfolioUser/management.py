from django.db.models import signals

from PortfolioUser.models import PortfolioUser

user_map = {'s0': 's0'}

def init_data(sender, **kwargs):
    if 'django.contrib.auth.models' == kwargs['app'].__name__:
        for i in range(len(list(user_map.keys()))):
            print('Adding Student %s of %s' % (i, len(list(user_map.keys()))))
            username = list(user_map.keys())[i]
            user = PortfolioUser(username=username)
            user.email = '%s@student.tuwien.ac.at.' % username
            user.first_name = 'Firstname_%s' % username
            user.last_name = 'Lastname_%s' % username
            user.nickname = 'Nickname_%s' % username
            user.is_staff = False
            user.is_superuser = False
            password = user_map[username]
            user.set_password(password)
            user.save()

        # create an admin user with password amanaman
        superuser = PortfolioUser(username='amanaman')
        superuser.set_password('amanaman')
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save()



signals.post_syncdb.connect(init_data)
