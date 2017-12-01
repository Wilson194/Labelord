import pytest
import os

ABS_PATH = os.path.abspath(os.path.dirname(__file__))
CONFIGS_PATH = os.path.join(ABS_PATH, 'fixtures', 'configs')


def test_list_of_repos_return_all_repos(labelord_session):
    from labelord.github import get_list_repos

    repos = get_list_repos(labelord_session)

    assert 'Wilson194/ella' in repos

    assert 'Wilson194/pyloppy' in repos

    assert len(repos) == 16


@pytest.mark.parametrize(['name', 'color', 'result'],
                         [('bug', 'ee0701', 2),
                          ('duplicate', 'cccccc', 2),
                          ('trap', '111111', 0)])
def test_list_of_labels_from_one_repository(labelord_session, utils, name, color, result):
    from labelord.github import get_list_labels

    labels = get_list_labels(labelord_session, 'wilson194/labelord')

    assert utils.find_label(labels, name=name, color=color) == result


def test_list_of_labels_quit_with_bad_repo_name(labelord_session):
    from labelord.github import get_list_labels
    with pytest.raises(SystemExit) as pytest_wrapped_404:
        get_list_labels(labelord_session, 'NotAName/NotARepo')

    assert pytest_wrapped_404.value.code == 5


@pytest.mark.parametrize(['name', 'color', 'result'],
                         [('bug', 'ee0701', 2),
                          ('duplicate', 'cccccc', 2),
                          ('trap', '111111', 0)])
def test_get_source_labels_with_parameters(label_updater_client, utils, name, color, result):
    labels = label_updater_client.get_source_labels('Wilson194/labelord')

    assert utils.find_label(labels, name=name, color=color) == result


@pytest.mark.parametrize(['name', 'color', 'result'],
                         [('bug', 'ee0701', 2),
                          ('duplicate', 'cccccc', 2),
                          ('trap', '111111', 0)])
def test_get_source_labels_with_repo_in_config(label_updater_client, utils, name, color, result):
    cfg = utils.load_config(os.path.join(CONFIGS_PATH, 'source_repo.cfg'))

    label_updater_client.config = cfg
    labels = label_updater_client.get_source_labels(None)

    assert utils.find_label(labels, name=name, color=color) == result


@pytest.mark.parametrize(['name', 'color', 'result'],
                         [('bug', 'ee0701', False),
                          ('duplicate', 'cccccc', False),
                          ('trap', '111111', True)])
def test_get_source_labels_from_config_file(label_updater_client, utils, name, color, result):
    cfg = utils.load_config(os.path.join(CONFIGS_PATH, 'labels_repo.cfg'))

    label_updater_client.config = cfg
    labels = label_updater_client.get_source_labels(None)

    assert utils.find_label(labels, name=name, color=color) == result


def test_get_target_repositories_with_all_flag(label_updater_client):
    label_updater_client.allRepos = True

    repos = label_updater_client.get_target_repositories()

    assert 'Wilson194/ella' in repos
    assert len(repos) == 16


@pytest.mark.parametrize(['repository', 'result'],
                         [('wilson194/labelord', 1),
                          ('wilson194/ella', 0),
                          ('wilson194/python-snake', 1),
                          ('wilson194/wator', 0)])
def test_get_target_repositories_with_repos_in_config(label_updater_client, utils, repository, result):
    cfg = utils.load_config(os.path.join(CONFIGS_PATH, 'target_repos.cfg'))

    label_updater_client.config = cfg
    repos = label_updater_client.get_target_repositories()

    assert (repository in repos) == result


@pytest.mark.parametrize('error_num', (0, 1, 5))
def test_output_of_print_summary(capsys, error_num):
    from labelord.github import LabelUpdater
    label_updater_client = LabelUpdater(None, None, {})
    label_updater_client.errorNum = error_num

    if error_num > 0:
        with pytest.raises(SystemExit) as wrap:
            label_updater_client.print_summary()
    else:
        label_updater_client.print_summary()

    out, err = capsys.readouterr()

    assert str(error_num) in out
    assert 'SUMMARY' in out


