from django.db import models


class Space(models.Model):
    TYPE_CHOICES = [
        ('box', 'Caja'),
        ('freezer', 'Freezer'),
    ]

    STATUS_CHOICES = [
        ('enabled', 'Habilitado'),
        ('disabled', 'Inhabilitado'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
