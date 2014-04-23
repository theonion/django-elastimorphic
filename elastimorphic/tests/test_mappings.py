import datetime

from django.test import TestCase
from django.utils.timezone import utc

from elastimorphic.tests.testapp.models import GrandchildIndexable
from elastimorphic.mapping import Mapping, StringField, IntegerField, DateField


class TestMapping(Mapping):
    
    model = GrandchildIndexable

    foo = StringField(index="not_analyzed")
    bar = IntegerField(store="yes")
    baz = DateField(format="YYYY-MM-dd")


class MappingTestCase(TestCase):

    def test_automatic_mapping(self):
        mapping = Mapping(model=GrandchildIndexable)
        reference_mapping = {
            "testapp_grandchildindexable": {
                "_id": {"path": "id"},
                "dynamic": "strict",
                "properties": {
                    "baz": {"type": "date"},
                    "foo": {"type": "string"},
                    "bar": {"type": "integer"},
                    "id": {"type": "integer"},
                    "polymorphic_ctype": {"type": "integer"}
                }
            }
        }
        self.assertEqual(reference_mapping, mapping.mapping())

    def test_extract_document(self):
        mapping = Mapping(model=GrandchildIndexable)

        test_obj = GrandchildIndexable(
            foo="Testing",
            bar=7,
            baz=datetime.datetime(year=2014, month=4, day=23, hour=9).replace(tzinfo=utc)
        )
        test_obj.save(index=False)
        reference_document = {
            "id": test_obj.id,
            "foo": "Testing",
            "bar": 7,
            "baz": "2014-04-23T09:00:00.000000+00:00",
            "polymorphic_ctype": test_obj.polymorphic_ctype_id
        }
        self.assertEqual(reference_document, mapping.extract_document(test_obj))

    def test_load_document(self):
        mapping = Mapping(model=GrandchildIndexable)
        test_obj = GrandchildIndexable(
            foo="Testing",
            bar=7,
            baz=datetime.datetime(year=2014, month=4, day=23, hour=9).replace(tzinfo=utc)
        )
        test_obj.save(index=False)
        document = mapping.extract_document(test_obj)

        loaded_object = mapping.load_document(document)
        self.assertEqual(loaded_object.pk, test_obj.pk)
        self.assertEqual(loaded_object.id, test_obj.id)
        self.assertEqual(loaded_object.foo, test_obj.foo)
        self.assertEqual(loaded_object, test_obj)

    def test_manual_mapping(self):
        mapping = TestMapping()
        reference_mapping = {
            "testapp_grandchildindexable": {
                "_id": {"path": "id"},
                "dynamic": "strict",
                "properties": {
                    "baz": {"type": "date", "format": "YYYY-MM-dd"},
                    "foo": {"type": "string", "index": "not_analyzed"},
                    "bar": {"type": "integer", "store": "yes"},
                    "id": {"type": "integer"},
                    "polymorphic_ctype": {"type": "integer"}
                }
            }
        }
        self.assertEqual(reference_mapping, mapping.mapping())
