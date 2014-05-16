from django.core.management import call_command
from django.test import TestCase
from elasticutils import get_es

from elastimorphic.conf import settings
from elastimorphic.models import polymorphic_indexable_registry


class BaseIndexableTestCase(TestCase):
    """A TestCase which handles setup and teardown of elasticsearch indexes."""
    def setUp(self):
        self.index_suffix = "vtest"
        self.es = get_es(urls=settings.ES_URLS)
        call_command("synces", self.index_suffix, drop_existing_indexes=True)
        call_command("es_swap_aliases", self.index_suffix)

    def tearDown(self):
        self.delete_indexes_with_suffix(self.index_suffix)

    def delete_indexes_with_suffix(self, suffix):
        for base_class in polymorphic_indexable_registry.families.keys():
            self.es.indices.delete(index=base_class.get_index_name() + "_" + suffix, ignore=404)
