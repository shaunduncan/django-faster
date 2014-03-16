from dateutil.relativedelta import relativedelta

from django.db.models import Max, Min
from django.db.models.query import QuerySet


class FasterQuerySet(QuerySet):

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
        minmax = self.aggregate(min_year=Min(field_name), max_year=Max(field_name))
        min_year, max_year = minmax['min_year'], minmax['max_year']

        # Generate datetimes from min_year -> max_year, delta 'kind'
        delta = relativedelta(**{'%ss' % kind: 1})
        dates = []

        while min_year <= max_year:
            dates.append(min_year)
            min_year += delta

        return sorted(dates, reverse=(order == 'DESC'))
