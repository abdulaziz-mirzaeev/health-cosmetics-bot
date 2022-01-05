import sys

import django.utils.timezone as timezone
from django.utils.datetime_safe import datetime

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()


class Person(models.Model):
    full_name = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=64)
    product = models.CharField(max_length=256)
    user_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(default=timezone.now)


class Product(models.Model):
    title = models.CharField(max_length=256)
    excerpt = models.CharField(max_length=256)
    description_uz = models.TextField()
    description_ru = models.TextField()
    img_url = models.CharField(max_length=256)
    category_id = models.PositiveIntegerField()


class Category(models.Model):
    title_uz = models.CharField(max_length=256)
    title_ru = models.CharField(max_length=256)