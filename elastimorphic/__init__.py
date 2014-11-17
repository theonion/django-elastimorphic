from .base import Indexable, PolymorphicIndexable, SearchManager  # noqa

__version__ = "0.1.7"
__all__ = [PolymorphicIndexable, SearchManager]

default_app_config = "elastimorphic.apps.ElastimorphicConfig"
