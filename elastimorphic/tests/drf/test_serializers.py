from datetime import date
from elastimorphic.tests.base import BaseIndexableTestCase

from elastimorphic.tests.testapp.models import (
    ChildIndexable, GrandchildIndexable, ParentIndexable
)
from elastimorphic.tests.testapp.serializers import (
    PolymorphicParentIndexableSerializer,
)


class SerializerTestCase(BaseIndexableTestCase):
    def test_base_deserialize(self):
        data = (
            (ParentIndexable, dict(foo="Magnum P.I.")),
            (ChildIndexable, dict(foo="Quantum Leap", bar=8)),
            (GrandchildIndexable, dict(foo="AirWolf", bar=10, baz=date(1980, 1, 1))),
        )
        for klass, datum in data:
            serializer_class = klass.get_serializer_class()
            serializer = serializer_class(data=datum)
            self.assertTrue(serializer.is_valid())
            obj = serializer.save()
            self.assertIsInstance(obj, klass)
            for key, value in datum.items():
                self.assertEqual(value, getattr(obj, key))
        self.assertEqual(len(data), ParentIndexable.objects.count())

    def test_fail_base_deserialize(self):
        data = (
            (ParentIndexable, dict(foo=None)),
            (ChildIndexable, dict(foo=13234, bar="AirWolf")),
            (GrandchildIndexable, dict(foo=34515, bar="Bellisario", baz="notadate")),
        )
        for klass, datum in data:
            serializer_class = klass.get_serializer_class()
            serializer = serializer_class(data=datum)
            self.assertFalse(serializer.is_valid())

    def test_poly_deserialize(self):
        data = (
            (ChildIndexable, dict(foo="Quantum Leap", bar=8)),
            (GrandchildIndexable, dict(foo="AirWolf", bar=10, baz=date(1980, 1, 1))),
        )
        # create some instances
        instances = []
        for klass, datum in data:
            instance = klass(**datum)
            instance.save()
            instances.append(instance)
        # pull them out of the database and serialize
        serializer = PolymorphicParentIndexableSerializer(
            ParentIndexable.objects.all().order_by("id")
        )
        # make sure they were all created
        self.assertEqual(len(serializer.data), len(data))
        # ensure we get all the orginal data back
        for original_datum, serialized_datum in zip([d[1] for d in data], serializer.data):
            for key, value in original_datum.items():
                self.assertEqual(value, serialized_datum[key])
