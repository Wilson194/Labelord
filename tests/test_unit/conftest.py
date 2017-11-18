import pytest
import betamax
import os
from labelord.github import LabelUpdater
from labelord.github import MyAuth
import configparser
import json

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
CONFIGS_PATH = os.path.join(ABS_PATH, 'fixtures', 'configs')
CASSETTES_PATH = os.path.join(ABS_PATH, 'fixtures', 'cassettes')


def load_auth_file(path):
    cfg = configparser.ConfigParser()
    cfg.read(path)

    token = cfg.get('github', 'token')

    return token


with betamax.Betamax.configure() as config:
    if 'LABELORD_AUTH' in os.environ:

        TOKEN = load_auth_file(os.environ.get('LABELORD_AUTH'))

        config.default_cassette_options['record_mode'] = 'once'
    else:
        TOKEN = 'DoYouThinkThatThisIsToken'

        config.default_cassette_options['record_mode'] = 'none'

    config.cassette_library_dir = CASSETTES_PATH

    config.define_cassette_placeholder('<TOKEN>', TOKEN)


@pytest.fixture
def label_updater_client(betamax_parametrized_session):
    if 'LABELORD_AUTH' in os.environ:
        auth = MyAuth(TOKEN)
        betamax_parametrized_session.auth = auth
    return LabelUpdater(betamax_parametrized_session, None, {})


@pytest.fixture
def labelord_session(betamax_parametrized_session):
    if 'LABELORD_AUTH' in os.environ:
        auth = MyAuth(TOKEN)
        betamax_parametrized_session.auth = auth
    return betamax_parametrized_session


@pytest.fixture
def utils():
    return Utils()


@pytest.fixture
def flask_test_app():
    from labelord import app
    app.config['TESTING'] = True
    return app.test_client()


class Utils:
    def find_label(self, labels, name=None, color=None):
        for label in labels:
            if label.name == name and label.color.lower() == color.lower():
                return 2
            elif label.name == name:
                return 1

        return 0


    def load_config(self, path):
        cfg = configparser.ConfigParser()
        cfg.read(path)

        return cfg
