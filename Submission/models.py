from django.db import models

# Create your models here.

class Submission(models.Model):
    elaboration = models.ForeignKey('Elaboration.Elaboration')
    submissionDate = models.DateTimeField(auto_now_add=True)

    SUBMISSION_STATE_WAITING_FOR_EVALUATION = 'WE'
    SUBMISSION_STATE_EVALUATED = 'EV'
    SUBMISSION_STATE_BEING_REVISED = 'BR'

    SUBMISSION_STATES = (
                            (SUBMISSION_STATE_WAITING_FOR_EVALUATION, 'not evaluated'),
                            (SUBMISSION_STATE_EVALUATED, 'evaluated'),
                            (SUBMISSION_STATE_BEING_REVISED, 'in revision'),
                        )

    submissionState = models.CharField(max_length=2, choices=SUBMISSION_STATES, default=SUBMISSION_STATE_WAITING_FOR_EVALUATION)