@pytest.mark.parametrize(['error_num', 'verbose', 'quiet', 'text'],
                         [(0, True, True, 'updated successfully'),
                          (5, True, True, 'please error check log'),
                          (0, False, False, 'updated successfully'),
                          (4, False, False, 'please check log above'),
                          (4, False, True, ''),
                          ])
def test_all_types_of_print_summary_based_on_parameters(capsys, error_num, verbose, quiet, text):
    from labelord.github import LabelUpdater
    label_updater_client = LabelUpdater(None, None, {})
    label_updater_client.errorNum = error_num

    label_updater_client.quiet = quiet
    label_updater_client.verbose = verbose

    if error_num > 0:
        with pytest.raises(SystemExit) as wrap:
            label_updater_client.print_summary()
    else:
        label_updater_client.print_summary()

    out, err = capsys.readouterr()

    if text:
        assert str(error_num) in out
    assert text in out


def test_add_label_and_remove_label(label_updater_client, utils):
    from labelord.github import Label
    from labelord.github import get_list_labels

    repo = 'Wilson194/hello_world'
    label = Label('newAwesomeLabel', 'FFFFFF')

    label_updater_client.add_label(repo, label)

    session = label_updater_client.session

    labels = get_list_labels(session, repo)

    assert utils.find_label(labels, 'newAwesomeLabel', 'ffffff')

    label_updater_client.remove_label(repo, label)

    labels = get_list_labels(session, repo)

    assert utils.find_label(labels, 'newAwesomeLabel', 'FFFFFF') == 0


def test_update_label(label_updater_client, utils):
    from labelord.github import Label
    from labelord.github import get_list_labels

    repo = 'Wilson194/hello_world'
    label = Label('newAwesomeLabel', 'FFFFFF')

    label_updater_client.add_label(repo, label)

    session = label_updater_client.session

    newLabel = Label('newAwesomeLabel2', '000000')

    label_updater_client.update_label(repo, newLabel, label)

    labels = get_list_labels(session, repo)

    assert utils.find_label(labels, 'newAwesomeLabel2', '000000')
    assert utils.find_label(labels, 'newAwesomeLabel', 'FFFFFF') == 0

    label_updater_client.remove_label(repo, newLabel)


def test_update_more_then_one_label_at_more_then_one_repo(label_updater_client, utils):
    from labelord.github import Label
    from labelord.github import get_list_labels

    session = label_updater_client.session

    # Same label
    l1 = Label('bug', 'fc2929')

    # different color
    l2 = Label('duplicate', 'cdcdcd')

    # new label
    l3 = Label('ItsATrap', 'FF0000')
    l4 = Label('DefinitelyNotAPorn', 'FF0000')

    label_updater_client.update_labels([l1, l2, l3, l4], ['Wilson194/python-Smurf_Pexeso', 'Wilson194/hello_world'])

    labels = get_list_labels(session, 'Wilson194/python-Smurf_Pexeso')

    assert utils.find_label(labels, 'bug', 'fc2929') == 2
    assert utils.find_label(labels, 'ItsATrap', 'FF0000') == 2
    assert utils.find_label(labels, 'DefinitelyNotAPorn', 'FF0000') == 2

    labels = get_list_labels(session, 'Wilson194/hello_world')

    assert utils.find_label(labels, 'bug', 'fc2929') == 2
    assert utils.find_label(labels, 'duplicate', 'cccccc') == 1


def test_print_log_print_all_necesarry_informations(label_updater_client, capsys):
    from labelord.github import Label
    label = Label('Bug', 'ffffff')

    label_updater_client.verbose = True
    label_updater_client.quiet = False

    label_updater_client.print_log('Wilson194/labelord', 'ADD', label, 'Label not found')
    out, err = capsys.readouterr()

    assert 'ADD' in out
    assert 'ERR' in out
    assert 'Wilson194/labelord' in out
    assert label.color in out
    assert label.name in out
    assert 'Label not found' in out
