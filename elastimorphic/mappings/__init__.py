import fields as search_fields


class DeclarativeMappingMeta(type):
 
    def __new__(cls, name, bases, attrs):
        fields = [(name_, attrs.pop(name_)) for name_, column in attrs.items() if isinstance(column, search_fields.SearchField)]
        attrs['fields'] = fields
        return super(DeclarativeMappingMeta, cls).__new__(cls, name, bases, attrs)


class DocumentType(object):

    __metaclass__ = DeclarativeMappingMeta

    def get_mapping(self):
        fields = {}
        for name, field in self.fields:
            name = field.index_fieldname or name
            defn = field.get_definition()
            fields[name] = defn

        mapping = {"properties": fields}
        return mapping


SIMPLE_FIELD_MAPPINGS = {
    "CharField": search_fields.StringField,
    "IntegerField": search_fields.IntegerField,
    "DateTimeField": search_fields.DateField,
}


def get_search_field(field):
    """Returns a tuple (name, field) representing the django field as a search_field

    """

    internal_type = field.get_internal_type()

    if internal_type in ("OneToOneField", "ForeignKey", "AutoField"):
        return (field.get_attname(), search_fields.IntegerField())

    klass = SIMPLE_FIELD_MAPPINGS.get(internal_type)
    if klass:
        return (field.name, klass())
    return None
