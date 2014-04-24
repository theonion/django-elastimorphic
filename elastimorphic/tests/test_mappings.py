import datetime

from django.test import TestCase
from django.utils import timezone

from elastimorphic.tests.testapp.models import GrandchildIndexable, ChildIndexable, RelatedModel


class MappingTestCase(TestCase):

    maxDiff = 4000

    def test_manual_mapping(self):
        reference_mapping = {
            "testapp_grandchildindexable": {
                "_id": {"path": "childindexable_ptr_id"},
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "integer"},
                    "polymorphic_ctype_id": {"type": "integer"},
                    "parentindexable_ptr_id": {"type": "integer"},
                    "childindexable_ptr_id": {"type": "integer"},

                    "foo": {"type": "string", "index": "not_analyzed"},
                    "bar": {"type": "integer", "store": "yes"},
                    "baz": {"type": "date"},

                    "related_id": {"type": "integer"},
                }
            }
        }

        self.assertEqual(reference_mapping, GrandchildIndexable.get_mapping())

    def test_automatic_mapping(self):
        reference_mapping = {
            "testapp_childindexable": {
                "_id": {"path": "parentindexable_ptr_id"},
                "dynamic": "strict",
                "properties": {
                    "id": {"type": "integer"},
                    "polymorphic_ctype_id": {"type": "integer"},
                    "parentindexable_ptr_id": {"type": "integer"},
                    "foo": {"type": "string"},
                    "bar": {"type": "integer"}
                }
            }
        }

        self.assertDictEqual(reference_mapping, ChildIndexable.get_mapping())

    def test_extract_document(self):

        related = RelatedModel.objects.create(qux="qux")
        test_obj = GrandchildIndexable(
            foo="Testing",
            bar=7,
            baz=datetime.datetime(year=2014, month=4, day=23, hour=9).replace(tzinfo=timezone.utc),
            related=related
        )
        test_obj.save(index=False)
        reference_document = {
            "id": test_obj.pk,
            "parentindexable_ptr_id": test_obj.pk,
            "childindexable_ptr_id": test_obj.pk,
            "polymorphic_ctype_id": test_obj.polymorphic_ctype_id,

            "foo": "Testing",
            "bar": 7,
            "baz": "2014-04-23T09:00:00+00:00",
            
            "related_id": related.id
        }
        self.assertEqual(reference_document, test_obj.extract_document())

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
