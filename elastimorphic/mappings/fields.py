import datetime

from django.utils import timezone


class SearchField(object):
    
    field_type = None
    attrs = []

    # Used to maintain the order of fields as defined in the class.
    _creation_order = 0

    def __init__(self, *args, **kwargs):

        # These are special.
        for attr in ('index_fieldname', 'is_multivalue'):
            setattr(self, attr, kwargs.pop(attr, None))

        # Set all kwargs on self for later access.
        for attr in kwargs.keys():
            self.attrs.append(attr)
            setattr(self, attr, kwargs.pop(attr, None))

        # Store this fields order
        self._creation_order = SearchField._creation_order
        # Increment order number for future fields.
        SearchField._creation_order += 1

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


class ObjectField(SearchField):
    field_type = "object"


# class RelatedField(SearchField):

#     def __init__(self, model, mapping_class, *args, **kwargs):
#         super(RelatedField, self).__init__()
#         self.mapping["type"] = "object"
#         self.mapping_class = mapping_class or Mapping
#         self.model = model
#         self.mapping["properties"] = self.mapping_class(model=self.model).get_properties()

#     def to_es(self, value):
#         if value:
#             return self.mapping_class(model=self.model).extract_document(value)
#         return None

#     def from_es(self, value):
#         if value:
#             return self.mapping_class(model=self.model).load_document(value)
#         return None
