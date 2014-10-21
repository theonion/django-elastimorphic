django-elastimorphic
====================
A marriage of django-polymorphic and elasticutils. This should be considered
a work-in-progress and might change at any time. 

[![Build Status](https://travis-ci.org/theonion/django-elastimorphic.png?branch=master)](https://travis-ci.org/theonion/django-elastimorphic)
[![Coverage Status](https://coveralls.io/repos/theonion/django-elastimorphic/badge.png)](https://coveralls.io/r/theonion/django-elastimorphic)

Usage
-----
* `python setup.py install`
* Include "elastimorphic" in your INSTALLED_APPS
* Create models which subclass PolymorphicIndexable and PolymorphicModel
* Implement the PolymorphicIndexable interfaces on your models
* `manage.py synces <alias_name>` creates indexes for your models in elasticsearch with alias <dbname>_<app_name>_<model_name>_<alias_name>
* `manage.py es_swap_aliases <alias_name>` activates the indexes in ES
* `manage.py bulk_index` populates the index with data in the PolymorphicIndexable models

Running tests
-------------
Elastimorphic includes a simple Vagrantfile and shell provisioning script
which installs elasticsearch in a VM so you don't have to. 

* Install Vagrant
* Run `vagrant up` in the root directory of your django-elastimorphic checkout
* Get a cup of coffee and wait for that to complete
* `python setup.py test`

License
-------
MIT
