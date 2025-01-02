from rest_framework import status, viewsets
from rest_framework.response import Response

from . import mixins, models, tasks


class FieldsModelViewSet(mixins.ListFieldsModelMixin,
                         viewsets.ModelViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass


class HashesViewSet(viewsets.ModelViewSet):

    hash_column = 'updated_at'

    def _get_table_name(self):
        return self.queryset.model._meta.db_table

    def _update_hash(self):
        tasks.update_hash.delay_on_commit(self._get_table_name(), self.hash_column)

    def perform_create(self, serializer):
        instance = super().perform_create(serializer)
        self._update_hash()
        return instance

    def perform_update(self, serializer):
        instance = super().perform_update(serializer)
        self._update_hash()
        return instance

    def perform_destroy(self, instance):
        instance = super().perform_destroy(instance)
        self._update_hash()
        return instance

    def list(self, request, *args, **kwargs):
        provided_hash = request.COOKIES.get('X-Data-Hash')
        hash_obj = models.Hashes.objects.filter(table_name=self._get_table_name()).first()
        stored_hash = None

        if hash_obj:
            stored_hash = hash_obj.md5_hash
            if provided_hash and provided_hash == stored_hash:
                return Response(None, status=status.HTTP_304_NOT_MODIFIED)

        response = super().list(request, *args, **kwargs)
        if stored_hash:
            response.set_cookie('X-Data-Hash', stored_hash, max_age=3600)
        return response
