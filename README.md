# Labelord application

This is project for controlling, creating and cloning GitHub issues labels (based on FIT CUT MI-PYT project)


----


### This application allows you:

* List repositories of given connection
* List labels of target repo
* Create/update/delete label at target repo
* Replicate labels through selected repositories


### Config

For correct running of this application, you need to fill in config file. Default config is `config.cfg`.
You can find example of config in `default_config.cfg`. You need to specify GitHub
token for you GitHub account. Next configuration is for setting up application behaviour.
See `default_config.cfg` comments.


### Usage
There are 4 basic commands for this application. You can find all commands and parameters
with `labelord --help`.

Basic commands:
* labelord list_repos - list all repositories in GitHub account
* labelord list_labels [repo] - list all labels in repository
* labelord run [mode[] - run editing of labels based on config
* labelord run_server - run replication webserver  

### Pypi
You can find this project at testing Pypi at address [https://test.pypi.org/project/labelord-horacj10/](Pypi) 

### License


This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for more details.






