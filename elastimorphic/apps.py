from django.apps import AppConfig

from .base import PolymorphicIndexable
from .models import polymorphic_indexable_registry


class ElastimorphicConfig(AppConfig):
    name = "elastimorphic"

    def ready(self):
        def register_subclasses(klass):
            for subclass in klass.__subclasses__():
                # only register concrete models
                meta = getattr(subclass, "_meta")
                if meta and not getattr(meta, "abstract"):
                    polymorphic_indexable_registry.register(subclass)
                register_subclasses(subclass)
        register_subclasses(PolymorphicIndexable)
