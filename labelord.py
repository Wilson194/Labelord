# This is skeleton for labelord module
# MI-PYT, task 1 (requests+click)
# File: labelord.py
# TODO: create requirements.txt and install
import click
import requests
import configparser
import sys


class MyAuth(requests.auth.AuthBase):
    """
    Class for authentication of requests
    """


    def __init__(self, token):
        self.token = token


    def set_token(self, token):
        self.token = token


    def __call__(self, req):
        req.headers['Authorization'] = 'token ' + self.token
        return req


class Label:
    """
    Class for one label
    """


    def __init__(self, name, color):
        self.name = name
        self.color = color


    def __iter__(self):
        return self.name


    def __repr__(self):
        return '<Class label> {} - {}'.format(self.name, self.color)


    def __hash__(self):
        return hash((self.name, self.color))


class LabelUpdater:
    """
    Class for updating labels, for more readable code
    """


    def __init__(self, session, config, runConfig):
        """
        :param session: Authenticated session
        :param config: config object from parsed .ini file
        :param runConfig: dictionary with parameters from console
        """
        self.session = session
        self.config = config
        self.allRepos = runConfig['allRepos']
        self.dry = runConfig['dryRun']
        self.verbose = runConfig['verbose']
        self.quiet = runConfig['quiet']
        self.mode = runConfig['mode']
        self.errorNum = 0
        self.reposNum = 0


    def get_source_labels(self, repository):
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


    def get_target_repositories(self):
        """
        Get list of target repositories, where update will be used
        First check parameter -a/--all_repos (use all accesable repos)
        Second try list of repos from repos section in config file
        If not found, quit with exit code 7
        :return: list of repos / quit(7)
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


    def print_summary(self):
        """
        Print summary line based on -q/--quit and -v/--verbose parameters
        Each of them have another format
        If there were some errors, quit with exit code 10
        :return: None / quit(10)
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


    def print_log(self, repository, operationType, label, error):
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


    def update_labels(self, newLabels, targetRepositories):
        """
        Change labels in given repositories
        :param newLabels: list of new labels
        :param targetRepositories: list of target repositories
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


    def add_label(self, repository, label):
        """
        Add label to repository
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


    def update_label(self, repository, label, oldLabel=None):
        """
        Update existing label in repository
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


    def remove_label(self, repository, label):
        """
        Remove label from repository
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


def find_label(label, iterable):
    """
    Find class Label in list of Label classes
    :param label: searched label
    :param iterable: list of labels
    :return: (it, type)
                    it -> founded old label
                    type -> type of match
                        0 -> not found
                        1 -> name found, other color
                        2 -> name found, same color
                        3 -> name different case
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


def load_config(cfg):
    """
    Load .cfg file
    :param cfg: path to config file
    :return: config file Object
    """
    config = configparser.ConfigParser()

    config.optionxform = str
    config.read(cfg)

    return config


def load_token(config, token):
    # Load token
    if not token:
        token = config.get('github', 'token', fallback=False)

    # Token not set
    if not token:
        sys.stderr.write('No GitHub token has been provided\n')
        quit(3)

    return token


def validate_response(response, exitProgram=True):
    """
    Validate response
    :param response: response object from session
    :param exitProgram: if false, quit will be supprested
    :return: error code / quit with correct code
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


@click.group('labelord')
@click.option('-c', '--config', default='config.cfg', type=click.Path(), help='Specify path to config file.')
@click.option('-t', '--token', envvar='GITHUB_TOKEN', type=str, help='Token for GitHub API.')
@click.version_option('labelord, version 0.1')
@click.pass_context
def cli(ctx, config, token):
    """
    Main program group
    :param ctx: context for object passing
    :param config: path to config file, default config.cfg
    :param token: GITHUB token
    :return: None
    """
    # Create session
    session = ctx.obj.get('session', requests.Session())
    session.headers = {'User-Agent': 'Python'}

    ctx.obj['session'] = session
    ctx.obj['token'] = token
    ctx.obj['config'] = config


def get_list_repos(session):
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


@cli.command()
@click.pass_context
def list_repos(ctx):
    """
    Command for repositories list
    :param ctx: context
    :return: None
    """

    session = ctx.obj['session']

    # Load config
    config = load_config(ctx.obj['config'])

    token = load_token(config, ctx.obj['token'])

    # Set auth
    auth = MyAuth(token)
    session.auth = auth

    repositories = get_list_repos(session)

    for repo in repositories:
        print(repo)


def get_list_labels(session, repository, exitProgram=True):
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


@cli.command()
@click.pass_context
@click.argument('repository', nargs=1)
def list_labels(ctx, repository):
    """
    List of labels from repository
    :param ctx: context
    :param repository: name if repository
    :return: None
    """
    session = ctx.obj['session']

    # Load config
    config = load_config(ctx.obj['config'])

    token = load_token(config, ctx.obj['token'])

    # Set auth
    auth = MyAuth(token)
    session.auth = auth

    labels = get_list_labels(session, repository)

    for label in labels:
        print('#{} {}'.format(label.color, label.name))


@cli.command()
@click.option('-t', '--template-repo', 'sourceRepository', help='Source repository for labels')
@click.option('-a', '--all-repos', 'allRepos', is_flag=True, help='Use all available repository')
@click.option('-q', '--quiet', 'quiet', is_flag=True, help='Quit print, no output to console')
@click.option('-v', '--verbose', 'verbose', is_flag=True, help='Debug info to console')
@click.option('-d', '--dry-run', 'dryRun', is_flag=True, help='Run only testing instation, no changes at repos')
@click.argument('mode', nargs=1, type=click.Choice(['update', 'replace']))
@click.pass_context
def run(ctx, sourceRepository, allRepos, mode, quiet, verbose, dryRun):
    """
     Main program for copy labels and update labels
    :param ctx: context
    :param sourceRepository: source repository for source labels
    :param allRepos: flag if all repos should be updated
    :param mode: mode -> update / replace
    :param quiet: flag for quit mode
    :param verbose: flag for verbose mode
    :param dryRun: flag for dryRun mode
    :return: None
    """
    session = ctx.obj['session']
    runConfig = {
        'allRepos': allRepos,
        'mode'    : mode,
        'quiet'   : quiet,
        'verbose' : verbose,
        'dryRun'  : dryRun
    }

    # Load config
    config = load_config(ctx.obj['config'])
    token = load_token(config, ctx.obj['token'])

    # Set auth
    auth = MyAuth(token)
    session.auth = auth

    lu = LabelUpdater(session, config, runConfig)

    sourceLabels = lu.get_source_labels(sourceRepository)

    targetRepositories = lu.get_target_repositories()

    lu.update_labels(sourceLabels, targetRepositories)


if __name__ == '__main__':
    cli(obj={})
