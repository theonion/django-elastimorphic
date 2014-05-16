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
            defn = field.get_definition()
            fields[name] = defn

        mapping = {"properties": fields}
        return mapping


class ObjectField(DocumentType, search_fields.SearchField):
    field_type = "object"


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
