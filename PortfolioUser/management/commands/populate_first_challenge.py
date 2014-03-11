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
from AmanamanProjekt.settings import STATIC_ROOT
import os
from django.core.files import File


class Command(BaseCommand):
    help = 'Populates database with demo data'

    def handle(self, *args, **options):
        init_data()


def init_data():
    CommentsConfig.setup()

    number_of_users = 3
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
    for i in range(4):
        print("adding dummy user %s of %s" % (i, 4))
        username = "d%s" % i
        dummy_user = PortfolioUser(username=username)
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

    # create courses "GSI" and "HCI"
    if Course.objects.filter(short_title='gsi').exists():
        gsi = Course.objects.get(short_title='gsi')
    else:
        print('adding course gsi')
        gsi = Course(
            title='Gesellschaftliche Spannungsfelder der Informatik',
            short_title='gsi',
            description='GSI Description',
            course_number='187.237',
        )
        gsi.save()

    if Course.objects.filter(short_title='bhci').exists():
        hci = Course.objects.get(short_title='bhci')
    elif Course.objects.filter(short_title='hci').exists():
        hci = Course.objects.get(short_title='hci')
    else:
        print('adding course hci')
        hci = Course(
            title='Human Computer Interaction',
            short_title='hci',
            description='HCI Description',
            course_number='187.A21',
        )
        hci.save()

    for user in users:
        CourseUserRelation(course=gsi, user=user).save()
        CourseUserRelation(course=hci, user=user).save()

    # create course-user relations
    print('adding course-user relations for dummy users')
    CourseUserRelation(course=gsi, user=d1).save()
    CourseUserRelation(course=hci, user=d1).save()
    CourseUserRelation(course=gsi, user=d2).save()
    CourseUserRelation(course=hci, user=d2).save()
    CourseUserRelation(course=gsi, user=d3).save()
    CourseUserRelation(course=hci, user=d3).save()
    CourseUserRelation(course=gsi, user=d4).save()
    CourseUserRelation(course=hci, user=d4).save()

    # create challenges
    print('adding challenges')
    challenge_1 = Challenge(id=1,
                            title='Personalisieren',
                            subtitle='Personalisieren',
                            description='Setzen sie in ihrem Profil ein Avatar-Bild, das ein anderes ist als der Default. Achten sie dabei bitte darauf, dass die Abbildungen'
                                        ' weder rassistisch noch sexistisch sind. Es muss allerdings auch kein Foto von ihnen sein. Machen sie dann einen Screenshot, auf dem'
                                        ' ihr Avatar-Bild gut zu sehen ist, laden sie ihn hoch und geben sie das für diesen Task ab. Achten sie bitte darauf, dass ausser ihrem'
                                        ' Nickname keine anderen persönlichen Daten zu sehen sind.<br/><br/>'
                                        'Anmerkung: so ein Screenshot muss nicht ihren ganzen Bildschirm zeigen. Es genügt, wenn man den für den Task jeweils wesentlichen '
                                        'Ausschnitt sieht.',
                            accepted_files='image/*'
    )
    challenge_1.image.save('1.png', File(open(os.path.join(STATIC_ROOT, 'img', '1.png'), 'rb')))
    challenge_1.save()

    ReviewQuestion(challenge=challenge_1, order=1, text="Wurde die Aufgabe im wesentlichen erfüllt?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_1, order=2, text="Falls nein: Beschreiben sie, warum die Aufgabe nicht erfüllt wurde!").save()
    ReviewQuestion(challenge=challenge_1, order=3, text="Finden sie den Avatar nett?", boolean_answer=True).save()

    challenge_2 = Challenge(id=2,
                            title='Kommentieren',
                            subtitle='Kommentieren',
                            prerequisite=challenge_1,
                            description='Posten sie einen Kommentar zu den Folien der ersten Vorlesung. Dieser soll entweder einen inhaltlichen Bezug zum Inhalt einer Folie'
                                        ' bzw. des entsprechenden Vorlesungsteils haben, oder auf den Kommentar einer Kollegin oder eines Kollegen antworten.<br/>'
                                        'Achten sie auch hier darauf, dass ihre Äusserungen nicht rassistisch oder sexistisch sind, und streben sie ein dem universitären '
                                        'Umfeld entsprechendes Anspruchsniveau an. Auch wenn Diskussionen hitzig und/oder emotional sind, sollten gewisse Grenzen (Beleidigung, '
                                        'Herabwürdigung, Beschimpfung etc.) nicht überschritten werden.<br/><br/>'
                                        'Machen sie dann einen Screenshot ihres Kommentars, laden sieh ihn für diesen Task hoch und geben sie ihn ab. Geben sie ausserdem '
                                        'den Titel der Folie an, zu der sie den Kommentar gepostet haben.',
                            accepted_files='image/*'
    )
    challenge_2.image.save('2.png', File(open(os.path.join(STATIC_ROOT, 'img', '2.png'), 'rb')))
    challenge_2.save()

    ReviewQuestion(challenge=challenge_2, order=1, text="Wurde die Aufgabe im wesentlichen erfüllt?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_2, order=2, text="Falls nein: Beschreiben sie, warum die Aufgabe nicht erfüllt wurde!").save()
    ReviewQuestion(challenge=challenge_2, order=3,
                   text="Gibt es inzwischen Antworten auf den Kommentar? Gehen sie dazu zu der angegebenen Folie, und schauen sie, ob der Kommetnar zum Zeitpunkt ihres Reviews"
                        " schon eine Antwort bekommen hat.",
                   boolean_answer=True).save()

    challenge_3 = Challenge(id=3,
                            title='Markieren',
                            subtitle='Markieren',
                            prerequisite=challenge_2,
                            description='Markieren Sie Folien! Im Bereich »Slides« gibt es bei jeder Folie rechts oben drei »Lesezeichen«-Symbole, mit denen sie verwirrende '
                                        'Folien [??], wichtige Folien [!] und Folien, die ihnen gefallen [*], markieren können.<br/><br/>'
                                        'Markieren sie aus der ersten Vorlesung jeweils mindestens eine Folie als [??], [!] und [*]. Öffnen sie dann die drei '
                                        '»Lesezeichen«-Seiten (direkt im Slides-Bereich, zweite Zeile) und machen sie drei Screenshots, die die so markierten Folien zeigen.<br/>'
                                        'Geben sie diese drei Screenshots ab.',
                            accepted_files='image/*'
    )
    challenge_3.image.save('3.png', File(open(os.path.join(STATIC_ROOT, 'img', '3.png'), 'rb')))
    challenge_3.save()

    ReviewQuestion(challenge=challenge_3, order=1, text="Wurde die Aufgabe im wesentlichen erfüllt?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_3, order=2, text="Falls nein: Beschreiben sie, warum die Aufgabe nicht erfüllt wurde!").save()

    challenge_4 = Challenge(id=4,
                            title='Bewerten',
                            subtitle='Bewerten',
                            prerequisite=challenge_3,
                            description='Bewerten sie einen oder mehrere Kommentare in den Slides mit Hilfe der Bewertungspfeile rechts oben im Kommentar. '
                                        'Setzen sie diese Funktion ein, um auszudrücken, ob sie den Kommentar inhaltlich lesenswert finden - oder eben nicht.<br/><br/>'
                                        'Machen sie einen Screenshot von einem Kommentar, den sie bewertet haben, und geben sie diesen ab.',
                            accepted_files='image/*'
    )
    challenge_4.image.save('4.png', File(open(os.path.join(STATIC_ROOT, 'img', '4.png'), 'rb')))
    challenge_4.save()

    ReviewQuestion(challenge=challenge_4, order=1, text="Wurde die Aufgabe im wesentlichen erfüllt?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_4, order=2, text="Falls nein: Beschreiben sie, warum die Aufgabe nicht erfüllt wurde!").save()

    challenge_5 = Challenge(id=5,
                            title='Vormerken',
                            subtitle='Vormerken',
                            prerequisite=challenge_4,
                            description='Markieren sie Kommentare! Möchten sie einen Kommentar vormerken, zB. weil er wichtige Informationen enthält, oder weil'
                                        ' sie ihn weiter verfolgen möchten? Markieren sie mindestens einen Kommentar (im Newsfeed, in den Kommentaren, oder überall,'
                                        ' wo es Kommentare gibt) mit Hilfe der »BOOKMARK«-Funktion links unter dem Kommentar.<br/><br/>'
                                        'Öffnen sie dann die »Bookmarks«-Seite (Hauptnavigation), und machen sie einen Screenshot von der Sammlung vorgemerkter '
                                        'Kommentare. Geben sie diesen Screenshot ab.',
                            accepted_files='image/*'
    )
    challenge_5.image.save('5.png', File(open(os.path.join(STATIC_ROOT, 'img', '5.png'), 'rb')))
    challenge_5.save()
    ReviewQuestion(challenge=challenge_5, order=1, text="Wurde die Aufgabe im wesentlichen erfüllt?", boolean_answer=True).save()
    ReviewQuestion(challenge=challenge_5, order=2, text="Falls nein: Beschreiben sie, warum die Aufgabe nicht erfüllt wurde!").save()
    ReviewQuestion(challenge=challenge_5, order=3, text="Schätzen sie: wurden hier sinnvolle Kommentare markiert?", boolean_answer=True).save()

    challenge_6 = Challenge(id=6,
                            title='Erwarten',
                            subtitle='Erwarten',
                            prerequisite=challenge_5,
                            description='Was erwarten Sie sich von dieser Lehrveranstaltung? Was, meinen sie, werden sie hier lernen? Schreiben sie etwa einen Absatz'
                                        ' Text über ihre <b>inhaltlichen</b> Erwartungen an diese LVA.  Schreiben sie als Abschluss einen Satz zu anderen Erwartungen'
                                        ' zu dieser Lehrveranstaltung (Organisation, Experience, Unterhaltungswert, etc.).',
                            accepted_files=''
    )
    challenge_6.image.save('6.png', File(open(os.path.join(STATIC_ROOT, 'img', '6.png'), 'rb')))
    challenge_6.save()


    # create course-challenge relations
    print('adding course-challenge relations')
    CourseChallengeRelation(course=gsi, challenge_id=1).save()
    CourseChallengeRelation(course=gsi, challenge_id=2).save()
    CourseChallengeRelation(course=gsi, challenge_id=3).save()
    CourseChallengeRelation(course=gsi, challenge_id=4).save()
    CourseChallengeRelation(course=gsi, challenge_id=5).save()
    CourseChallengeRelation(course=gsi, challenge_id=6).save()

    CourseChallengeRelation(course=hci, challenge_id=1).save()
    CourseChallengeRelation(course=hci, challenge_id=2).save()
    CourseChallengeRelation(course=hci, challenge_id=3).save()
    CourseChallengeRelation(course=hci, challenge_id=4).save()
    CourseChallengeRelation(course=hci, challenge_id=5).save()
    CourseChallengeRelation(course=hci, challenge_id=6).save()


    # create stacks
    print('adding stack aurora gsi')
    aurora_gsi = Stack(
        title='Einstieg - Aurora kennenlernen',
        description='Diese Challenge soll ermöglichen, Aurora besser kennenzulernen, und gibt auch uns Gelegenheit, das System bei voller Nutzerlast testen zu können. '
                    'Rechnen sie mit Problemen und Bugs, und nutzen sie gegebenenfalls bitte den Menüpunkt »Bugs & Feedback«, um diese zu dokumentieren.<br/><br/>'
                    'Im Gegensatz zu allen anderen Challenges sind sie bei diesen Tasks gegenüber ihren Kollegen im Review <b>nicht anonym</b>, da sie ja Screenshots '
                    'abgeben, mit denen sie identifiziert werden können. Das ist leider unvermeidbar, und wird, wenn alles gut geht, die einzige Ausnahme bleiben.',
        course=gsi,
    )
    aurora_gsi.save()

    print('adding aurora hci')
    aurora_hci = Stack(
        title='Einstieg - Aurora kennenlernen',
        description='Diese Challenge soll ermöglichen, Aurora besser kennenzulernen, und gibt auch uns Gelegenheit, das System bei voller Nutzerlast testen zu können. '
                    'Rechnen sie mit Problemen und Bugs, und nutzen sie gegebenenfalls bitte den Menüpunkt »Bugs & Feedback«, um diese zu dokumentieren.'
                    'Im Gegensatz zu allen anderen Challenges sind sie bei diesen Tasks gegenüber ihren Kollegen im Review <b>nicht anonym</b>, da sie ja Screenshots '
                    'abgeben, mit denen sie identifiziert werden können. Das ist leider unvermeidbar, und wird, wenn alles gut geht, die einzige Ausnahme bleiben.',
        course=hci,
    )
    aurora_hci.save()


    # create stack-challenge relations
    print('adding stack challenge relations')
    StackChallengeRelation(stack=aurora_gsi, challenge=challenge_1).save()
    StackChallengeRelation(stack=aurora_gsi, challenge=challenge_2).save()
    StackChallengeRelation(stack=aurora_gsi, challenge=challenge_3).save()
    StackChallengeRelation(stack=aurora_gsi, challenge=challenge_4).save()
    StackChallengeRelation(stack=aurora_gsi, challenge=challenge_5).save()
    StackChallengeRelation(stack=aurora_gsi, challenge=challenge_6).save()

    StackChallengeRelation(stack=aurora_hci, challenge=challenge_1).save()
    StackChallengeRelation(stack=aurora_hci, challenge=challenge_2).save()
    StackChallengeRelation(stack=aurora_hci, challenge=challenge_3).save()
    StackChallengeRelation(stack=aurora_hci, challenge=challenge_4).save()
    StackChallengeRelation(stack=aurora_hci, challenge=challenge_5).save()
    StackChallengeRelation(stack=aurora_hci, challenge=challenge_6).save()


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
