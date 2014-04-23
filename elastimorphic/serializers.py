from django.db import models


class MappingField(object):
    
    name = None

    def __init__(self, index_name=None, store=None, index=None, boost=None, analyzer=None, *args, **kwargs):
        self.mapping = {}
        if index_name:
            assert isinstance(index_name, basestring)
            self.mapping["index_name"] = index_name
        if store:
            assert store in ["yes", "no"]
            self.mapping["store"]
        if index:
            assert index in ["analyzed", "not_analyzed", "no"]
            self.mapping["index"] = index
        if boost:
            assert isinstance(boost, float)
            self.mapping["boost"] = boost

    def to_es(self, value):
        pass

    def from_es(self, value):
        pass


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

            if field.__class__ in self.field_mappings:
                self.fields[field.name] = self.field_mappings[field.__class__]

    def mapping(self):
        _mapping = {
            "polymorphic_ctype": {"type": "integer"},
            self.model.polymorphic_primary_key_name: {"type": "integer"}
        }
        for key, value in self.fields.items():
            _mapping[key] = value.mapping
        return _mapping
