from click.testing import CliRunner
from labelord import labelord


def test_push_force():
    runner = CliRunner()
    result = runner.invoke(labelord.list_repos, ['push', '--force'])
    # assert result.exit_code == 0
    # assert 'forced update' in result.output
