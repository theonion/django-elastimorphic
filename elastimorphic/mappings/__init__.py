import collections

from django.db import models

import fields as search_fields


class DeclarativeMappingMeta(type):
 
    def __new__(cls, name, bases, attrs):
        fields = [(name_, attrs.pop(name_)) for name_, column in attrs.items() if isinstance(column, search_fields.SearchField)]
        # Put fields in order defined in the class.
        fields.sort(key=lambda f: f[1]._creation_order)
        attrs['fields'] = fields
        return super(DeclarativeMappingMeta, cls).__new__(cls, name, bases, attrs)


class DocumentType(object):

    __metaclass__ = DeclarativeMappingMeta

    def get_mapping(self):
        fields = collections.OrderedDict()
        for name, field in self.fields:
            name = field.index_fieldname or name
            defn = field.get_definition()
            fields[name] = defn

        mapping = {"properties": fields}
        return mapping


class MappingMixin(models.Model):

    class Meta:
        abstract = True

    SIMPLE_FIELD_MAPPINGS = {
        "CharField": search_fields.StringField,
        "IntegerField": search_fields.IntegerField,
        "DateTimeField": search_fields.DateField,
    }

    @classmethod
    def get_search_field(cls, field):
        internal_type = field.get_internal_type()
        klass = MappingMixin.SIMPLE_FIELD_MAPPINGS.get(internal_type)
        if klass:
            return klass()
        return None
        
    @classmethod
    def get_mapping(cls):
        doctype_class = DocumentType
        if hasattr(cls, "Mapping"):
            doctype_class = cls.Mapping

        exclude = getattr(doctype_class, "exclude", [])

        for field_pair in doctype_class.fields:
            exclude.append(field_pair[0])

        for field in cls._meta.fields:
            if field.name in exclude:
                continue
            search_field = cls.get_search_field(field)
            if search_field:
                doctype_class.fields.append((field.name, search_field))

        mapping = doctype_class().get_mapping()
        mapping["dynamic"] = "strict"
        mapping["_id"] = {"path": "pk"}
        return mapping

    # def extract_document(self, instance):
    #     document = {
    #         "pk": instance.pk
    #     }
    #     if issubclass(self.model, PolymorphicModel):
    #         document["polymorphic_ctype"] = instance.polymorphic_ctype_id
    #     for name, field in self.fields.items():
    #         value = getattr(instance, name, None)
    #         print(name, value)
    #         document[name] = field.to_es(value)
    #     return document

    # def load_document(self, document):
    #     instance = self.model()
    #     setattr(instance, "pk", document["pk"])

    #     for name, field in self.fields.items():
    #         value = document[name]
    #         setattr(instance, name, field.from_es(value))
    #     return instance
