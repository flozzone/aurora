from datetime import datetime, timedelta
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import Count, Min
from django.contrib.contenttypes.models import ContentType

from Comments.models import Comment
from Evaluation.models import Evaluation
from Review.models import Review
from FileUpload.models import UploadFile
from ReviewAnswer.models import ReviewAnswer
from collections import Counter
from taggit.managers import TaggableManager


class Elaboration(models.Model):
    challenge = models.ForeignKey('Challenge.Challenge')
    user = models.ForeignKey('AuroraUser.AuroraUser')
    creation_time = models.DateTimeField(auto_now_add=True)
    elaboration_text = models.TextField(default='')
    submission_time = models.DateTimeField(null=True)
    tags = TaggableManager()
    comments = GenericRelation(Comment)

    def __unicode__(self):
        return str(self.id)

    def is_started(self):
        if self.elaboration_text:
            return True
        if UploadFile.objects.filter(elaboration=self).exists():
            return True
        return False

    def is_submitted(self):
        if self.submission_time:
            return True
        return False

    def is_evaluated(self):
        evaluation = self.get_evaluation()
        if evaluation:
            if evaluation.submission_time:
                return True
        return False

    def get_evaluation(self):
        evaluation = Evaluation.objects.filter(submission=self)
        if evaluation.exists():
            return evaluation[0]
        return None

    def is_reviewed_2times(self):
        if Review.objects.filter(elaboration=self, submission_time__isnull=False).count() < 2:
            return False
        return True

    def is_older_3days(self):
        if not self.is_submitted():
            return False
        if self.submission_time + timedelta(3) > datetime.now():
            return False
        return True

    def get_challenge_elaborations(self):
        elaborations = Elaboration.objects.filter(challenge=self.challenge, submission_time__isnull=False)
        if elaborations.exists():
            return elaborations
        return False

    def get_others(self):
        elaborations = (
            Elaboration.objects
            .filter(challenge=self.challenge, submission_time__isnull=False, user__is_staff=False)
            .exclude(pk=self.id)
        )
        return elaborations

    def get_content_type_id(self):
        return ContentType.objects.get_for_model(self).id

    def add_tags_from_text(self, text):
        tags = text.split(',');
        tags = [tag.lower().strip() for tag in tags]
        self.tags.add(*tags)

    def remove_tag(self, tag):
        self.tags.remove(tag)

    @staticmethod
    def get_sel_challenge_elaborations(challenge):
        elaborations = (
            Elaboration.objects
            .filter(challenge=challenge, submission_time__isnull=False)
        )
        return elaborations

    @staticmethod
    def get_course_sel_challenge_elaborations(challenge):
        elaborations = (
            Elaboration.objects
            .filter(challenge=challenge, submission_time__isnull=False)
        )
        return elaborations

    @staticmethod
    def get_course_sel_challenge_user_elaborations(challenge, user):
        elaborations = (
            Elaboration.objects
            .filter(challenge=challenge, user=user, submission_time__isnull=False)
        )
        return elaborations

    @staticmethod
    def search(challenges, user):
        elaborations = (
            Elaboration.objects
            .filter(challenge__in=challenges, user__in=user, submission_time__isnull=False)
        )
        return elaborations

    @staticmethod
    def get_missing_reviews(course):
        from Challenge.models import Challenge

        final_challenge_ids = Challenge.get_course_final_challenge_ids(course)
        missing_reviews = (
            Elaboration.objects
            .filter(submission_time__lte=datetime.now() - timedelta(days=1), user__is_staff=False,
                    challenge__course=course)
            .annotate(num_reviews=Count('review'))
            .exclude(challenge__id__in=final_challenge_ids)
        )
        final_elaborations = []
        for elaboration in missing_reviews:
            if elaboration.num_reviews < 2:
                final_elaborations.append(elaboration.id)
            else:
                if Review.objects.filter(elaboration=elaboration, submission_time__isnull=False).count() < 2:
                    final_elaborations.append(elaboration.id)

        missing_reviews = Elaboration.objects.filter(id__in=final_elaborations)
        return missing_reviews

    @staticmethod
    def get_top_level_tasks(course):
        from Challenge.models import Challenge

        final_challenge_ids = Challenge.get_course_final_challenge_ids(course)
        top_level_challenges = (
            Elaboration.objects
            .filter(challenge__id__in=final_challenge_ids, submission_time__isnull=False, user__is_staff=False)
            .annotate(evaluated=Min('evaluation__submission_time'))
            .filter(evaluated=None)
            .order_by('-submission_time')
        )
        return top_level_challenges

    @staticmethod
    def get_non_adequate_elaborations(course):
        nothing_reviews = (
            Review.objects
            .filter(appraisal=Review.NOTHING, submission_time__isnull=False)
            .prefetch_related('elaboration')
            .values_list('elaboration__id', flat=True)
        )
        non_adequate_elaborations = (
            Elaboration.objects
            .filter(id__in=nothing_reviews, submission_time__isnull=False, user__is_staff=False,
                    challenge__course=course)
        )
        return non_adequate_elaborations

    @staticmethod
    def get_non_adequate_work(course):

        """
        alle non adequate elaborations für deren final challenge es noch keine abgegebene evaluation gibt

        von allen submitted evaluations nimm den user und den stack
        für jeden stack nimm alle elaborations für den jeweiligen user

        nimm alle non adequate elaborations und exclude die vorher gefundenen elaborations
        """
        non_adequate_elaborations = Elaboration.get_non_adequate_elaborations(course).prefetch_related('challenge')

        submitted_evaluations = (
            Evaluation.objects
            .filter(submission_time__isnull=False)
            .values_list('submission__user', 'submission__challenge__stackchallengerelation__stack__id')
        )


        stack_lookup = {}
        for user, stack in submitted_evaluations:
            if not stack in stack_lookup:
                stack_lookup[stack] = [user]
            elif not user in stack_lookup[stack]:
                stack_lookup[stack].append(user)
        exclude_elaboration_ids = []
        for stack, users in stack_lookup.items():
            exclude_elaboration_ids = exclude_elaboration_ids + list(
                Elaboration.objects
                .filter(challenge__stackchallengerelation__stack__id=stack, user_id__in=users)
                .values_list('id', flat=True)
            )

        return non_adequate_elaborations.exclude(id__in=exclude_elaboration_ids)

    @staticmethod
    def get_evaluated_non_adequate_work(course):
        non_adequate_elaborations = Elaboration.get_non_adequate_elaborations(course).prefetch_related('challenge')

        submitted_evaluations = (
            Evaluation.objects
            .filter(submission_time__isnull=False)
            .values_list('submission__user', 'submission__challenge__stackchallengerelation__stack__id')
        )

        stack_loockup = {}
        for user, stack in submitted_evaluations:
            if not stack in stack_loockup:
                stack_loockup[stack] = [user]
            elif not user in stack_loockup[stack]:
                stack_loockup[stack].append(user)
        include_elaboration_ids = []
        for stack, users in stack_loockup.items():
            include_elaboration_ids = include_elaboration_ids + list(
                Elaboration.objects
                .filter(challenge__stackchallengerelation__stack__id=stack, user_id__in=users)
                .values_list('id', flat=True)
            )
        return Elaboration.objects.filter(id__in=include_elaboration_ids).filter(id__in=non_adequate_elaborations)

    # offset is the number of hours needed to pass until elaboration is applicable as candidate
    @staticmethod
    def get_review_candidate(challenge, user, offset=0):
        already_submitted_reviews_ids = (
            Review.objects
            .filter(reviewer=user, elaboration__challenge=challenge)
            .values_list('elaboration__id', flat=True)
        )
        threshold = datetime.now() - timedelta(hours=offset)
        candidates = (
            Elaboration.objects
            .filter(challenge=challenge, submission_time__lt=threshold, user__is_staff=False)
            .exclude(user=user)
            .annotate(num_reviews=Count('review'))
            .exclude(id__in=already_submitted_reviews_ids)
        ).order_by('num_reviews')

        if candidates.exists():
            return candidates[0]

        candidates = (
            Elaboration.objects
            .filter(challenge=challenge, submission_time__isnull=False, user__is_staff=True)
            .annotate(num_reviews=Count('review'))
            .exclude(id__in=already_submitted_reviews_ids)
        ).order_by('num_reviews')

        if candidates.exists():
            return candidates[0]
        print("Error! No dummy elaborations created.")
        return None

    def get_success_reviews(self):
        return Review.objects.filter(elaboration=self, submission_time__isnull=False, appraisal=Review.SUCCESS)

    def get_nothing_reviews(self):
        return Review.objects.filter(elaboration=self, submission_time__isnull=False, appraisal=Review.NOTHING)

    def get_fail_reviews(self):
        return Review.objects.filter(elaboration=self, submission_time__isnull=False, appraisal=Review.FAIL)

    def get_awesome_reviews(self):
        return Review.objects.filter(elaboration=self, submission_time__isnull=False, appraisal=Review.AWESOME)

    def get_lva_team_notes(self):
        reviews = (
            Review.objects
            .filter(elaboration=self, submission_time__isnull=False)
            .values_list('id', flat=True)
        )
        notes = (
            ReviewAnswer.objects
            .filter(review__id__in=reviews, review_question__visible_to_author=False).exclude(text='')
        )
        if notes.exists():
            return True
        return False

    def is_passing_peer_review(self):
        return not self.get_nothing_reviews().exists()

    @staticmethod
    def get_complaints(course):
        result = Elaboration.objects.filter(
            challenge__course=course,
            comments__seen=False
        ).distinct()

        return result

    @staticmethod
    def get_awesome(course):
        awesome_review_ids = (
            Review.objects
            .filter(appraisal=Review.AWESOME, submission_time__isnull=False)
            .values_list('elaboration__id', flat=True)
        )
        multiple_awesome_review_ids = ([k for k,v in Counter(awesome_review_ids).items() if v>1])
        awesome_elaborations = (
            Elaboration.objects
            .filter(id__in=multiple_awesome_review_ids, challenge__course=course, user__is_staff=False)
        )
        return awesome_elaborations

    @staticmethod
    def get_awesome_challenge(course, challenge):
        awesome_review_ids = (
            Review.objects
            .filter(appraisal=Review.AWESOME, submission_time__isnull=False)
            .values_list('elaboration__id', flat=True)
        )
        multiple_awesome_review_ids = ([k for k,v in Counter(awesome_review_ids).items() if v>1])
        awesome_elaborations = (
            Elaboration.objects
            .filter(id__in=multiple_awesome_review_ids, challenge=challenge, challenge__course=course,
                    user__is_staff=False)
        )
        return awesome_elaborations

    @staticmethod
    def get_stack_elaborations(stack):
        elaborations = []
        for challenge in stack.get_challenges():
            for elaboration in challenge.get_elaborations():
                elaborations.append(elaboration)
        return elaborations

    @staticmethod
    def get_course_elaborations(course):
        elaborations = []
        for challenge in course.get_course_challenges():
            for elaboration in challenge.get_elaborations():
                elaborations.append(elaboration)
        return elaborations

    def get_visible_comments_count(self):
        return self.comments.filter(visibility=Comment.PUBLIC).count()

    def get_invisible_comments_count(self):
        return self.comments.filter(visibility=Comment.STAFF).count()

    def get_last_post_date(self):
        comment = self.comments.latest('post_date')
        return comment.post_date
