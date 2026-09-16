import importlib

import click

from estela_cli import __version__

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(name="estela", context_settings=CONTEXT_SETTINGS)
@click.version_option(__version__)
def cli():
    pass


commands = [
    "list",
    "create",
    "update",
    "delete",
    "stop",
    "deploy",
    "login",
    "logout",
    "set_host",
    "set_token",
    "create_api_token",
    "init",
    "context",
    "data",
]

for command in commands:
    module = importlib.import_module("estela_cli.{}".format(command))
    cli.add_command(module.estela_command, command.replace("_", "-"))


if __name__ == "__main__":
    cli()
