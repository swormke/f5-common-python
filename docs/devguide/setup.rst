Setting Up Your Environment
===========================

We think using virtual-environments is a good thing and encourage you to use
them too.  Below are a few things you should do before you start to write your
code to make sure you have everything you need to be productive.

Fork and Clone The Repo
~~~~~~~~~~~~~~~~~~~~~~~
1. Fork the `F5Networks/f5-common-python
   <https://github.com/F5Networks/f5-common-python>`_ repo into your GitHub
   account by clicking the *fork* button on the top left of the page.

2. When this completes, clone your fork of the repo onto you development
   machine.

.. code:: shell

    $> git clone https://github.com/username/f5-common-python.git

3. Create a git remote that points to the F5Networks/f5-common-python
   GitHub repo so that you can fetch and update your local copy of the code
   with changes the rest of the team is merging.  We like to call this
   ``upstream``.

.. code:: shell

    $> git remote add upstream https://github.com/F5Networks/f5-common-python
    $> git remote -v

Create a Feature Branch
~~~~~~~~~~~~~~~~~~~~~~~
It is always a good idea to create a feature branch that is based off of the
branch that you will ultimately be merging into.  We like to use a naming
convention that is ``feature.my-feature``, but you can use whatever you want
becaue you will be pushing to your fork.

The code below creates a branch called ``feature.my-feature`` which tracks
the upstream F5Networks's repo on branch 0.1.

.. code:: shell

    $> git checkout -b feature.my-feature upstream/0.1

Create A Virtual Environment and Install Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We like to develop in a virtual environment.  You don't have to of course, but
it makes the environment much cleaner and allows you to work on multiple
projects and versions more easily.  The steps below assume you have `virtual
environments <https://virtualenv.pypa.io/en/latest/>`_ installed on your
development system (the same one you cloned your code on) along with the
`virtualenvwrapper <https://virtualenvwrapper.readthedocs.org/en/latest/>`_
that makes dealing with them a whole lot easier.

.. code:: shell

    $> mkvirtualenv f5-common-python
    $> cd path/to/repos/f5-common-python
    $> pip install -r requirements.test.txt

The above commands will create a virtual-env named ``f5-common-python`` and
install all of the required libraries for developing and testing the code.

Testing the Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can test the installation by running our tests.  We have three different
tests that you can run.  You will need to run these prior to creating your
Pull Request when you are done with your code so make sure they work now.

1. Style checking with ``flake8``
2. Unit tests
3. Functional tests (you will need a BIG-IP to run these)

Style Checker
^^^^^^^^^^^^^
Run the command below from the top level directory of the code you cloned.

.. code:: shell

    $> flake8 --exclude docs

Unit Tests
^^^^^^^^^^
Run the command below from the top level directory of the code you cloned.

.. code:: shell

    $> py.test -sv --tb=line f5

Functional Tests
^^^^^^^^^^^^^^^^
Run the command below from the top level directory of the code you cloned.
You will of course need to use the IP address/hostname of your BIG-IP and the
appropriate login information.

.. code:: shell

    $> py.test -sv --tb=line --bigip=192.168.1.1 --username=admin --password==admin test/functional/

