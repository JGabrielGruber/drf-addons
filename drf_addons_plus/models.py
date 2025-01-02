from django.db import models


class Hashes(models.Model):
    table_name = models.CharField(max_length=255, unique=True, primary_key=True)
    md5_hash = models.CharField(max_length=32)
    updated_at = models.DateTimeField(auto_now=True)
