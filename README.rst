#####################
Labelord application
#####################

[![Build Status](https://travis-ci.com/Wilson194/Labelord.svg?token=PdLqtPfyXNo5KfhxbzAS&branch=v0.4.2)](https://travis-ci.com/Wilson194/)


This is project for controlling, creating and cloning GitHub issues labels (based on FIT CUT MI-PYT project)


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

Whole docummentation you can find at this page. If you want to build documentation at your computer just write
this command in folder docs:

.. code:: bash

   make clean html


This will build you a documentation in folder build. Documentation is in html format.

If you want to test documentation you can run command in same folder:

.. code:: bash

   make doctest


This will show you result of doctest. All tests and doctest are tested at Travis CI

License
######


This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for more details.






