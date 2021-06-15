import re
from decimal import Decimal
from datetime import date
from backports.cached_property import cached_property
from itertools import islice

from sqlalchemy import create_engine

from .logger import logger


class Controllers():

    PARAM_RE = re.compile(':([-a-z()_]+)$')

    def __init__(self, connection_string, max_rows, debug):
        self.connection_string = connection_string
        self.max_rows = max_rows
        self.debug = debug

    @cached_property
    def engine(self):
        return create_engine(self.connection_string, pool_size=20, max_overflow=0)

    def query_db_streaming(self, query_str, formatters):
        try:
            headers, formatters = self.parse_formatters(formatters)

            with self.engine.connect() as connection:
                logger.debug('executing %r', query_str)
                result = connection.execution_options(stream_results=True)\
                    .execute(query_str)
                yield headers
                yield from (
                    [f(row) for f in formatters]
                    for row in map(self.jsonable, map(dict, result))
                )
        except Exception:
            logger.exception('EXC')
            raise

    def query_db(self, query_str, num_rows):
        try:
            with self.engine.connect() as connection:
                num_rows = min(num_rows, self.max_rows)
                query = "select * from (%s) s limit %s" % (query_str, num_rows)
                count_query = "select count(1) from (%s) s" % query_str
                logger.debug('executing %r', count_query)
                count = connection.execute(count_query).fetchone()[0]
                logger.debug('count %r', count)
                logger.debug('executing %r', query)
                result = connection.execute(query)
                rows = list(map(dict, islice(iter(result), 0, num_rows)))
                rows = [self.jsonable(row) for row in rows]
                logger.debug('rowcount %r', len(rows))
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        return {
            'success': True,
            'total': count,
            'rows': rows,
        }

    def parse_formatters(self, formatters):
        _headers = []
        _formatters = []
        for h in formatters:
            matches = self.PARAM_RE.findall(h)
            funcs = []
            while len(matches) > 0:
                mod = matches[0]
                h = h[:-(len(mod)+1)]
                funcs.append(self.formatter(mod))
                matches = self.PARAM_RE.findall(h)
            f = self.getter(h)
            for g in reversed(funcs):
                f = self.compose(f, g)
            k = self.wrapper(f)
            _formatters.append(k)
            _headers.append(h)
        return _headers, _formatters

    def wrapper(self, f):
        def _f(row):
            return f('', row)
        return _f

    def getter(self, h):
        hdr = h

        def _f(x, row):
            return row[hdr]
        return _f

    def compose(self, f, g):
        def _f(x, row):
            return g(f(x, row), row)
        return _f

    def formatter(self, mod):
        if mod == 'number':
            def _f(x, row):
                return str(x)
            return _f
        elif mod == 'yesno':
            def _f(x, row):
                return 'Yes' if x else 'No'  # TODO
            return _f
        elif mod == 'comma-separated':
            def _f(x, row):
                if x and isinstance(x, list):
                    return ','.join(x)
            return _f
        else:
            def _f(x, row):
                return str(x)
            return _f

    def jsonable(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, list):
            return [self.jsonable(x) for x in obj]
        if isinstance(obj, dict):
            return dict((k, self.jsonable(v)) for k, v in obj.items())
        return obj
