Using like API
===============

If you want to use this module as part of your application, you can. In this part of documentation i will try
describe main functions, which help you integrate this module to your application.


Basic structure
----------------

Module is divided to three parts:

* labelord - which enable running this module from console
* server - which creating web server
* github - which doing all magic with GitHub API

If you want to use this module as part of your code, you will probably use only github part.
I don't recommend you using labelord console as entry point to this module. It's really bad idea.
Much better solution is use directly functions and classes from github part.


Setup main class
-----------------

The main class ``LabelUpdater`` handle all action with GitHub, so you need to initialize this class.
Class constructor accept tree parameters:

* **session** - this is session with correct authetication for GitHub
* **config** - loaded config file (you can use load_config function
* **runConfig** - dictionary of parameters, which changing behaviour of class
   * allRepos - bool
   * dryRun - bool
   * verbose - bool
   * quiet - bool
   * mode - str (update/replace)

.. testcode::

   import labelord.github
   import requests

   s = requests.Session()
   cfg = labelord.github.load_config('_static/default_config.cfg')
   lu = labelord.github.LabelUpdater(s,cfg,{'allRepos':True, 'mode':'update'})
   print(lu.allRepos)
   print(lu.mode)

.. testoutput::

   True
   update



Your session must have correct authentication. You can use created class for authentication MyAuth. This class need only github token,
you can specify token in constructor and anytime you can change it with setter ``set_token(token:str)``

.. testcode::

   import labelord.github
   auth = labelord.github.MyAuth('secret_token')
   auth.set_token('new_secret_token')

   print(auth.token)

.. testoutput::

   new_secret_token



New you have all initialized and you can start using API. There are several other functions that could help you:


get_list_repos(session)
************************

This function will return list of all repos, which you can find with current GitHub secret

For example:

.. code:: python


   import labelord.github

   repos = labelord.github.get_list_repos(session)
   print(repos)

will return list of repositories. If don't specify token or something goes wrong, system will raise SystemExit

get_list_labels(session, repository)
**************************************

This function will return list of label in one repository. You must specify session and name of repository.

For example:

.. code:: python

   import labelord.github

   repos = labelord.github.get_list_labels(session, 'dumpUser/HelloWorld')
   print(repos)

will return list of labels of selected repository. List is list of class Label, described later.



Label class
-------------


For save label to one object there is class Label. Constructor need name and color of label, both parameters are strings.
Name could have spaces and color is hexadecimal value of RGB color (without hashtag). Be careful, color is case sensitive
(same color but could create more edit actions)

Example usage of class:

.. testcode::

   import labelord.github

   label = labelord.github.Label('Bug', 'FF0000')
   label2 = labelord.github.Label('Bug', 'ff0000')
   print(label.name)
   print(label.color)
   print(label == label2)

.. testoutput::

   Bug
   FF0000
   False


Label class have some controls of color (correct color format), some you need only catch exceptions if for example user will specify labels

Example:

.. testcode::

   import labelord.github

   try:
       label = labelord.github.Label('Bug', 'HH0000')
   except ValueError as e:
       print(str(e))


   try:
       label = labelord.github.Label('Bug', 'FF0000FF')
   except ValueError as e:
       print(str(e))


.. testoutput::

   Label color must be hexadecimal number
   Label color must have 6 digit! (RGB in hexadecimal)


Using LabelUpdater class
-------------------------

Main class have some functions, which you can use. All functions are documented in module documentation.
There I will only write interesting ones.


get_source_labels(repository)
******************************

This function accept string name of repository and return list of labels of that repository. If repository is not set, try to
find source repository in config. If source repository is not in config, load labels from config. If labels not in config,
function exit with error


get_target_repositories()
**************************

Based on parameters and config file will return list of target repositories (list of strings)


update_labels(newLabels,targetRepositories)
*********************************************

This function will update labels in target repositories. NewLabels is list of classes Label.
Function connect to repository and based on mode, create/update/delete all necessary labels.


