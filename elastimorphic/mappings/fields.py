import datetime

from django.utils import timezone


class SearchField(object):
    
    field_type = None
    attrs = []

    def __init__(self, *args, **kwargs):
        # Set all kwargs on self for later access.
        for attr in kwargs.keys():
            self.attrs.append(attr)
            setattr(self, attr, kwargs.pop(attr, None))

    def to_es(self, value):
        return value

    def to_python(self, value):
        return value

    def get_definition(self):
        f = {'type': self.field_type}
        for attr in self.attrs:
            val = getattr(self, attr, None)
            if val is not None:
                f[attr] = val
        return f


class StringField(SearchField):

    field_type = "string"

    def to_es(self, value):
        if value is None:
            return None
        return unicode(value)

    def to_python(self, value):
        if value is None:
            return None


class IntegerField(SearchField):

    field_type = "integer"

    def to_es(self, value):
        if value is None:
            return None
        return int(value)

    def to_python(self, value):
        if value is None:
            return None
        return int(value)


class FloatField(SearchField):
    field_type = "float"

    def to_es(self, value):
        if value is None:
            return None
        return float(value)

    def to_python(self, value):
        if value is None:
            return None
        return float(value)


class DateField(SearchField):
    field_type = "date"

    def to_es(self, value):
        if isinstance(value, (datetime.date, datetime.datetime)):
            return value.isoformat()
        return value

    def to_python(self, value):
        if value is None:
            return None

        if isinstance(value, basestring):
            datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f+00:00").replace(tzinfo=timezone.utc)

        return value
