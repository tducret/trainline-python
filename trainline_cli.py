# -*- coding: utf-8 -*-

"""CLI tool for trainline."""
import sys
import click
from trainline import __version__

# Usage : trainline_cli.py --help


@click.command()
@click.option(
    '--param1', '-p',
    envvar="PARAM1",
    type=str,
    help='example string param (or set the env var PARAM1)',
)
@click.option(
    '--defaultparam2', '-d',
    type=str,
    help='example param with default value',
    default='fr'
)
@click.version_option(
    version=__version__,
    message='%(prog)s, based on [trainline] package version %(version)s'
)
def main(param1, defaultparam2):
    """ Example main """


if __name__ == "__main__":
    main()
