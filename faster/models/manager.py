from django.db.models import Manager

from faster.models.query import FasterQuerySet


class FasterManager(Manager):

    def get_fast_queryset(self):
        return FasterQuerySet(self.model, using=self._db)

    def dates(self, *args, **kwargs):
        return self.get_fast_queryset().approximate_dates(*args, **kwargs)

    def datetimes(self, *args, **kwargs):
        return self.get_fast_queryset().approximate_datetimes(*args, **kwargs)

    def exact_dates(self, *args, **kwargs):
        return super(FasterManager, self).dates(*args, **kwargs)

    def exact_datetimes(self, *args, **kwargs):
        return super(FasterManager, self).dates(*args, **kwargs)
