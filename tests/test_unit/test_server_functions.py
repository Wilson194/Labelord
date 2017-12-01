import labelord.server
import pytest
import os
import flexmock
import flask
import json

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
CONFIGS_PATH = os.path.join(ABS_PATH, 'fixtures', 'configs')


@pytest.mark.parametrize('repo', ('JohnyDep/Pirates', 'BradPit/Mr&MsBlack', 'RobertDawneyJr/Iron-Man'))
def test_server_github_link_filter(repo):
    assert 'https://github.com/{}'.format(repo) in labelord.server.convert_git_repo(repo)


def test_check_signature_create_correct_sha1_hash():
    import hashlib
    import hmac
    message = 'ThisIsTopSecretMessage'
    secret = 'MyReallyPrivatePassword'
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha1).hexdigest()

    assert labelord.server.check_signature(message.encode(), secret, signature)


@pytest.mark.parametrize(['repo', 'result'],
                         [('wilson194/labelord', True),
                          ('wilson194/ella', False),
                          ('wilson194/python-snake', True),
                          ('wilson194/trap', False)])
def test_allowed_repos_return_allowed_repos(labelord_session, monkeypatch, utils, repo, result):
    from labelord.server import check_allowed_repo

    app = flexmock.flexmock(session=labelord_session,
                            labelordConfig=utils.load_config(os.path.join(CONFIGS_PATH, 'target_repos.cfg')))

    monkeypatch.setattr(flask, 'current_app', app)

    assert check_allowed_repo(repo) == result


def test_edit_label_request_edit_target_repository(labelord_session, monkeypatch, utils):
    from labelord.server import edit_label_request
    from labelord.github import get_list_labels
    app = flexmock.flexmock(session=labelord_session,
                            labelordConfig=utils.load_config(os.path.join(CONFIGS_PATH, 'editable_repos.cfg')),
                            updatedRepos=[])

    monkeypatch.setattr(flask, 'current_app', app)

    with open(os.path.join(ABS_PATH, 'fixtures', 'json', 'edit_label.json'), 'r') as f:
        js_text = f.read()
    js = json.loads(js_text)

    edit_label_request(js)

    labels = get_list_labels(labelord_session, 'Wilson194/testin_repo', False)

    assert utils.find_label(labels, 'bug', 'FF0011') == 2


def test_create_label_and_delete_label_based_on_json(labelord_session, monkeypatch, utils):
    from labelord.server import create_label_request, delete_label_request
    from labelord.github import get_list_labels
    app = flexmock.flexmock(session=labelord_session,
                            labelordConfig=utils.load_config(os.path.join(CONFIGS_PATH, 'editable_repos.cfg')),
                            updatedRepos=[])

    monkeypatch.setattr(flask, 'current_app', app)

    with open(os.path.join(ABS_PATH, 'fixtures', 'json', 'create_and_delete_label.json'), 'r') as f:
        js_text = f.read()

    js = json.loads(js_text)

    create_label_request(js)

    labels = get_list_labels(labelord_session, 'Wilson194/testin_repo', False)

    assert utils.find_label(labels, 'porn', 'FF0000')

    delete_label_request(js)

    labels = get_list_labels(labelord_session, 'Wilson194/testin_repo', False)

    assert utils.find_label(labels, 'porn', 'FF0000') == 0
