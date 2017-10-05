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


def load_config(cfg):
    config = configparser.ConfigParser()
    config.read(cfg)

    return config


@click.group('labelord')
@click.option('-c', '--config', default='config.cfg', type=click.Path(), help='Specify path to config file.')
@click.option('-t', '--token', envvar='GITHUB_TOKEN', type=str, help='Token for GitHub API.')
@click.pass_context
def cli(ctx, config, token):
    # Create session
    session = ctx.obj.get('session', requests.Session())
    session.headers = {'User-Agent': 'Python'}

    # Load config
    cfg = load_config(config)

    # Load token
    if not token:
        token = cfg.get('github', 'token', fallback=False)

    # Token not set
    if not token:
        sys.stderr.write('No GitHub token has been provided\n')
        quit(3)

    # Set auth
    auth = MyAuth(token)
    session.auth = auth

    # Validate token
    r = session.get('https://api.github.com/user')
    if not r.ok:
        sys.stderr.write(r.text)
        quit(4)

    ctx.obj['session'] = session


@cli.command()
@click.pass_context
def list_repos(ctx):
    # TODO: Add required options/arguments
    # TODO: Implement the 'list_repos' command
    session = ctx.obj['session']
    r = session.get('https://api.github.com/user/repos?per_page=100&page=1')

    if not r.ok:
        sys.stderr.write(r.text)
        quit(10)

    repositories = r.json()

    for repo in repositories:
        print('{}/{}'.format(repo['owner']['login'], repo['name']))


@cli.command()
@click.pass_context
@click.argument('repository', nargs=1)
def list_labels(ctx, repository):
    session = ctx.obj['session']

    userName, repoName = repository.split('/')

    r = session.get('https://api.github.com/repos/{}/{}/labels?per_page=100&page=1'.format(userName, repoName))

    if not r.ok:
        sys.stderr.write(r.text)
        quit(5)

    labels = r.json()

    for label in labels:
        print('#{} {}'.format(label['color'], label['name']))


@cli.command()
@click.pass_context
def run(ctx):
    # TODO: Add required options/arguments
    # TODO: Implement the 'run' command
    pass


if __name__ == '__main__':
    cli(obj={})
