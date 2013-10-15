from django.db import models

# Create your models here.

class Portfolio(models.Model):
    user = models.ForeignKey('PortfolioUser.PortfolioUser')