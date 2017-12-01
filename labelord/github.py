import requests
import configparser
import sys
import string
from typing import Union


class MyAuth(requests.auth.AuthBase):
    """
    Class for authentication of requests

    :ivar token: authentication token for GitHub
    :vartype token: str
    """


    def __init__(self, token: str):
        self.token = token


    def set_token(self, token: str):
        """
        Set token to class auth

        :param token: GitHub token
        :type token: str
        """
        self.token = token


    def __call__(self, req):
        req.headers['Authorization'] = 'token ' + self.token
        return req


class Label:
    """
    Class that handle one github label.

    :ivar name: Name of label
    :vartype name: str
    :ivar color: Color of label in hexadecimal format
    :vartype color: str
    """


    def __init__(self, name, color):
        if not all(c in string.hexdigits for c in color):
            raise ValueError('Label color must be hexadecimal number')
        if len(color) != 6:
            raise ValueError('Label color must have 6 digit! (RGB in hexadecimal)')
        self.name = name
        self.color = color


    def __eq__(self, other):
        return self.name == other.name and self.color == other.color


    def __iter__(self):
        return self.name


    def __repr__(self):
        return '<Class label> {} - {}'.format(self.name, self.color)


    def __hash__(self):
        return hash((self.name, self.color))


class LabelUpdater:
    """
    Class that handle all communication with GitHub api.

    :ivar session: authenticated connection session with GitHub
    :vartype session: Session
    :ivar config: Config object with loaded labelord config
    :vartype config: Config
    :ivar runConfig: dictionary with all arguments from console
    :vartype runConfig: dict
    """


    def __init__(self, session, config, runConfig):
        self.session = session
        self.config = config
        self.allRepos = runConfig.get('allRepos', None)
        self.dry = runConfig.get('dryRun', None)
        self.verbose = runConfig.get('verbose', None)
        self.quiet = runConfig.get('quiet', None)
        self.mode = runConfig.get('mode', None)
        self.errorNum = 0
        self.reposNum = 0


    def get_source_labels(self, repository: str) -> list:
        """
        Return source labels (how target repository should have)
        First use -t/--template_repo (even it was empty)
        Next try template-repo from config file from others section
        Last one is labels section in config file

        :param repository: repository from -t/--template-repo parameter
        :return: list of Label classes
        """
        labels = []

        if repository:
            labels = get_list_labels(self.session, repository)
            return labels

        if 'others' in self.config and 'template-repo' in self.config['others']:
            labels = get_list_labels(self.session, self.config['others']['template-repo'])

        if labels:
            return labels

        if 'labels' in self.config:
            for label in self.config['labels']:
                newLabel = Label(label, self.config['labels'][label])
                labels.append(newLabel)
            return labels

        sys.stderr.write('No labels specification has been found\n')
        quit(6)


    def get_target_repositories(self) -> list:
        """
        Get list of target repositories, where update will be used
        First check parameter -a/--all_repos (use all accesable repos)
        Second try list of repos from repos section in config file
        If not found, quit with exit code 7

        :return: list of repos
        :raises SystemExit: if not repos found
        """
        if self.allRepos:
            repos = get_list_repos(self.session)
            return repos

        repos = []
        if 'repos' in self.config:
            for key in self.config['repos']:
                if self.config['repos'].getboolean(key):
                    repos.append(key)
            return repos

        sys.stderr.write('No repositories specification has been found\n')
        quit(7)


    def print_summary(self) -> None:
        """
        Print summary line based on -q/--quit and -v/--verbose parameters
        Each of them have another format
        If there were some errors, quit with exit code 10

        :return: None
        :raises SystemExit: if there is some error
        """
        if self.quiet and self.verbose:
            if self.errorNum == 0:
                print('SUMMARY: {} repo(s) updated successfully'.format(self.reposNum))
            else:
                print('SUMMARY: there were {} errors, please error check log'.format(self.errorNum))
                quit(10)
        elif not self.quiet and not self.verbose:
            if self.errorNum == 0:
                print('SUMMARY: {} repo(s) updated successfully'.format(self.reposNum))
            else:
                print('SUMMARY: {} error(s) in total, please check log above'.format(self.errorNum))
                quit(10)
        elif self.verbose:
            if self.errorNum == 0:
                print('[SUMMARY] {} repo(s) updated successfully'.format(self.reposNum))
            else:
                print('[SUMMARY] {} error(s) in total, please check log above'.format(self.errorNum))
                quit(10)
        elif self.quiet and self.errorNum != 0:
            quit(10)


    def print_log(self, repository: str, operationType: str, label: Label, error: str) -> None:
        """
        Print one log line

        :param repository: Repository specification
        :param operationType: Operation type (UPD,DEL,ADD)
        :param label: Label class with new label
        :param error: error message, if there war some error
        :return: None
        """
        if self.verbose:
            if not self.quiet:
                if self.dry:
                    res = 'DRY'
                elif error is not None:
                    res = 'ERR'
                else:
                    res = 'SUC'

                errorText = '; {}'.format(error) if error is not None else ''
                print('[{}][{}] {}; {}; {}{}'.format(operationType, res, repository, label.name, label.color, errorText))

        if not self.verbose and not self.quiet and error is not None:
            sys.stderr.write('ERROR: {}; {}; {}; {}; {}\n'.format(operationType, repository, label.name, label.color, error))


    def update_labels(self, newLabels: list, targetRepositories: list) -> None:
        """
        Change labels in given repositories

        :param newLabels: list of new labels
        :param targetRepositories: list of target repositories
        :return: None
        """
        for repository in targetRepositories:
            oldLabels = get_list_labels(self.session, repository, False)

            if type(oldLabels) is not list:
                self.errorNum += 1
                if not self.quiet:
                    if not self.verbose:
                        sys.stderr.write('ERROR: LBL; {}; {}\n'.format(repository, '404 - Not Found'))
                    else:
                        print('[LBL][ERR] {}; {}'.format(repository, '404 - Not Found'))
                continue

            self.reposNum += 1

            for label in newLabels:
                it, sim = find_label(label, oldLabels)

                if sim != 0:
                    oldLabels.remove(it)

                if sim == 0:
                    self.add_label(repository, label)

                elif sim == 1:
                    self.update_label(repository, label)

                elif sim == 3:
                    self.update_label(repository, label, it)

            if self.mode == 'replace':
                for label in oldLabels:
                    self.remove_label(repository, label)

        self.print_summary()


    def add_label(self, repository: str, label: Label) -> None:
        """
        Add label to repository, if there is some error, increase error counter

        :param repository: target repository
        :param label: class Label with new label
        :return: None
        """
        userName, repoName = repository.split('/')
        error = None

        if not self.dry:
            r = self.session.post('https://api.github.com/repos/{}/{}/labels'.format(userName, repoName),
                                  json={'name': label.name, 'color': label.color})

            if r.status_code != 201:
                error = '{} - {}'.format(r.status_code, r.json()['message'])
                self.errorNum += 1

        self.print_log(repository, 'ADD', label, error)


    def update_label(self, repository: str, label: Label, oldLabel: Label = None) -> None:
        """
        Update existing label in repository, if there is some error, increase error counter

        :param repository: target repository
        :param label: class Label with new Label
        :param oldLabel: class Label with old label, if change only case in name of label
        :return: None
        """
        userName, repoName = repository.split('/')
        error = None
        labelName = oldLabel.name if oldLabel is not None else label.name
        if not self.dry:
            r = self.session.patch('https://api.github.com/repos/{}/{}/labels/{}'.format(userName, repoName, labelName),
                                   json={'color': label.color, 'name': label.name})

            if r.status_code != 200:
                error = '{} - {}'.format(r.status_code, r.json()['message'])
                self.errorNum += 1

        self.print_log(repository, 'UPD', label, error)


    def remove_label(self, repository: str, label: Label) -> None:
        """
        Remove label from repository, if there is some error, increase error counter

        :param repository: target repository
        :param label: class Label, which should be deleted
        :return: None
        """
        userName, repoName = repository.split('/')
        error = None
        if not self.dry:
            r = self.session.delete('https://api.github.com/repos/{}/{}/labels/{}'.format(userName, repoName, label.name))

            if r.status_code != 204:
                error = '{} - {}'.format(r.status_code, r.json()['message'])
                self.errorNum += 1

        self.print_log(repository, 'DEL', label, error)


