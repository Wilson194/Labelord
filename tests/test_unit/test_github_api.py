import pytest
from labelord import github
import os
import flexmock


ABS_PATH = os.path.abspath(os.path.dirname(__file__))
CONFIGS_PATH = os.path.join(ABS_PATH, 'fixtures', 'configs')


def test_github_label_class_correct_label():
    label = github.Label('Bug', 'FF0000')

    assert label.color == 'FF0000'
    assert label.name == 'Bug'


def test_github_invalid_label():
    with pytest.raises(ValueError):
        github.Label('Bug', 'GG0000')

    with pytest.raises(ValueError):
        github.Label('Bug', 'red')


def test_find_labels_find_correct_label():
    l1 = github.Label('Bug', 'FF0000')
    l2 = github.Label('Enchantment', '0000FF')
    l3 = github.Label('Correct', '00FF00')
    l4 = github.Label('Stupidity', 'FFFF00')
    l5 = github.Label('Bug', 'EE0000')
    l6 = github.Label('BUG', 'FF0000')

    labels = (l1, l2, l3)

    # same labels => 2
    assert github.find_label(l1, labels) == (l1, 2)

    # same name, other color => 1
    assert github.find_label(l5, labels) == (l1, 1)

    # same color, same name but different case
    assert github.find_label(l6, labels) == (l1, 3)

    # label not found
    assert github.find_label(l4, labels) == (None, 0)


def test_config_file_loader():
    cfg = github.load_config(os.path.join(CONFIGS_PATH, 'dummy.cfg'))

    assert cfg.get('github', 'token') == 'ItsATrapTrustMe'

    assert len(cfg.sections()) == 1


def test_load_token_with_not_token_given():
    import configparser
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIGS_PATH, 'dummy.cfg'))

    assert github.load_token(config, None) == 'ItsATrapTrustMe'


def test_load_token_with_given_token():
    import configparser
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIGS_PATH, 'dummy.cfg'))

    assert github.load_token(config, 'WhatIsThisTokenFor') == 'WhatIsThisTokenFor'


def test_validate_response_that_return_correct_codes():
    with pytest.raises(SystemExit) as pytest_wrapped_401:
        github.validate_response(response=flexmock.flexmock(status_code=401))

    assert pytest_wrapped_401.value.code == 4

    with pytest.raises(SystemExit) as pytest_wrapped_404:
        github.validate_response(response=flexmock.flexmock(status_code=404))

    assert pytest_wrapped_404.value.code == 5

    with pytest.raises(SystemExit) as pytest_wrapped_404:
        github.validate_response(response=flexmock.flexmock(status_code=1000, ok=False, text='Dummy'))

    assert pytest_wrapped_404.value.code == 10
