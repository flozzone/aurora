from django.core.management.base import BaseCommand

import os
import csv
import hashlib
from datetime import datetime

from django.core.management.base import BaseCommand

from Course.models import Course, CourseUserRelation
from PortfolioUser.models import PortfolioUser

class Command(BaseCommand):
    help = 'Populates database with demo data'

    def handle(self, *args, **options):
        import_tutors()


def import_tutors():
    print("import tutors")
    print("get previously created courses")
    courses = Course.objects.all()
    if len(courses) == 0:
        print("could not find any courses!")
    csv_path = os.path.join('/tmp', 'tutors.csv')
    print("search for the tutors csv at %s" % csv_path)
    try:
        with open(csv_path, encoding='latin1') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';', quotechar='"')
            index = 0
            amount = len(csv_file.readlines())
            csv_file.seek(0)
            for row in csv_reader:
                index += 1
                print("processing row %s of %s" % (index, amount))
                values = row
                if len(values) == 5:
                    matriculation_number, last_name, first_name, email, study_code = values
                    username = "%s.%s" % (first_name.lower(), last_name.lower())
                    student, created = PortfolioUser.objects.get_or_create(username=username)
                    if created:
                        print("new user")
                    else:
                        print("user already in db")
                    student.matriculation_number = matriculation_number
                    student.last_name = last_name
                    student.first_name = first_name
                    student.email = email
                    student.study_code = study_code
                    student.nickname = first_name
                    student.is_staff = True
                    student.is_superuser = False
                    student.set_password(username)
                    student.save()
                    for course in courses:
                        CourseUserRelation.objects.get_or_create(course=course, user=student)
                    print("adding tutor %s %s to %s:" % (last_name, first_name, course.short_title))
                    print(values)
                elif len(values) != 0:
                    print(len(values))
                    print("there might be a problem with the csv or the script!")
                    print("discarding following entry:")
                    print(values)
    except IOError:
        print("could not find the csv file!")
    except Exception as e:
        print(e)
        return
