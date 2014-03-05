django-elastimorphic
====================
A marriage of django-polymorphic and elasticutils. This should be considered
a work-in-progress and might change at any time. 

Usage
-----
* `python setup.py install`
* Include "elastimorphic" in your INSTALLED_APPS
* Create models which subclass PolymorphicIndexable and PolymorphicModel
* Implement the PolymorphicIndexable interfaces on your models.
* `manage.py synces` creates indexes for your models in elasticsearch

Running tests
-------------
Elastimorphic includes a simple Vagrantfile and shell provisioning script
which installs elasticsearch in a VM so you don't have to. 

* Install Vagrant
* Run `vagrant up` in the root directory of your django-elastimorphic checkout
* Get a cup of coffee and wait for that to complete.
* python setup.py test

License
-------
MIT
