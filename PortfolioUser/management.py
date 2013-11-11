from datetime import datetime
from django.db.models import signals

from PortfolioUser.models import PortfolioUser
from Course.models import *
from Challenge.models import Challenge
from Elaboration.models import Elaboration
from Stack.models import Stack, StackChallengeRelation


user_map = {'s0': 's0'}


def init_data(app, sender, **kwargs):
    if 'django.contrib.auth.models' == app.__name__:
        for i in range(len(list(user_map.keys()))):
            print('adding student %s of %s' % (i, len(list(user_map.keys()))))
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


        # create the three dummy users for jumpstarting the peer review process
        print('adding dummy user 1')
        d1 = PortfolioUser(username='d1')
        d1.set_password('d1')
        d1.is_staff = False
        d1.is_superuser = False
        d1.save()
        print('adding dummy user 2')
        d2 = PortfolioUser(username='d2')
        d2.set_password('d2')
        d2.is_staff = False
        d2.is_superuser = False
        d2.save()
        print('adding dummy user 3')
        d3 = PortfolioUser(username='d3')
        d3.set_password('d3')
        d3.is_staff = False
        d3.is_superuser = False
        d3.save()

        # create an admin user with password amanaman
        print('adding superuser')
        superuser = PortfolioUser(username='amanaman')
        superuser.set_password('amanaman')
        superuser.is_staff = True
        superuser.is_superuser = True
        superuser.save()


        # create courses "GSI" and "HCI"
        print('adding course gsi')
        gsi = Course(
            title='Gesellschaftliche Spannungsfelder der Informatik',
            short_title='gsi',
            description='GSI Description',
            course_number='123.456',
        )
        gsi.save()

        print('adding course hci')
        hci = Course(
            title='Human Computer Interaction',
            short_title='hci',
            description='HCI Description',
            course_number='123.457',
        )
        hci.save()


        # create course-user relations
        print('adding course-user relations')
        CourseUserRelation(course=gsi, user=user).save()
        CourseUserRelation(course=hci, user=user).save()
        CourseUserRelation(course=gsi, user=superuser).save()
        CourseUserRelation(course=gsi, user=superuser).save()


        # create challenges
        print('adding challenges')
        challenge_1 = Challenge(id=1,
                                title='meine meinung',
                                subtitle='meine meinung',
                                description='posten sie ihre meinung zu irgendwas in drei sätzen. dabei müssen sie lediglich darauf achten, dass die drei sätze alle mit demselben buchstaben beginnen.',
                                image_url='1.png',
        )
        challenge_1.save()

        challenge_2 = Challenge(id=2,
                                title='rage-comic',
                                subtitle='rage-comic',
                                prerequisite=challenge_1,
                                description='finden sie einen rage-comic, den sie lustig finden, und beschreiben sie kurz, warum sie ihn lustig finden. laden sie dazu den rage-comic als bild hoch, und beschreiben sie in einem satz mit genau 5 worten, warum dieser rage-comic zum schreien komisch ist.',
                                image_url='2.png',
        )
        challenge_2.save()

        challenge_3 = Challenge(id=3,
                                title='wikipedia',
                                subtitle='wikipedia',
                                prerequisite=challenge_2,
                                description='kopieren sie 4 absätze aus einem langweiligen wikipedia-artikel und geben sie sie ab. selbst schreiben ist verboten - das würde als plagiat gewertet!',
                                image_url='3.png',
        )
        challenge_3.save()

        challenge_4 = Challenge(id=4,
                                title='wissenschaft',
                                subtitle='wissenschaft',
                                prerequisite=challenge_3,
                                description='finden sie einen pseudowissenschaftlichen artikel und laden sie ihn hier hoch.',
                                image_url='4.png',
        )
        challenge_4.save()

        challenge_5 = Challenge(id=5,
                                title='ping',
                                subtitle='ping',
                                description='laden sie ein bild im png-format hoch. das bild muss allerdings genau quadratisch sein. schreiben sie nichts dazu (geht ja auch nicht).',
                                image_url='5.png',
        )
        challenge_5.save()

        challenge_6 = Challenge(id=6,
                                title='advice animal',
                                subtitle='advice animal',
                                prerequisite=challenge_5,
                                description='finden sie ein »advice animal« bild, das hier überhaupt nicht dazupasst. laden sie das bild hoch, und posten sie einen text dazu, der stattdessen auf dem bild stehen sollte. der muss auch gar nicht witzig sein.',
                                image_url='6.png',
        )
        challenge_6.save()

        challenge_7 = Challenge(id=7,
                                title='animated gif',
                                subtitle='animated gif',
                                prerequisite=challenge_6,
                                description='suchen sie ein lustiges animated gif und posten sie es. schreiben sie als text 10 x das wort "lustig" dazu.',
                                image_url='7.png',
        )
        challenge_7.save()

        challenge_8 = Challenge(id=8,
                                title='das bin ich',
                                subtitle='das bin ich',
                                prerequisite=challenge_7,
                                description='posten sie drei bilder von sich, und beschreiben sie kurz, wer auf den fotos zu sehen ist. die bilder von sich brauchen auch gar nicht wirklich von ihnen zu sein, sondern einfach nur von irgendwem, der ihnen ähnlich schaut. oder auch nicht.',
                                image_url='8.png',
        )
        challenge_8.save()

        challenge_9 = Challenge(id=9,
                                title='sherlock',
                                subtitle='sherlock',
                                description='finden sie einen ausschnitt der britischen fernsehserie »sherlock« auf youtube und posten sie ihn hier. schreiben sie ausserdem dazu, dass sie sherlock saucool finden (in eigenen worten!)',
                                image_url='9.png',
        )
        challenge_9.save()

        challenge_10 = Challenge(id=10,
                                 title='schmetterling',
                                 subtitle='schmetterling',
                                 prerequisite=challenge_9,
                                 description='laden sie zwei bilder von schmetterlingen hoch, und schreiben sie eine kleine geschichte (max. 10 worte), in denen die schmetterlinge vorkommen.',
                                 image_url='4.png',
        )
        challenge_10.save()

        # create course-challenge relations
        print('adding course-challenge relations')
        CourseChallengeRelation(course=gsi, challenge_id=1).save()
        CourseChallengeRelation(course=gsi, challenge_id=2).save()
        CourseChallengeRelation(course=gsi, challenge_id=3).save()
        CourseChallengeRelation(course=gsi, challenge_id=4).save()
        CourseChallengeRelation(course=gsi, challenge_id=5).save()
        CourseChallengeRelation(course=gsi, challenge_id=6).save()
        CourseChallengeRelation(course=gsi, challenge_id=7).save()
        CourseChallengeRelation(course=gsi, challenge_id=8).save()
        CourseChallengeRelation(course=gsi, challenge_id=9).save()
        CourseChallengeRelation(course=gsi, challenge_id=10).save()

        CourseChallengeRelation(course=hci, challenge_id=4).save()
        CourseChallengeRelation(course=hci, challenge_id=6).save()
        CourseChallengeRelation(course=hci, challenge_id=7).save()
        CourseChallengeRelation(course=hci, challenge_id=8).save()

        # create stacks
        print('adding stack accessibility')
        accessibility = Stack(
            title='Accessibility',
            description='Learn about Accessibility issues...',
            course=gsi,
        )
        accessibility.save()

        print('adding stack digital life')
        digitallife = Stack(
            title='Digital life',
            description='Learn about Digital life...',
            course=gsi,
        )
        digitallife.save()

        print('adding stack gtav')
        gtav = Stack(
            title='GTAV',
            description='Play some GTAV...',
            course=gsi,
        )
        gtav.save()

        # create dummy elaboration for challenge 1
        print('adding dummy elaboration 1 for challenge 1')
        de1 = Elaboration(challenge=challenge_1, user=d1, elaboration_text="dummy elaboration 1",
                          submission_time=datetime.now())
        de1.save()

        print('adding dummy elaboration 2 for challenge 1')
        de2 = Elaboration(challenge=challenge_1, user=d2, elaboration_text="dummy elaboration 2",
                          submission_time=datetime.now())
        de2.save()

        print('adding dummy elaboration 3 for challenge 1')
        de3 = Elaboration(challenge=challenge_1, user=d3, elaboration_text="dummy elaboration 3",
                          submission_time=datetime.now())
        de3.save()




        # create stack-challenge relations
        print('adding stack challenge relations')
        StackChallengeRelation(stack=accessibility, challenge=challenge_1).save()
        StackChallengeRelation(stack=accessibility, challenge=challenge_2).save()
        StackChallengeRelation(stack=accessibility, challenge=challenge_3).save()
        StackChallengeRelation(stack=accessibility, challenge=challenge_4).save()

        StackChallengeRelation(stack=digitallife, challenge=challenge_5).save()
        StackChallengeRelation(stack=digitallife, challenge=challenge_6).save()
        StackChallengeRelation(stack=digitallife, challenge=challenge_7).save()
        StackChallengeRelation(stack=digitallife, challenge=challenge_8).save()

        StackChallengeRelation(stack=gtav, challenge=challenge_9).save()
        StackChallengeRelation(stack=gtav, challenge=challenge_10).save()


signals.post_syncdb.connect(init_data)
