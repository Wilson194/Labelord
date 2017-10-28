#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import requests
import os
import github
import server
from server import server as serverBlueprint


@click.group('labelord')
@click.option('-c', '--config', envvar='LABELORD_CONFIG', default='config.cfg', type=click.Path(),
              help='Specify path to config file.')
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
    config = github.load_config(ctx.obj['config'])

    token = github.load_token(config, ctx.obj['token'])

    # Set auth
    auth = github.MyAuth(token)
    session.auth = auth

    repositories = github.get_list_repos(session)

    for repo in repositories:
        print(repo)


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
    config = github.load_config(ctx.obj['config'])

    token = github.load_token(config, ctx.obj['token'])

    # Set auth
    auth = github.MyAuth(token)
    session.auth = auth

    labels = github.get_list_labels(session, repository)

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
    config = github.load_config(ctx.obj['config'])
    token = github.load_token(config, ctx.obj['token'])

    # Set auth
    auth = github.MyAuth(token)
    session.auth = auth

    lu = github.LabelUpdater(session, config, runConfig)

    sourceLabels = lu.get_source_labels(sourceRepository)

    targetRepositories = lu.get_target_repositories()

    lu.update_labels(sourceLabels, targetRepositories)


@cli.command()
@click.option('-h', '--host', 'hostname', help='Host name for start server', default='127.0.0.1')
@click.option('-p', '--port', 'port', help='Port for start server', default=5000, type=int)
@click.option('-d', '--debug', 'debug', help='Enable flask server debug mode', is_flag=True)
@click.pass_context
def run_server(ctx, hostname, port, debug):
    """
    Run server command
    :param ctx: context from click
    :param hostname: hostname for flask run
    :param port: port for flask run
    :param debug: enable debug mode
    :return: None
    """

    session = ctx.obj['session']

    # Load config
    config = github.load_config(ctx.obj['config'])

    token = github.load_token(config, ctx.obj['token'])

    # Set auth
    auth = github.MyAuth(token)
    session.auth = auth

    app.inject_session(session)
    app.set_labelord_config(config)

    app.run(hostname, port, debug)


def create_app():
    """
    Factory creator for flask App
    :return: app class
    """
    app = server.LabelordWeb(__name__)

    configPath = os.getenv('LABELORD_CONFIG', 'config.cfg')

    labelordConfig = github.load_config(configPath)

    app.labelordConfig = labelordConfig

    return app


app = create_app()
app.register_blueprint(serverBlueprint)
app.jinja_env.filters['gitLink'] = server.convert_time

if __name__ == '__main__':
    cli(obj={})
