Basic usage
############

Labelord have two different parts. First part is console application. With this console you can manage labels at repositories.
you can delete labels, create new labels or edit some labels. You can specify this in config file or use console arguments.
But all the changes you must do manually.

Second part is web server. This server is used for accepting GitHub webhooks and based on this webhooks replicate labels between
two or more repositories.

Console
=======

The main entrypoint for console application is command **labelord**. When you run only **labelord** without any parameters,
you will get help.

.. note::
    You must have activated virtual enviroment and after that just type ``python -m labelord``

Main command could have some parameters which are same for every command:

* **-c / --config [path]** - with this parameter you could specify path to config file. Default is config.cfg in current directory.
* **-t / --token [token]** - with this parameter you could specify GitHub API token

Token must be specified (in config file or by token parameter). Next you could chose from 3 commands.


list_repos
----------

This command is used for get list of repositories, which you enable. This command will check config file and read all enabled
repositories. After that check if you have access for this repositories and print all enabled repositories.

.. hint::
    ``python -m labelord -t my_secret_token list_repos`` will show list of repositories



list_labels
-------------

This command is used for get list of all labels in one repository. For this command you must specify target repository.
You can specify this as first argument of command. If you don't have permission for this repository or this repository
don't exist, program will show error message. Repository is specified in format **user_name/repository_name**.

.. hint::
    ``python -m labelord -t my_secret_token list_labels dummyUser/HelloWorld`` will show list of label in HelloWorld repository


run
----

This is main command for labels editing. With this command you can create labels, delete labels or edit some labels.
This command accept many optional arguments which defining behaviour of command:

* **-t / --template-repo [repo]** - with this argument you can specify repository, which will be used as template. All definitions of labels will be get from this repo. Just read all repos in this repo.
* **-a / --all-repos** - if this flag is set, command will ignore settings in config.cfg in section repos and editing labels will be done in all user repositories
* **-q / --quiet** - if this flag is set, program print nothing to console
* **-v / --verbose** - if this flag is set, program will print more informations about run. (done commands, errors, etc.)
* **-d / --dry-run** - if this flag is set, all command wil not affect any repository. Just print some informations about commands.

Next you must specify mode. This mode is first parameter of command. You can chose from two:

* **update** - if you select this mode, all new labels will be created, labels with different color will be changed and all other labels will not change
* **replace** - if you select this mode, all new labels will be created, labels with different color will be changed and **all other labels that are not in template will be deleted!**

After run this command, summary output will be printed in command line.

.. hint::
    ``python -m labelord -t my_secret_token run -a -v update`` will update labels in all my repositories based on config file and
    some debug info will be printed to console


Example of verbose output

.. code::

    [ADD][SUC] Wilson194/hello_world; label1; FFAA00
    [ADD][SUC] Wilson194/hello_world; label2; CCAAFF
    [ADD][SUC] Wilson194/hello_world; label3; 00BBCC
    [DEL][SUC] Wilson194/hello_world; bug; fc2929
    [DEL][SUC] Wilson194/hello_world; DefinitelyNotAPorn; FF0000
    [DEL][SUC] Wilson194/hello_world; duplicate; cdcdcd
    [DEL][SUC] Wilson194/hello_world; enhancement; 84b6eb
    [DEL][SUC] Wilson194/hello_world; help wanted; 159818
    [DEL][SUC] Wilson194/hello_world; invalid; e6e6e6
    [DEL][SUC] Wilson194/hello_world; ItsATrap; FF0000
    [DEL][SUC] Wilson194/hello_world; new fantastic label; 0e8a16
    [DEL][SUC] Wilson194/hello_world; question; cc317c
    [DEL][SUC] Wilson194/hello_world; Won't fix; 888888
    [DEL][SUC] Wilson194/hello_world; wontfix; ffffff
    [SUMMARY] 1 repo(s) updated successfully


.. tip:: first [] show command, second [] show result of this command, next is name of repository and last is name of label. Last line is summary


Server
======

This is part of modelu for server. You can run your own server on your computer, there is problem with forwarding packet to your computer.
Much better is deploy application to some server like `PythonAnywhere <https://www.pythonanywhere.com/>`.

Run the server is very simple. Just type to console:

``python -m labelord run_server``

If no parameters are set, server will start in default mode at localhost at port 5000. The config file must be correctly filled.
You must specify webhook_secret, github token and target repositories. When you open webpage, you will see some informations
about application and all traced repositories. If you create webhook at GitHub that dirrecting request to this IP, server
start replicating labels from this repo to all selected repositories.

You can change some behaviour of server with parameters:

* **-h / --host [ip]** - with this parameter, you can change ip of created server
* **-p / --port [port]** - with this parameter, you can change port of created server
* **-d / --debug** - with this parameter you enable debug mode of Flask, which writing some debug informations
