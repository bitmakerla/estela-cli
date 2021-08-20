import click
import importlib


@click.group(short_help="Delete a resource")
def bm_command():
    pass


commands = [
    "project",
]

for command in commands:
    module = importlib.import_module("bm_cli.delete.{}".format(command))
    bm_command.add_command(module.bm_command, command)
