#####################
Labelord application
#####################

.. image:: https://travis-ci.org/Wilson194/Labelord.svg?branch=master
   :target: https://travis-ci.org/Wilson194/Labelord


.. image:: https://readthedocs.org/projects/labelord-horacj10/badge/?version=latest
   :target: http://labelord-horacj10.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


This is project for controlling, creating and cloning GitHub issues labels (based on FIT CUT MI-PYT project).

You can find this project at test version of `PiPy <https://test.pypi.org/project/labelord-horacj10/>`_


----


This application allows you:
############################

* List repositories of given connection
* List labels of target repo
* Create/update/delete label at target repo
* Replicate labels through selected repositories


Config
########

For correct running of this application, you need to fill in config file. Default config is `config.cfg`.
You can find example of config in `default_config.cfg`. You need to specify GitHub
token for you GitHub account. Next configuration is for setting up application behaviour.
See `default_config.cfg` comments.


Usage
#####

There are 4 basic commands for this application. You can find all commands and parameters
with `labelord --help`.

Basic commands:
----------------

* labelord list_repos - list all repositories in GitHub account
* labelord list_labels [repo] - list all labels in repository
* labelord run [mode[] - run editing of labels based on config
* labelord run_server - run replication webserver  


Test
######

There are several test located in folder tests. You can run test by `setup.py test`. Tests using betamax and recording 
cassettes. Recorded cassettes are in repository. If you want to record new cassettes, you must add path to auth file to 
sys variable `LABELORD_AUTH`. In this file you must specify `token` under section `github`


Documentation
##############

Whole docummentation you can find at `this page <http://labelord-horacj10.readthedocs.io/en/latest/>`_.
If you want to build documentation at your computer just write this command in folder docs:

.. code:: bash

   pip install -r requirements.txt
   pip install -r docs/requirements.txt
   make clean html


This will build you a documentation in folder build. Documentation is in html format.

If you want to test documentation you can run command in same folder:

.. code:: bash

   make doctest


This will show you result of doctest. All tests and doctest are tested at Travis CI

License
######


This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for more details.






