from django.db.models import Manager

from faster.models.query import FasterQuerySet


class FasterManager(Manager):

    def get_fast_queryset(self):
        return FasterQuerySet(self.model, using=self._db)

    def dates(self, *args, **kwargs):
        return self.get_fast_queryset().approximate_dates(*args, **kwargs)