def find_label(label: Label, iterable: list) -> tuple:
    """
    Find class Label in list of Label classes

    * it -> founded old label
    * type -> type of match
       * 0 -> not found
       * 1 -> name found, other color
       * 2 -> name found, same color
       * 3 -> name different case

    :param label: searched label
    :param iterable: list of labels
    :return: tuple (it, type)
    """
    for it in iterable:
        if label.name == it.name:
            if label.color == it.color:
                return it, 2
            else:
                return it, 1
        if label.name.lower() == it.name.lower():
            return it, 3

    return None, 0


def load_config(cfg: str) -> configparser.ConfigParser:
    """
    Load .cfg file and parse to Config object

    :param cfg: path to config file
    :return: config file Object
    """
    config = configparser.ConfigParser()

    config.optionxform = str
    config.read(cfg)

    return config


def load_token(config: configparser.ConfigParser, token: str) -> str:
    """
    Load token from config file, if token given by parameter, just return this string

    :param config: config file object
    :param token: token string
    :return: token
    :raises SystemExit: if no token found
    """
    # Load token
    if not token:
        token = config.get('github', 'token', fallback=False)

    # Token not set
    if not token:
        sys.stderr.write('No GitHub token has been provided\n')
        quit(3)

    return token


def validate_response(response: requests.Response, exitProgram: bool = True) -> int:
    """
    Validate response by status code

    * 401 - code 4
    * 404 - code 5
    * response.ok == False - code 10

    :param response: response object from session
    :param exitProgram: if false, quit will be supprested
    :return: error code
    :raises SystemExit: if exitProgram is tru
    """
    if response.status_code == 401:
        if exitProgram:
            sys.stderr.write('GitHub: ERROR 401 - Bad credentials\n')
            quit(4)
        else:
            return 4

    if response.status_code == 404:
        if exitProgram:
            sys.stderr.write('GitHub: ERROR 404 - Not Found\n')
            quit(5)
        else:
            return 5

    if not response.ok:
        if exitProgram:
            sys.stderr.write(response.text)
            quit(10)
        else:
            return 10

    return 0


