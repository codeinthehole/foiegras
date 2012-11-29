from django.db import models


class Record(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=12)
    stock = models.PositiveIntegerField()
