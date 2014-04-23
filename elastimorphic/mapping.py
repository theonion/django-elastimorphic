from datetime import datetime

from django.db import models
from django.utils import timezone


class MappingField(object):
    
    name = None

    def __init__(self, index_name=None, store=None, index=None, boost=None, analyzer=None, *args, **kwargs):
        self.mapping = {}
        if index_name:
            assert isinstance(index_name, basestring)
            self.mapping["index_name"] = index_name
        if store:
            assert store in ["yes", "no"]
            self.mapping["store"] = store
        if index:
            assert index in ["analyzed", "not_analyzed", "no"]
            self.mapping["index"] = index
        if boost:
            assert isinstance(boost, float)
            self.mapping["boost"] = boost

    def to_es(self, value):
        return value

    def from_es(self, value):
        return value


class StringField(MappingField):

    def __init__(self, analyzer=None, *args, **kwargs):
        super(StringField, self).__init__(*args, **kwargs)
        self.mapping["type"] = "string"
        if analyzer:
            assert isinstance(analyzer, basestring)
            self.mapping["analyzer"] = analyzer


class IntegerField(MappingField):

    def __init__(self, precision_step=None, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)
        self.mapping["type"] = "integer"
        if precision_step:
            assert isinstance(precision_step, int)
            self.mapping["precision_step"] = precision_step


class DateField(MappingField):
    def __init__(self, format=None, *args, **kwargs):
        super(DateField, self).__init__(*args, **kwargs)
        self.mapping["type"] = "date"
        if format:
            assert isinstance(format, basestring)
            self.mapping["format"] = format

    def to_es(self, value):
        return value.replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")

    def from_es(self, value):
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f+00:00").replace(tzinfo=timezone.utc)


class Mapping(object):

    field_mappings = {
        models.CharField: StringField(),
        models.IntegerField: IntegerField(),
        models.DateTimeField: DateField(),
        models.DateField: DateField()
    }

    def __init__(self, model=None):
        if model:
            self.model = model

        self.fields = {}

        for field in self.model._meta.fields:
            field_mapping = getattr(self, field.name, None)
            if isinstance(field_mapping, MappingField):
                self.fields[field.name] = field_mapping
                continue

            if field.__class__ in self.field_mappings:
                self.fields[field.name] = self.field_mappings[field.__class__]

    def mapping(self):

        properties = {
            "polymorphic_ctype": {"type": "integer"},
            self.model.polymorphic_primary_key_name: {"type": "integer"}
        }
        for key, value in self.fields.items():
            properties[key] = value.mapping
        return {
            self.model.get_mapping_type_name(): {
                "_id": {
                    "path": self.model.polymorphic_primary_key_name
                },
                "properties": properties,
                "dynamic": "strict"
            }
        }

    def extract_document(self, instance):
        document = {
            "polymorphic_ctype": instance.polymorphic_ctype_id,
            instance.polymorphic_primary_key_name: instance.id
        }
        for name, field in self.fields.items():
            value = getattr(instance, name, None)
            document[name] = field.to_es(value)
        return document

    def load_document(self, document):
        instance = self.model()
        pk_attr_name = self.model.polymorphic_primary_key_name
        setattr(instance, pk_attr_name, document[pk_attr_name])

        # Fix up the _ptr fields
        for field in instance._meta.fields:
            if isinstance(field, models.OneToOneField) and field.name.endswith("_ptr"):
                setattr(instance, field.get_attname_column()[0], document[pk_attr_name])

        for name, field in self.fields.items():
            value = document[name]
            setattr(instance, name, field.from_es(value))
            
        return instance
