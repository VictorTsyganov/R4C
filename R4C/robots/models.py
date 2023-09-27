from django.db import models


class Robot(models.Model):
    serial = models.CharField(max_length=5, )
    model = models.CharField(max_length=2, )
    version = models.CharField(max_length=2, )
    created = models.DateTimeField()