def get_list_repos(session: requests.Session) -> list:
    """
    Get list of available repos

    :param session: authenticated session
    :return: list of available repos
    """
    reposList = []
    page = 1
    while True:
        r = session.get('https://api.github.com/user/repos?per_page=100&page={}'.format(page))

        validate_response(r)

        repositories = r.json()
        for repo in repositories:
            reposList.append(repo['full_name'])

        if len(repositories) == 100:
            page += 1
        else:
            break

    return reposList


def get_list_labels(session: requests.Session, repository: str, exitProgram: bool = True) -> Union[list, bool]:
    """
    Get list of labels in given repository

    :param session: authenticated session
    :param repository: target repository
    :param exitProgram: if False, program will not quit if repository not found, only return False
    :return: list of Labels / False
    """
    labelsList = []
    userName, repoName = repository.split('/')
    page = 1
    while True:
        r = session.get('https://api.github.com/repos/{}/{}/labels?per_page=100&page={}'.format(userName, repoName, page))

        exitStatus = validate_response(r, exitProgram)

        if exitStatus:
            return False

        labelsJson = r.json()

        for one in labelsJson:
            labelsList.append(Label(one['name'], one['color']))

        # Check, if there is 100 labels and we need try another page
        if len(labelsJson) != 100:
            break
        else:
            page += 1

    return labelsList
