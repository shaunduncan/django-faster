from dateutil import rrule

from django import VERSION
from django.conf import settings
from django.db.models import Max, Min
from django.db.models.query import QuerySet


KIND_TO_RRULE = {
    'year': rrule.YEARLY,
    'month': rrule.MONTHLY,
    'day': rrule.DAILY,
    'hour': rrule.HOURLY,
    'minute': rrule.MINUTELY,
    'second': rrule.SECONDLY,
}


class FasterQuerySetBase(QuerySet):

    def approximate_dates(self, field_name, kind, order='ASC'):
        """
        Returns a list of approximate date objects representing available dates
        for the given field_name, scoped to 'kind'. This is really a fuzzy-type
        optimization where, in PostgreSQL, DISTINCT(DATE_TRUNC('year', field))
        has serious performance issues on large tables.

        Why? This is because if field is timestamp with timezone, you cannot create
        an index on date_trunc, so you'll end up with a full sequential scan. This
        is probably OK for small tables, but not if your tables are sufficiently
        large
        """
        if kind not in ('year', 'month', 'day'):
            raise AssertionError("'kind' must be one of 'year', 'month', or 'day'.")

        if order not in ('ASC', 'DESC'):
            raise AssertionError("'order' must be either 'ASC' or 'DESC'")

        # The magic is all in how we get years. We only get a fuzzy min/max of the years
        # as it is much faster than select distinct. Then we generate dates
        dates = self.aggregate(min=Min(field_name), max=Max(field_name))

        # Generate datetimes from min_year -> max_year, delta 'kind'
        rule = rrule.rrule(KIND_TO_RRULE[kind], dtstart=dates['min'])

        return sorted(rule.between(dates['min'], dates['max'], inc=True),
                      reverse=(order == 'DESC'))


class FasterQuerySet16(FasterQuerySetBase):
    """
    A sublass of FasterQuerySetBase that exposes behavior that is present in django >= 1.6
    """

    def approximate_dates(self, *args, **kwargs):
        from django.utils import six

        datetimes = super(FasterQuerySet16, self).approximate_dates(*args, **kwargs)
        return six.moves.map(lambda dt: dt.date(), datetimes)

    def approximate_datetimes(self, field_name, kind, order='ASC', tzinfo=None):
        """
        Returns a list of approximate datetime objects representing available datetimes
        for the given field_name, scoped to 'kind'. This is really a fuzzy-type
        optimization where, in PostgreSQL, DISTINCT(DATE_TRUNC('year', field))
        has serious performance issues on large tables.

        Why? This is because if field is timestamp with timezone, you cannot create
        an index on date_trunc, so you'll end up with a full sequential scan. This
        is probably OK for small tables, but not if your tables are sufficiently
        large
        """
        from django.utils import six
        from django.utils import timezone

        if kind not in ('year', 'month', 'day', 'hour', 'minute', 'second'):
            raise AssertionError("'kind' must be one of 'year', 'month', 'day', "
                                 "'hour', 'minute', 'or 'second'.")

        if order not in ('ASC', 'DESC'):
            raise AssertionError("'order' must be either 'ASC' or 'DESC'")

        if settings.USE_TZ:
            if tzinfo is None:
                tzinfo = timezone.get_current_timezone()
        else:
            tzinfo = None

        # The magic is all in how we get years. We only get a fuzzy min/max of the years
        # as it is much faster than select distinct. Then we generate dates
        datetimes = self.aggregate(min=Min(field_name), max=Max(field_name))

        # Generate datetimes from min_year -> max_year, delta 'kind'
        rule = rrule.rrule(KIND_TO_RRULE[kind], dtstart=datetimes['min'])

        datetimes = sorted(rule.between(datetimes['min'], datetimes['max'], inc=True),
                           reverse=(order == 'DESC'))

        if tzinfo is not None:
            return six.moves.map(lambda dt: timezone.make_aware(dt, tzinfo), datetimes)
        return datetimes


# Depending on the version of django is installed, use the correct manager
if VERSION >= (1, 6):
    FasterQuerySet = FasterQuerySet16
else:
    FasterQuerySet = FasterQuerySetBase
