from .fields import *  # noqa


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
    "CharField": StringField,
    "IntegerField": IntegerField,
    "FloatField": FloatField,
    "DateTimeField": DateField,
    "OneToOneField": IntegerField,
    "ForeignKey": IntegerField,
    "AutoField": IntegerField
}


def search_field_factory(field):
    """Returns a tuple (name, field) representing the Django model field as a SearchField
    """

    internal_type = field.get_internal_type()
    klass = SIMPLE_FIELD_MAPPINGS.get(internal_type)

    if klass:
        return (field.get_attname(), klass())
    return None
