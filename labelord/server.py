import hashlib
import hmac
import os
import sys

import flask
import jinja2
import requests

from labelord import github


server = flask.Blueprint('server', __name__, template_folder='templates')


class LabelordWeb(flask.Flask):
    """
    Custom class for app, extend flask.Flask
    """


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.session = None
        self.labelordConfig = None
        self.repos = None
        self.secret = None
        self.updatedRepos = []
        self.lastAction = None


    def inject_session(self, session):
        """
        Inject session to current app (for testing)
        :param session: session class
        :return: None
        """
        self.session = session


    def set_labelord_config(self, config):
        """
        Setter for config
        :param config: config object
        :return: None
        """
        self.labelordConfig = config


    def reload_config(self):
        """
        Reload config from system variable
        :return: None
        """
        configPath = os.getenv('LABELORD_CONFIG', 'config.cfg')

        self.labelordConfig = github.load_config(configPath)

        token = github.load_token(self.labelordConfig, '')

        auth = github.MyAuth(token)
        self.session.auth = auth

        labelUpdater = github.LabelUpdater(self.session, self.labelordConfig, {})
        repos = labelUpdater.get_target_repositories()

        if self.labelordConfig.get('github', 'webhook_secret', fallback=None) is None:
            sys.stderr.write('No webhook secret has been provided\n')
            quit(8)


@server.route('/', methods=['GET', 'POST'])
def index():
    myApp = flask.current_app
    if myApp.session is None:
        token = github.load_token(myApp.labelordConfig, '')

        auth = github.MyAuth(token)
        session = requests.Session()
        session.headers = {'User-Agent': 'Python'}
        session.auth = auth

        myApp.session = session

    if flask.request.method == 'POST':
        return post_request()
    else:
        session = myApp.session

        labelUpdater = github.LabelUpdater(session, myApp.labelordConfig, {})
        repos = labelUpdater.get_target_repositories()
        return flask.render_template('index.html', repos=repos)


# @server.template_filter('gitLink')
def convert_time(text):
    """Convert the time format to a different one"""

    return jinja2.Markup('<a href="https://github.com/' + text + '">' + text + '</a>')


#################################################################################
#  functions for label handling

def post_request():
    """
    Request handler for POST method
    :return:
    """
    myApp = flask.current_app
    cfg = myApp.labelordConfig

    headers = flask.request.headers

    rawData = flask.request.data

    js = flask.request.get_json()

    # Validate header action
    if headers['X-GitHub-Event'] == 'ping':
        return 'Everything is OK'

    elif headers['X-Github-Event'] == 'label':
        pass

    else:
        flask.abort(400)

    # Check signature
    if 'X-Hub-Signature' not in headers:
        return flask.abort(401)
    shaSignature = headers['X-Hub-Signature'].replace('sha1=', '')
    correct = check_signature(rawData, cfg.get('github', 'webhook_secret'), shaSignature)
    if not correct:
        return flask.abort(401)

    if not check_allowed_repo(js['repository']['full_name']):
        return flask.abort(400)

    if js['action'] != myApp.lastAction:
        myApp.updatedRepos = []
        myApp.lastAction = js['action']

    if js['action'] == 'created':
        create_label_request(js)

    elif js['action'] == 'edited':
        edit_label_request(js)

    elif js['action'] == 'deleted':
        delete_label_request(js)

    return 'Nothing is happend'


def check_allowed_repo(repo):
    """
    Check if repo is allowed in config
    :param repo: repository string
    :return: True if allowed, False otherwise
    """
    myApp = flask.current_app
    session = myApp.session

    labelUpdater = github.LabelUpdater(session, myApp.labelordConfig, {})
    repos = labelUpdater.get_target_repositories()

    if repo in repos:
        return True
    else:
        return False


def edit_label_request(js):
    """
    Handle POST edit label
    :param js: json request object
    :return: None
    """
    myApp = flask.current_app
    session = myApp.session

    if js['repository']['full_name'] in myApp.updatedRepos:
        myApp.updatedRepos.remove(js['repository']['full_name'])
        return

    labelUpdater = github.LabelUpdater(session, myApp.labelordConfig, {})
    repos = labelUpdater.get_target_repositories()

    sourceRepo = js['repository']['full_name']

    newLabel = github.Label(js['label']['name'], js['label']['color'])

    oldLabel = github.Label(js['changes']['name']['from'] if 'name' in js['changes'] else js['label']['name'],
                            js['changes']['color']['from'] if 'color' in js['changes'] else js['label']['color'])

    if sourceRepo in repos:
        repos.remove(sourceRepo)

    for repo in repos:
        myApp.updatedRepos.append(repo)
        labelUpdater.update_label(repo, newLabel, oldLabel)


def delete_label_request(js):
    """
    Handle POST delete label
    :param js: json request object
    :return: None
    """
    myApp = flask.current_app
    session = myApp.session

    if js['repository']['full_name'] in myApp.updatedRepos:
        myApp.updatedRepos.remove(js['repository']['full_name'])
        return

    labelUpdater = github.LabelUpdater(session, myApp.labelordConfig, {})
    repos = labelUpdater.get_target_repositories()

    sourceRepo = js['repository']['full_name']

    label = github.Label(js['label']['name'], js['label']['color'])

    if sourceRepo in repos:
        repos.remove(sourceRepo)

    for repo in repos:
        myApp.updatedRepos.append(repo)
        labelUpdater.remove_label(repo, label)


def create_label_request(js):
    """
    Handle POST create label
    :param js: json request object
    :return: None
    """
    myApp = flask.current_app
    session = myApp.session

    if js['repository']['full_name'] in myApp.updatedRepos:
        myApp.updatedRepos.remove(js['repository']['full_name'])
        return

    labelUpdater = github.LabelUpdater(session, myApp.labelordConfig, {})
    repos = labelUpdater.get_target_repositories()

    sourceRepo = js['repository']['full_name']

    label = github.Label(js['label']['name'], js['label']['color'])

    if sourceRepo in repos:
        repos.remove(sourceRepo)

    for repo in repos:
        # myApp.updatedRepos.append(repo)
        labelUpdater.add_label(repo, label)


def check_signature(msg, secret, signature):
    """
    Check sha1 sum
    :param msg: body message
    :param secret: secret from config
    :param signature: signature from GitHub header
    :return: True if checked, False otherwise
    """
    hash = hmac.new(secret.encode(), msg, hashlib.sha1)
    if signature == hash.hexdigest():
        return True
    else:
        return False
