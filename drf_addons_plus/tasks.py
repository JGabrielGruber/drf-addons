from celery import shared_task
from django.core.exceptions import ImproperlyConfigured
from django.db import connection

from . import models

@shared_task
def update_hash(table_name, hash_column):
    if connection.vendor != 'postgresql':
        raise ImproperlyConfigured("This operation requires PostgreSQL as the database backend.")

    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT MD5(string_agg({hash_column}::text, '' ORDER BY {hash_column})) 
            FROM {table_name};
        """)
        hash_value = cursor.fetchone()[0]
    models.Hashes.objects.update_or_create(
        table_name=table_name,
        defaults={"md5_hash":hash_value}
    )