# -*- coding: utf-8 -*-
from datetime import datetime

import random
import traceback
from django.core.management.base import BaseCommand
from django.db import transaction

from AuroraUser.models import AuroraUser
from Course.models import *
from Challenge.models import Challenge
from Elaboration.models import Elaboration
from Stack.models import Stack, StackChallengeRelation
from ReviewQuestion.models import ReviewQuestion
from Slides.models import *
from Comments.models import CommentsConfig
from Notification.models import Notification
from AuroraProject.settings import STATIC_ROOT
import os
from django.core.files import File


class Command(BaseCommand):
    help = 'Populates database with demo data'

    def handle(self, *args, **options):
        populate_test_session()


def populate_test_session():
    try:
        with transaction.atomic():
            print("Starting transaction...")
            import_data()

    except Exception as e:
        traceback.print_exc()
        print("Caught error during transaction: %s" % e)
        print("Database has rolled back the transaction!")
    print("All Done!")


def import_data():
    CommentsConfig.setup()

    number_of_users = 30
    number_of_tutors = 10
    users = []
    dummy_users = []
    tutors = []

    for i in range(number_of_users):
        print("adding student %s of %s" % (i, number_of_users))
        username = "s%s" % i
        user = AuroraUser(username=username)
        user.email = '%s@student.tuwien.ac.at' % username
        user.first_name = 'Firstname_%s' % username
        user.last_name = 'Lastname_%s' % username
        user.nickname = 'Nickname_%s' % username
        user.matriculation_number = "{0:0=2d}".format(i) + ''.join(["%s" % random.randint(0, 9) for num in range(0, 5)])
        user.is_staff = False
        user.is_superuser = False
        password = username
        user.set_password(password)
        user.save()
        users.append(user)
    s0 = users[0]

    # create the three dummy users for jumpstarting the peer review process
    for i in range(4):
        print("adding dummy user %s of %s" % (i, 3))
        username = "d%s" % i
        dummy_user = AuroraUser(username=username)
        dummy_user.email = '%s@student.tuwien.ac.at' % username
        dummy_user.first_name = 'Firstname_%s' % username
        dummy_user.last_name = 'Lastname_%s' % username
        dummy_user.nickname = 'Nickname_%s' % username
        dummy_user.is_staff = False
        dummy_user.is_superuser = False
        password = username
        dummy_user.set_password(password)
        dummy_user.save()
        dummy_users.append(dummy_user)
    d1 = dummy_users[0]
    d2 = dummy_users[1]
    d3 = dummy_users[2]
    d4 = dummy_users[3]

    # adding tutors
    for i in range(number_of_tutors):
        print("adding tutor %s of %s" % (i, number_of_tutors))
        username = "t%s" % i
        tutor = AuroraUser(username=username)
        tutor.email = '%s@student.tuwien.ac.at' % username
        tutor.first_name = 'Firstname_%s' % username
        tutor.last_name = 'Lastname_%s' % username
        tutor.nickname = 'Nickname_%s' % username
        tutor.is_staff = True
        tutor.is_superuser = False
        password = username
        tutor.set_password(password)
        tutor.save()
        print("***tutor username: %s" % tutor.username)
        tutors.append(tutor)

    # create an admin user with password amanaman
    print('adding superuser')
    username = "amanaman"
    amanaman = AuroraUser(username=username)
    amanaman.first_name = 'Firstname_%s' % username
    amanaman.last_name = 'Lastname_%s' % username
    amanaman.nickname = 'Nickname_%s' % username
    amanaman.set_password(username)
    amanaman.is_staff = True
    amanaman.is_superuser = True
    amanaman.save()

    # hagrid staff user
    print('adding staff')
    username = "hagrid"
    superuser = AuroraUser(username=username)
    superuser.first_name = 'Firstname_%s' % username
    superuser.last_name = 'Lastname_%s' % username
    superuser.nickname = 'Nickname_%s' % username
    superuser.set_password(username)
    superuser.is_staff = True
    superuser.is_superuser = False
    superuser.save()


    # create course "GSI"
    print('adding course gsi')
    gsi = Course(
        title='Gesellschaftliche Spannungsfelder der Informatik',
        short_title='gsi',
        description='GSI Description',
        course_number='123.456',
    )
    gsi.save()

    # create course-user relations
    print('adding course-user relations')
    CourseUserRelation(course=gsi, user=amanaman).save()
    CourseUserRelation(course=gsi, user=superuser).save()

    for tutor in tutors:
        CourseUserRelation(course=gsi, user=tutor).save()
        Notification(user=tutor, course=gsi, text="Welcome to GSI!").save()

    for user in users:
        CourseUserRelation(course=gsi, user=user).save()
        Notification(user=user, course=gsi, text="Welcome to GSI!").save()


    # create challenges
    print('adding challenges')
    challenge_1 = Challenge(id=1,
                            title='meine meinung',
                            subtitle='meine meinung',
                            description='gehen sie nach derstandard.at, suchen sie einen beliebigen artikel, und posten sie den text dieses artikels hier.',
                            accepted_files='',
                            course=gsi,
                            points=15,
    )
    challenge_1.image.save('1.png', File(open(os.path.join(STATIC_ROOT, 'img', '1.png'), 'rb')))
    challenge_1.save()

    ReviewQuestion(challenge=challenge_1, order=1, text="Erfüllt diese Arbeit die gestellte Aufgabe?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_1, order=2, text="Falls nicht: Was fehlt? Was sollte anders sein? Was ist zuviel?").save()

    challenge_2 = Challenge(id=2,
                            title='rage-comic',
                            subtitle='rage-comic',
                            prerequisite=challenge_1,
                            description='finden sie einen web-comic, den sie lustig finden, und laden sie ihn hier hoch. beschreiben sie kurz, wie lange sie diesen webcomic schon lesen.',
                            accepted_files='image/*',
                            course=gsi,
                            points=10,
    )
    challenge_2.image.save('2.png', File(open(os.path.join(STATIC_ROOT, 'img', '2.png'), 'rb')))
    challenge_2.save()

    ReviewQuestion(challenge=challenge_2, order=1, text="Erfüllt diese Arbeit die gestellte Aufgabe?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_2, order=2, text="Falls nicht: Was fehlt? Was sollte anders sein? Was ist zuviel?").save()
    ReviewQuestion(challenge=challenge_2, order=3, text="Ist der Webcomic lustig?",
                   boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_2, order=4, text="Ist dieser Webcomic interessant?", boolean_answer=True,
                   visible_to_author=False).save()

    challenge_3 = Challenge(id=3,
                            title='wikipedia',
                            subtitle='wikipedia',
                            prerequisite=challenge_2,
                            description='kopieren sie 4 absätze aus einem  wikipedia-artikel und geben sie sie ab! setzen sie ans ende der arbeit den link auf den wikipedia-artikel!',
                            accepted_files='',
                            course=gsi,
                            points=8,
    )
    challenge_3.image.save('3.png', File(open(os.path.join(STATIC_ROOT, 'img', '3.png'), 'rb')))
    challenge_3.save()

    ReviewQuestion(challenge=challenge_3, order=1, text="Erfüllt diese Arbeit die gestellte Aufgabe?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_3, order=2, text="Falls nicht: Was fehlt? Was sollte anders sein? Was ist zuviel?").save()

    challenge_4 = Challenge(id=4,
                            title='wissenschaft',
                            subtitle='wissenschaft',
                            prerequisite=challenge_3,
                            description='finden sie einen pseudowissenschaftlichen artikel und laden sie ihn hier hoch.',
                            accepted_files='application/pdf',
                            course=gsi,
                            points=9,
    )
    challenge_4.image.save('4.png', File(open(os.path.join(STATIC_ROOT, 'img', '4.png'), 'rb')))
    challenge_4.save()

    challenge_5 = Challenge(id=5,
                            title='ping',
                            subtitle='ping',
                            description='laden sie drei bilder im png-format hoch. beschreiben sie dann kurz, was auf diesen bildern zu sehen ist.',
                            accepted_files='image/png',
                            course=gsi,
                            points=10,
    )
    challenge_5.image.save('5.png', File(open(os.path.join(STATIC_ROOT, 'img', '5.png'), 'rb')))
    challenge_5.save()
    ReviewQuestion(challenge=challenge_5, order=1, text="Erfüllt diese Arbeit die gestellte Aufgabe?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_5, order=2, text="Falls nicht: Was fehlt? Was sollte anders sein? Was ist zuviel?").save()

    challenge_6 = Challenge(id=6,
                            title='advice animal',
                            subtitle='advice animal',
                            prerequisite=challenge_5,
                            description='suchen sie ein »advice animal« bild und posten sie es hier. geben sie die quelle dazu an.',
                            accepted_files='image/*',
                            course=gsi,
                            points=12,
    )
    challenge_6.image.save('6.png', File(open(os.path.join(STATIC_ROOT, 'img', '6.png'), 'rb')))
    challenge_6.save()
    ReviewQuestion(challenge=challenge_6, order=1, text="Erfüllt diese Arbeit die gestellte Aufgabe?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_6, order=2, text="Falls nicht: Was fehlt? Was sollte anders sein? Was ist zuviel?").save()

    challenge_7 = Challenge(id=7,
                            title='animated gif',
                            subtitle='animated gif',
                            prerequisite=challenge_6,
                            description='suchen sie ein animated gif und posten sie es. geben sie die quelle dazu an.',
                            accepted_files='image/gif',
                            course=gsi,
                            points=14,
    )
    challenge_7.image.save('7.png', File(open(os.path.join(STATIC_ROOT, 'img', '7.png'), 'rb')))
    challenge_7.save()
    ReviewQuestion(challenge=challenge_7, order=1, text="Erfüllt diese Arbeit die gestellte Aufgabe?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_7, order=2, text="Falls nicht: Was fehlt? Was sollte anders sein? Was ist zuviel?").save()

    challenge_8 = Challenge(id=8,
                            title='zwei menschen',
                            subtitle='zwei menschen',
                            prerequisite=challenge_7,
                            description='laden sie zwei bilder von zwei verschiedenen menschen hoch. erklären sie dann, wer diese beiden menschen sind. vergessen sie nicht auf die quellenangabe!',
                            accepted_files='image/*',
                            course=gsi,
                            points=5,
    )
    challenge_8.image.save('8.png', File(open(os.path.join(STATIC_ROOT, 'img', '8.png'), 'rb')))
    challenge_8.save()

    challenge_9 = Challenge(id=9,
                            title='youtube',
                            subtitle='youtube',
                            description='suchen sie ein gutes youtube-video und posten sie den link hier. wenn sherlock holmes darin vorkommt, dann können sie auch einen extrapunkt bekommen.',
                            accepted_files='',
                            course=gsi,
                            points=25,
    )
    challenge_9.image.save('9.png', File(open(os.path.join(STATIC_ROOT, 'img', '9.png'), 'rb')))
    challenge_9.save()
    ReviewQuestion(challenge=challenge_9, order=1, text="Erfüllt diese Arbeit die gestellte Aufgabe?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_9, order=2, text="Falls nicht: Was fehlt? Was sollte anders sein? Was ist zuviel?").save()

    challenge_10 = Challenge(id=10,
                             title='schmetterling',
                             subtitle='schmetterling',
                             prerequisite=challenge_9,
                             description='suchen sie in google image search schmetterlingsbilder und laden sie diese hier hoch. vergessen sie nicht auf die quellenangaben!',

                             accepted_files='image/*',
                             course=gsi,
                             points=3,
    )
    challenge_10.image.save('4.png', File(open(os.path.join(STATIC_ROOT, 'img', '4.png'), 'rb')))
    challenge_10.save()

    # create stacks
    print('adding stack accessibility')
    accessibility = Stack(
        title='Universal Design',
        description='In diesem Block setzen sie sich mit »Unversal Design« auseinander. Universal Design (Universelles Design) ist ein internationales Design-Konzept, das Produkte, Geräte, Umgebungen und Systeme derart gestaltet, dass sie für so viele Menschen wie möglich ohne weitere Anpassung oder Spezialisierung nutzbar sind. In der Informatik bedeutet das im allgemeinen, Systeme so zu gestalten, dass sie von Menschen mit Behinderungen, insbesondere blinde Menschen, auch benutzt werden können.',
        course=gsi,
    )
    accessibility.save()

    print('adding stack digital life')
    digitallife = Stack(
        title='Copyleft vs. Business',
        description='In diesem Block geht es um die Suche nach neuen Business-Modellen für die geänderten Bedingngen, die durch neue Technologien geschaffen wurden. Viele traditionelel Business-Modelle gehen dabei den Bach runter, neue Ansätze sind gefragt.',
        course=gsi,
    )
    digitallife.save()

    print('adding stack gtav')
    gtav = Stack(
        title='Geschichte der Informatik',
        description='Dieser Block führt sie in die Geschichte der Informatik, zurück zu den Anfängen des interaktiven Computers. Sie setzen sich damit auseinander, welche Vorstellungen von Interaktivität im Laufe der Geschichte entstanden, probiert und wieder verworfen wurden. Dabei werden Darstellungen in Film und Fernsehen ebenso aufgearbeitet wie die Visionen der Techniker und wissenschaftliche Diskussionen.',
        course=gsi,
    )
    gtav.save()

    # create dummy elaborations
    challenges = Challenge.objects.all()
    for challenge in challenges:
        for dummy_user in dummy_users:
            if not challenge.is_final_challenge():
                Elaboration(challenge=challenge, user=dummy_user, elaboration_text="dummy elaboration %s" % dummy_user.username,
                            submission_time='2013-11-01 10:00:00').save()

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

    print('Adding Sample Lectures')
    Lecture(
        course=gsi,
        start=datetime(2013, 2, 15, 15, 00, 17, 345952),
        end=datetime(2013, 2, 15, 17, 20, 17, 345952),
        active=True,
    ).save()
    Lecture(
        course=gsi,
        start=datetime(2013, 2, 16, 15, 00, 17, 345952),
        end=datetime(2013, 2, 16, 17, 20, 17, 345952),
        active=True,
    ).save()
    Lecture(
        course=gsi,
        start=datetime(2013, 2, 17, 15, 00, 17, 345952),
        end=datetime(2013, 2, 17, 17, 20, 17, 345952),
        active=True,
    ).save()
#    Lecture(
#        course=gsi,
#        start=datetime(2013, 2, 24, 15, 00, 17, 345952),
#        end=datetime(2014, 2, 24, 17, 20, 17, 345952),
#        active=True,
#    ).save()

    print('Adding Sample Slides')
    Slide(
        lecture_id=1,
        title="Preparation Slide #1 - Lecture 1",
        pub_date=datetime(2013, 2, 10, 15, 21, 17, 345952),
        filename="vo_10_02_13_1",
        tags='.preparation',
    ).save()
    Slide(
        lecture_id=1,
        title="Preparation Slide #2 - Lecture 1",
        pub_date=datetime(2013, 2, 10, 15, 22, 17, 345952),
        filename="vo_10_02_13_2",
        tags='.preparation',
    ).save()
    Slide(
        lecture_id=1,
        title="Preparation Slide #3 - Lecture 1",
        pub_date=datetime(2013, 2, 10, 15, 23, 17, 345952),
        filename="vo_10_02_13_3",
        tags='.preparation',
    ).save()        
    Slide(
        lecture_id=1,
        title="Super Sample Slide #1 - Lecture 1",
        pub_date=datetime(2013, 2, 15, 15, 20, 17, 345952),
        filename="vo_15_02_13_1",
        tags='.exercise',
    ).save()
    Slide(
        lecture_id=1,
        title="Super Sample Slide #2 - Lecture 1",
        pub_date=datetime(2013, 2, 15, 15, 22, 17, 345952),
        filename="vo_15_02_13_2",
    ).save()
    Slide(
        lecture_id=1,
        title="Super Sample Slide #3 - Lecture 1",
        pub_date=datetime(2013, 2, 15, 15, 24, 17, 345952),
        filename="vo_15_02_13_3",
    ).save()
    Slide(
        lecture_id=1,
        title="Super Sample Slide #4 - Lecture 1",
        pub_date=datetime(2013, 2, 15, 15, 26, 17, 345952),
        filename="vo_15_02_13_4",
    ).save()
    Slide(
        lecture_id=1,
        title="Super Sample Slide #5 - Lecture 1",
        pub_date=datetime(2013, 2, 15, 15, 28, 17, 345952),
        filename="vo_15_02_13_5",
        tags='.exercise',
    ).save()
    Slide(
        lecture_id=1,
        title="Super Sample Slide #6 - Lecture 1",
        pub_date=datetime(2013, 2, 15, 15, 30, 17, 345952),
        filename="vo_15_02_13_6",
    ).save()
    Slide(
        lecture_id=1,
        title="Super Sample Slide #7 - Lecture 1",
        pub_date=datetime(2013, 2, 15, 15, 32, 17, 345952),
        filename="vo_15_02_13_7",
    ).save()
    Slide(
        lecture_id=1,
        title="Super Sample Slide #8 - Lecture 1",
        pub_date=datetime(2013, 2, 15, 15, 34, 17, 345952),
        filename="vo_15_02_13_8",
    ).save()
    Slide(
        lecture_id=1,
        title="Super Sample Slide #9 - Lecture 1",
        pub_date=datetime(2013, 2, 15, 15, 36, 17, 345952),
        filename="vo_15_02_13_9",
        tags='.exercise',
    ).save()
    Slide(
        lecture_id=2,
        title="Super Sample Slide #1 - Lecture 2",
        pub_date=datetime(2013, 2, 16, 15, 20, 17, 345952),
        filename="vo_16_02_13_1",
    ).save()
    Slide(
        lecture_id=2,
        title="Super Sample Slide #2 - Lecture 2",
        pub_date=datetime(2013, 2, 16, 15, 22, 17, 345952),
        filename="vo_16_02_13_2",
    ).save()
    Slide(
        lecture_id=2,
        title="Super Sample Slide #2 - Lecture 2",
        pub_date=datetime(2013, 2, 16, 15, 24, 17, 345952),
        filename="vo_16_02_13_3",
    ).save()
    Slide(
        lecture_id=3,
        title="Super Sample Slide #1 - Lecture 3",
        pub_date=datetime(2013, 2, 17, 15, 20, 17, 345952),
        filename="vo_17_02_13_1",
    ).save()
    Slide(
        lecture_id=3,
        title="Super Sample Slide #2 - Lecture 3",
        pub_date=datetime(2013, 2, 17, 15, 22, 17, 345952),
        filename="vo_17_02_13_2",
        tags='.exercise',
    ).save()
    
    print("Adding sample stream")
    Stream(
        lecture_id=1,
        url="rtmp://video.zserv.tuwien.ac.at/lecturetube_public",
        type="rtmp",
        clipname="gsiss13e10",
        offset=-656,
    ).save()

    for user in AuroraUser.objects.all():
        if not user.avatar:
            user.get_gravatar()

if __name__ == '__main__':
    populate_test_session()
