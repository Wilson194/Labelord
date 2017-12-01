Config file
============

All behaviour could be defined in config file. Example of config file is located in GitHub.

.. literalinclude:: _static/default_config.cfg

[github]
---------
In this section you can specify information about GitHub authorization.

token
*******
This option is for specify GitHub token. Where you can find GitHub token is specified in
GitHub section.

webhook_secret
***************
This option is for specify GitHub webhook secret. Where you can find webhook_secret and what
is webhook you can find in section GitHub.


[labels]
---------
This section is for specify custom labels. That should be created in repositories.
The syntax is very simple:

name = color

Name could have spaces. color is hexadecimal RGB value of color.
You can specify as many labels as you want. All labels will be created.

[repos]
--------
In this section you can specify repositories, in which all operations should be done.
The syntax is very simple:

user/repository = yes

           or

user/repository = no

* **user** - name of owner of repository
* **repository** - name of repository
* **yes/no** - specify, if this repository should be enable for editing.



[other]
--------
In this section are located all other settings

template-repo
**************
This option is for specify source repository. From this repository will be loaded
all labels and will be used as template. You can specify only one source repository.
