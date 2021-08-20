import click
import importlib


__version__ = "0.1"

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
def cli():
    pass


commands = [
    "list",
    "create",
    "delete",
    "stop",
    "deploy",
    "login",
    "logout",
    "init",
    "context",
]

for command in commands:
    module = importlib.import_module("bm_cli.{}".format(command))
    cli.add_command(module.bm_command, command)
