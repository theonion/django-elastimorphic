from datetime import datetime

from django.db import models
from django.utils import timezone

from polymorphic import PolymorphicModel


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


class RelatedField(MappingField):

    def __init__(self, model, mapping_class=None, *args, **kwargs):
        super(RelatedField, self).__init__()
        self.mapping["type"] = "object"
        self.mapping_class = mapping_class or Mapping
        self.model = model
        self.mapping["properties"] = self.mapping_class(model=self.model).get_properties()

    def to_es(self, value):
        if value:
            return self.mapping_class(model=self.model).extract_document(value)
        return None

    def from_es(self, value):
        if value:
            return self.mapping_class(model=self.model).load_document(value)
        return None


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
            if field.name == "polymorphic_ctype":
                continue

            field_mapping = getattr(self, field.name, None)
            if isinstance(field_mapping, MappingField):
                self.fields[field.name] = field_mapping
                continue

            if field.__class__ == models.ForeignKey:
                self.fields[field.name] = RelatedField(model=field.related.parent_model)

            if field.__class__ in self.field_mappings:
                self.fields[field.name] = self.field_mappings[field.__class__]

    def get_properties(self):
        properties = {
            "pk": {"type": "integer"}
        }
        if issubclass(self.model, PolymorphicModel):
            properties["polymorphic_ctype"] = {"type": "integer"}
        for key, value in self.fields.items():
            properties[key] = value.mapping
        return properties

    def mapping(self):
        return {
            self.model.get_mapping_type_name(): {
                "_id": {
                    "path": "pk"
                },
                "properties": self.get_properties(),
                "dynamic": "strict"
            }
        }

    def extract_document(self, instance):
        document = {
            "pk": instance.pk
        }
        if issubclass(self.model, PolymorphicModel):
            document["polymorphic_ctype"] = instance.polymorphic_ctype_id
        for name, field in self.fields.items():
            value = getattr(instance, name, None)
            print(name, value)
            document[name] = field.to_es(value)
        return document

    def load_document(self, document):
        instance = self.model()
        setattr(instance, "pk", document["pk"])

        for name, field in self.fields.items():
            value = document[name]
            setattr(instance, name, field.from_es(value))
            
        return instance
