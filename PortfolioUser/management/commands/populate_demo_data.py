# -*- coding: utf-8 -*-
from datetime import datetime

import random
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from PortfolioUser.models import PortfolioUser
from Course.models import *
from Challenge.models import Challenge
from Elaboration.models import Elaboration
from Stack.models import Stack, StackChallengeRelation
from Review.models import Review
from ReviewQuestion.models import ReviewQuestion
from Slides.models import *
from Comments.models import Comment, CommentsConfig
from Notification.models import Notification


class Command(BaseCommand):
    help = 'Populates database with demo data'

    def handle(self, *args, **options):
        print("Test")
        init_data()


def init_data():
    CommentsConfig.setup()

    number_of_users = 50
    number_of_tutors = 50
    users = []
    dummy_users = []
    tutors = []

    for i in range(number_of_users):
        print("adding student %s of %s" % (i, number_of_users))
        username = "s%s" % i
        user = PortfolioUser(username=username)
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
    for i in range(3):
        print("adding dummy user %s of %s" % (i, 3))
        username = "d%s" % i
        dummy_user = PortfolioUser(username=username)
        dummy_user.email = '%s@student.tuwien.ac.at' % username
        dummy_user.first_name = 'Firstname_%s' % username
        dummy_user.last_name = 'Lastname_%s' % username
        dummy_user.nickname = 'Nickname_%s' % username
        dummy_user.is_staff = True
        dummy_user.is_superuser = False
        password = username
        dummy_user.set_password(password)
        dummy_user.save()
        dummy_users.append(dummy_user)
    d1 = dummy_users[0]
    d2 = dummy_users[1]
    d3 = dummy_users[2]

    # adding tutors
    for i in range(number_of_tutors):
        print("adding tutor %s of %s" % (i, number_of_tutors))
        username = "t%s" % i
        tutor = PortfolioUser(username=username)
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
    amanaman = PortfolioUser(username=username)
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
    superuser = PortfolioUser(username=username)
    superuser.first_name = 'Firstname_%s' % username
    superuser.last_name = 'Lastname_%s' % username
    superuser.nickname = 'Nickname_%s' % username
    superuser.set_password(username)
    superuser.is_staff = True
    superuser.is_superuser = False
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
    CourseUserRelation(course=gsi, user=amanaman).save()
    CourseUserRelation(course=hci, user=amanaman).save()
    CourseUserRelation(course=gsi, user=superuser).save()
    CourseUserRelation(course=hci, user=superuser).save()

    for tutor in tutors:
        CourseUserRelation(course=gsi, user=tutor).save()
        CourseUserRelation(course=hci, user=tutor).save()
        Notification(user=tutor, course=gsi, text="Welcome to GSI!").save()
        Notification(user=tutor, course=hci, text="Welcome to HCI!").save()

    for user in users:
        CourseUserRelation(course=gsi, user=user).save()
        CourseUserRelation(course=hci, user=user).save()
        Notification(user=user, course=gsi, text="Welcome to GSI!").save()
        Notification(user=user, course=hci, text="Welcome to HCI!").save()


    # create challenges
    print('adding challenges')
    challenge_1 = Challenge(id=1,
                            title='meine meinung',
                            subtitle='meine meinung',
                            description='posten sie ihre meinung zu irgendwas in drei sätzen. dabei müssen sie lediglich darauf achten, dass die drei sätze alle mit demselben buchstaben beginnen.',
                            image_url='1.png',
                            accepted_files=''
    )
    challenge_1.save()

    ReviewQuestion(challenge=challenge_1, order=1, text="Do you think the submission was funny?",
                   boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_1, order=2, text="Was this submission original?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_1, order=3,
                   text="Can you find any additional material not included in this submission?").save()

    challenge_2 = Challenge(id=2,
                            title='rage-comic',
                            subtitle='rage-comic',
                            prerequisite=challenge_1,
                            description='finden sie einen rage-comic, den sie lustig finden, und beschreiben sie kurz, warum sie ihn lustig finden. laden sie dazu den rage-comic als bild hoch, und beschreiben sie in einem satz mit genau 5 worten, warum dieser rage-comic zum schreien komisch ist.',
                            image_url='2.png',
                            accepted_files='image/*'
    )
    challenge_2.save()

    ReviewQuestion(challenge=challenge_2, order=1, text="Do you think the submission was funny?",
                   boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_2, order=2, text="Was this submission original?", boolean_answer=True,
                   visible_to_author=False).save()
    ReviewQuestion(challenge=challenge_2, order=3,
                   text="Can you find any additional material not included in this submission?").save()

    challenge_3 = Challenge(id=3,
                            title='wikipedia',
                            subtitle='wikipedia',
                            prerequisite=challenge_2,
                            description='kopieren sie 4 absätze aus einem langweiligen wikipedia-artikel und geben sie sie ab. selbst schreiben ist verboten - das würde als plagiat gewertet!',
                            image_url='3.png',
                            accepted_files=''
    )
    challenge_3.save()

    challenge_4 = Challenge(id=4,
                            title='wissenschaft',
                            subtitle='wissenschaft',
                            prerequisite=challenge_3,
                            description='finden sie einen pseudowissenschaftlichen artikel und laden sie ihn hier hoch.',
                            image_url='4.png',
                            accepted_files='application/pdf'
    )
    challenge_4.save()

    challenge_5 = Challenge(id=5,
                            title='ping',
                            subtitle='ping',
                            description='laden sie ein bild im png-format hoch. das bild muss allerdings genau quadratisch sein. schreiben sie nichts dazu (geht ja auch nicht).',
                            image_url='5.png',
                            accepted_files='image/png'
    )
    challenge_5.save()

    challenge_6 = Challenge(id=6,
                            title='advice animal',
                            subtitle='advice animal',
                            prerequisite=challenge_5,
                            description='finden sie ein »advice animal« bild, das hier überhaupt nicht dazupasst. laden sie das bild hoch, und posten sie einen text dazu, der stattdessen auf dem bild stehen sollte. der muss auch gar nicht witzig sein.',
                            image_url='6.png',
                            accepted_files='image/*'
    )
    challenge_6.save()

    challenge_7 = Challenge(id=7,
                            title='animated gif',
                            subtitle='animated gif',
                            prerequisite=challenge_6,
                            description='suchen sie ein lustiges animated gif und posten sie es. schreiben sie als text 10 x das wort "lustig" dazu.',
                            image_url='7.png',
                            accepted_files='image/gif'
    )
    challenge_7.save()

    challenge_8 = Challenge(id=8,
                            title='das bin ich',
                            subtitle='das bin ich',
                            prerequisite=challenge_7,
                            description='posten sie drei bilder von sich, und beschreiben sie kurz, wer auf den fotos zu sehen ist. die bilder von sich brauchen auch gar nicht wirklich von ihnen zu sein, sondern einfach nur von irgendwem, der ihnen ähnlich schaut. oder auch nicht.',
                            image_url='8.png',
                            accepted_files='image/*'
    )
    challenge_8.save()

    challenge_9 = Challenge(id=9,
                            title='sherlock',
                            subtitle='sherlock',
                            description='finden sie einen ausschnitt der britischen fernsehserie »sherlock« auf youtube und posten sie ihn hier. schreiben sie ausserdem dazu, dass sie sherlock saucool finden (in eigenen worten!)',
                            image_url='9.png',
                            accepted_files=''
    )
    challenge_9.save()

    challenge_10 = Challenge(id=10,
                             title='schmetterling',
                             subtitle='schmetterling',
                             prerequisite=challenge_9,
                             description='laden sie zwei bilder von schmetterlingen hoch, und schreiben sie eine kleine geschichte (max. 10 worte), in denen die schmetterlinge vorkommen.',
                             image_url='4.png',
                             accepted_files='image/*'
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

    # create dummy elaborations
    challenges = Challenge.objects.all()
    for challenge in challenges:
        for dummy_user in dummy_users:
            if not challenge.is_final_challenge():
                Elaboration(challenge=challenge, user=dummy_user, elaboration_text="dummy elaboration %s" % dummy_user.username,
                            submission_time='2013-11-01 10:00:00').save()

    print('adding final elaboration 1 for challenge 10')
    de4 = Elaboration(challenge=challenge_10, user=d1, elaboration_text="final submission user d1",
                      submission_time=datetime.now())
    de4.save()

    print('adding FAIL review for dummy user d1')
    Review(elaboration=de4, reviewer=d3, appraisal='F', submission_time=datetime.now()).save()

    print('adding final elaboration 2 for challenge 10')
    de5 = Elaboration(challenge=challenge_10, user=d2, elaboration_text="final submission user d2",
                      submission_time=datetime.now())
    de5.save()

    print('adding final elaboration 1 for challenge 8')
    de6 = Elaboration(challenge=challenge_8, user=d3, elaboration_text="final submission user d3",
                      submission_time=datetime.now())
    de6.save()

    # create elaboration for challenge 1 for s0
    print('adding elaboration for challenge 1 for s0')
    e1 = Elaboration(challenge=challenge_1, user=s0, elaboration_text="dummy elaboration 1",
                     submission_time=datetime.now())
    e1.save()

    elaborations = Elaboration.objects.all()
    e1 = elaborations[0]
    e2 = elaborations[1]
    e3 = elaborations[2]

    # create review for elaboration
    print('adding review 1 for elaboration for challenge 1 for s0')
    r1 = Review(elaboration=e1, reviewer=s0, appraisal='N', submission_time=datetime.now())
    r1.save()
    print('adding review 2 for elaboration for challenge 1 for s0')
    r2 = Review(elaboration=e2, reviewer=s0, appraisal='F', submission_time=datetime.now())
    r2.save()
    print('adding review 3 for elaboration for challenge 1 for s0')
    Review(elaboration=e3, reviewer=s0, appraisal='A', submission_time=datetime.now()).save()
    print('adding review 4 for elaboration for challenge 1 for s0')
    Review(elaboration=e3, reviewer=d2, appraisal='F', submission_time=datetime.now()).save()


    # create elaboration for challenge 2 for s0
    print('adding elaboration for challenge 2 for s0')
    e2 = Elaboration(challenge=challenge_2, user=s0, elaboration_text="dummy elaboration 1",
                     submission_time=datetime.now())
    e2.save()

    # create review for elaboration
    print('adding review 1 for elaboration for challenge 2 for s0')
    Review(elaboration=de4, reviewer=s0, appraisal='N', submission_time=datetime.now()).save()

    de5.save()
    print('adding review 1 for elaboration for challenge 2 for s0')
    Review(elaboration=de5, reviewer=d1, appraisal='A', submission_time=datetime.now()).save()
    print('adding review 2 for elaboration for challenge 2 for s0')
    Review(elaboration=de5, reviewer=d2, appraisal='S', submission_time=datetime.now()).save()

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

    print('adding escalation for challenge 1 for s0')
    com1 = Comment(text="escalation for review 1 for challenge 1 for d1", author=superuser, post_date=datetime.now(),
                   content_type=ContentType.objects.get_for_model(Review), object_id=r1.id, visibility=Comment.STAFF)
    com1.save()
    com2 = Comment(text="escalation for review 2 for challenge 1 for d2", author=superuser, post_date=datetime.now(),
                   content_type=ContentType.objects.get_for_model(Review), object_id=r2.id, visibility=Comment.PUBLIC)
    com2.save()

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
    Lecture(
        course=hci,
        start=datetime(2013, 1, 15, 15, 00, 17, 345952),
        end=datetime(2013, 1, 15, 17, 20, 17, 345952),
        active=True,
    ).save()
    Lecture(
        course=hci,
        start=datetime(2013, 1, 16, 15, 00, 17, 345952),
        end=datetime(2013, 1, 16, 17, 20, 17, 345952),
        active=True,
    ).save()

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

if __name__ == '__main__':
    init_data()
