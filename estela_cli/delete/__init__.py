import click
import importlib


@click.group(short_help="Delete a resource")
def estela_command():
    pass


commands = [
    "project",
]

for command in commands:
    module = importlib.import_module("estela_cli.delete.{}".format(command))
    estela_command.add_command(module.estela_command, command)
