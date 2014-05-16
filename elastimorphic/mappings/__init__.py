import datetime

from django.utils import timezone

from elastimorphic.mappings import fields as search_fields


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


class DeclarativeMappingMeta(type):
 
    def __new__(cls, name, bases, attrs):
        fields = [(name_, attrs.pop(name_)) for name_, column in attrs.items() if hasattr(column, "get_definition")]
        attrs['fields'] = fields
        return super(DeclarativeMappingMeta, cls).__new__(cls, name, bases, attrs)


class DocumentType(SearchField):

    __metaclass__ = DeclarativeMappingMeta
    field_type = "object"

    def get_mapping(self):
        fields = {}
        for name, field in self.fields:
            defn = field.get_definition()
            fields[name] = defn

        mapping = {"properties": fields}
        return mapping

    def get_definition(self):
        definition = super(DocumentType, self).get_definition()
        definition.update(self.get_mapping())
        return definition

    def to_es(self, value):
        document = {}
        for name, field in self.fields:
            value = getattr(self, name, None)
            document[name] = field.to_es(value)
        return document

    def to_python(self, value):
        return None


SIMPLE_FIELD_MAPPINGS = {
    "CharField": search_fields.StringField,
    "IntegerField": search_fields.IntegerField,
    "FloatField": search_fields.FloatField,
    "DateTimeField": search_fields.DateField,
    "OneToOneField": search_fields.IntegerField,
    "ForeignKey": search_fields.IntegerField,
    "AutoField": search_fields.IntegerField
}


def search_field_factory(field):
    """Returns a tuple (name, field) representing the Django model field as a SearchField
    """

    internal_type = field.get_internal_type()
    klass = SIMPLE_FIELD_MAPPINGS.get(internal_type)

    if klass:
        return (field.get_attname(), klass())
    return None


def doctype_class_factory(model):
    """Given a Django model, return a DocumentType class to map it"""

    doctype_class = type("{}_Mapping".format(model.__name__), (DocumentType,), {})
    if hasattr(model, "Mapping"):
        doctype_class = model.Mapping

    exclude = getattr(doctype_class, "exclude", [])

    for field_pair in doctype_class.fields:
        exclude.append(field_pair[0])

    for field in model._meta.fields:
        if field.name in exclude:
            continue

        field_tuple = search_field_factory(field)
        if field_tuple:
            doctype_class.fields.append(field_tuple)
    return doctype_class

