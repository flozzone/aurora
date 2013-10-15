from django.db import models

# Create your models here.

class Review(models.Model):
    elaboration = models.ForeignKey('Elaboration.Elaboration')
    user = models.ForeignKey('PortfolioUser.PortfolioUser')
    text = models.TextField(1000)
    reviewDate = models.DateTimeField(auto_now_add=True)
    reviewState = models.CharField(max_length=100)