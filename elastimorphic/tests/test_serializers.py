from django.test import TestCase

from elastimorphic.tests.testapp.models import GrandchildIndexable
from elastimorphic.serializers import Mapping, StringField


class GrandchildIndexableMapping(Mapping):
    
    model = GrandchildIndexable


class SerializerTestCase(TestCase):

    def test_automatic_mapping(self):
        mapping = GrandchildIndexable.Mapping(model=GrandchildIndexable)
        reference_mapping = {
            "id": {"type": "integer"},
            "polymorphic_ctype": {"type": "integer"},
            "foo": {"type": "string"},
            "bar": {"type": "integer"},
            "baz": {"type": "date"}
        }
        self.assertEqual(reference_mapping, mapping.mapping())
