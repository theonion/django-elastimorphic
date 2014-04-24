import datetime

from django.test import TestCase
from django.utils.timezone import utc

from elastimorphic.tests.testapp.models import GrandchildIndexable, RelatedModel
from elastimorphic.mappings import DocumentType, fields


class TestDoctype(DocumentType):
    
    foo = fields.StringField(index="not_analyzed")
    bar = fields.IntegerField(store="yes")
    baz = fields.DateField(format="YYYY-MM-dd")


class MappingTestCase(TestCase):

    maxDiff = 4000

    def test_manual_mapping(self):
        # {
        #     "_id": {"path": "pk"},
        #     "dynamic": "strict",
        #     "properties": {
        #         "foo": {"type": "string", "index": "not_analyzed"},
        #         "bar": {"type": "integer", "store": "yes"},
        #         "baz": {"type": "date", "format": "YYYY-MM-dd"},
        #     }
        # }
        self.assertEqual(GrandchildIndexable.get_mapping()["_id"], {"path": "pk"})
        self.assertEqual(GrandchildIndexable.get_mapping()["dynamic"], "strict")
        self.assertEqual(GrandchildIndexable.get_mapping()["properties"]["foo"], {"type": "string", "index": "not_analyzed"})
        self.assertEqual(GrandchildIndexable.get_mapping()["properties"]["bar"], {"type": "integer", "store": "yes"})
        self.assertEqual(GrandchildIndexable.get_mapping()["properties"]["baz"], {"type": "date", "format": "YYYY-MM-dd"},)


    # def test_automatic_mapping(self):
    #     mapping = DocumentType(model=GrandchildIndexable)
    #     reference_mapping = {
    #         "testapp_grandchildindexable": {
    #             "_id": {"path": "pk"},
    #             "dynamic": "strict",
    #             "properties": {
    #                 "baz": {"type": "date"},
    #                 "foo": {"type": "string"},
    #                 "bar": {"type": "integer"},
    #                 "pk": {"type": "integer"},
    #                 "polymorphic_ctype": {"type": "integer"},
    #                 "related": {
    #                     "type": "object",
    #                     "properties": {
    #                         "pk": {"type": "integer"},
    #                         "qux": {"type": "string"}
    #                     }
    #                 }
    #             }
    #         }
    #     }
    #     self.assertEqual(reference_mapping, mapping.mapping())

    # def test_extract_document(self):
    #     mapping = Mapping(model=GrandchildIndexable)

    #     related = RelatedModel.objects.create(qux="qux")
    #     test_obj = GrandchildIndexable(
    #         foo="Testing",
    #         bar=7,
    #         baz=datetime.datetime(year=2014, month=4, day=23, hour=9).replace(tzinfo=utc),
    #         related=related
    #     )
    #     test_obj.save(index=False)
    #     reference_document = {
    #         "pk": test_obj.pk,
    #         "foo": "Testing",
    #         "bar": 7,
    #         "baz": "2014-04-23T09:00:00.000000+00:00",
    #         "polymorphic_ctype": test_obj.polymorphic_ctype_id,
    #         "related": {
    #             "pk": related.pk,
    #             "qux": "qux"
    #         }
    #     }
    #     self.assertEqual(reference_document, mapping.extract_document(test_obj))

    # def test_load_document(self):
    #     mapping = Mapping(model=GrandchildIndexable)
    #     related = RelatedModel.objects.create(qux="qux")
    #     test_obj = GrandchildIndexable(
    #         foo="Testing",
    #         bar=7,
    #         baz=datetime.datetime(year=2014, month=4, day=23, hour=9).replace(tzinfo=utc),
    #         related=related
    #     )
    #     test_obj.save(index=False)
    #     document = mapping.extract_document(test_obj)

    #     loaded_object = mapping.load_document(document)
    #     self.assertEqual(loaded_object.pk, test_obj.pk)
    #     self.assertEqual(loaded_object.foo, test_obj.foo)
    #     self.assertEqual(loaded_object, test_obj)
    #     self.assertEqual(loaded_object.related.qux, test_obj.related.qux)
