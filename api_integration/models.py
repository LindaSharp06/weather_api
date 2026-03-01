# Django models (admin/migrations). Exchange rate data is stored via SQLAlchemy in exchange_rate.py (tables: requests, responses).
from django.db import models


class Request(models.Model):
    timestamp = models.DateTimeField()


class Response(models.Model):
    request = models.ForeignKey(Request, related_name="responses", on_delete=models.CASCADE)
    exchange_rate = models.FloatField()
    status_code = models.IntegerField()