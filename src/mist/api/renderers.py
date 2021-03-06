"""
    CSV renderer for API results
"""
import json
import csv

try:
    from StringIO import StringIO  # python 2
except ImportError:
    from io import StringIO  # python 3

from pyramid.events import subscriber
from pyramid.events import NewRequest

from mist.api.helpers import params_from_request


@subscriber(NewRequest)
def json_to_csv_subscriber(event):
    """
    Subscribes to all requests and if the accept header mentions csv
    it overrides the default renderer with the csv one
    """
    request = event.request
    try:
        if (request.accept.header_value.endswith('csv') and
                request.path.startswith('/api/')):
            request.override_renderer = 'csv'
            return True
    except AttributeError:
        pass


def flattenjson(obj, delim="__"):
    """
    Flattens a JSON object

    Arguments:
    obj -- dict or list, the object to be flattened
    delim -- string, delimiter for sub-fields

    Returns:
    The flattened JSON object
    """
    val = {}
    for i in obj:
        if isinstance(obj[i], dict):
            ret = flattenjson(obj[i], delim)
            for j in ret:
                val[i + delim + j] = ret[j]
        else:
            val[i] = obj[i]
    return val


def json2csv(value, columns=None):
    """
    Transforms a serialized JSON object to CSV format
    """
    if isinstance(value, basestring):
        value = json.loads(value)
    flat_value = map(lambda x: flattenjson(x, "__"), value)
    if not columns:
        columns = [x for row in flat_value for x in row.keys()]
    columns = list(set(columns))
    fout = StringIO()
    writer = csv.writer(fout, delimiter=',', quotechar='"',
                        quoting=csv.QUOTE_MINIMAL)

    writer.writerow(columns)
    for row in flat_value:
        writer.writerow(map(lambda x: row.get(x, ""), columns))

    return fout.getvalue()


class CSVRenderer(object):
    """
    Pyramid renderer for CSV encoding
    """
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        """ Returns a plain CSV-encoded string with content-type
        ``text/csv``. The content-type may be overridden by
        setting ``request.response.content_type``."""

        request = system.get('request')
        if request is not None:
            response = request.response
            if request.path.startswith('/api/') and \
               request.accept.header_value.endswith('csv'):
                response.content_type = 'text/csv'
                params = params_from_request(request)
                columns = params.get('columns', '')
                columns = columns and columns.split(',') or []
                response.body = json2csv(value, columns)
            else:
                response.content_type = 'application/json'
                response.json_body = value
