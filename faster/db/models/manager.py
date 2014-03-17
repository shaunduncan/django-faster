from django import VERSION
from django.db.models import Manager

from faster.models.query import FasterQuerySet


class FasterManagerBase(Manager):

    def get_fast_queryset(self):
        return FasterQuerySet(self.model, using=self._db)

    def dates(self, *args, **kwargs):
        return self.get_fast_queryset().approximate_dates(*args, **kwargs)

    def exact_dates(self, *args, **kwargs):
        return super(FasterManagerBase, self).dates(*args, **kwargs)


class FasterManager16(FasterManagerBase):
    """
    Manager with compatibility for django >= 1.6
    """

    def datetimes(self, *args, **kwargs):
        return self.get_fast_queryset().approximate_datetimes(*args, **kwargs)

    def exact_datetimes(self, *args, **kwargs):
        return super(FasterManager16, self).dates(*args, **kwargs)


# Depending on the version of django is installed, use the correct manager
if VERSION >= (1, 6):
    FasterManager = FasterManager16
else:
    FasterManager = FasterManagerBase
