********************
Quickstart
********************

Installation
============
Install the project from pypi using::

    pip install django-elastimorphic

To install the development version::

    pip install https://github.com/theonion/django-elastimorphic/archive/master.zip

Update your settings file to include `django.contrib.contenttypes`, `polymorphic` and `elasticmorphic`::

    INSTALLED_APPS += (
        'django.contrib.contenttypes',
        'polymorphic',
        'elastimorphic'
    )

The current release of *django-elasticmorphic* supports Django 1.4, 1.5 and 1.6 and Python 3 is supported.

Making Your Models Elastimorphic
================================

Lorem ipsum

Creating Indexes
================

Once you have models that inherit from PolymorphicIndexable, you'll need to create indexes for those models:

    python manage.py synces

Migrating Indexes
================

Lorem ipsum