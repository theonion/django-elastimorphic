********************
Contributing
********************

Elastimorphic includes a simple Vagrantfile and shell provisioning script
which installs elasticsearch in a VM so you don't have to. 

To get started, fork the project, and clone it. Then install Vagrant, and then::

    cd django-elasticmorphic
    vagrant up

To run the test suite, just make sure the vagrant vm is running, and then::

    python setup.py test
