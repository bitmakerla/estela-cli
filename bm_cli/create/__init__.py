import click
import importlib


@click.group(short_help="Create a resource")
def bm_command():
    pass


commands = [
    "project",
    "job",
]

for command in commands:
    module = importlib.import_module("bm_cli.create.{}".format(command))
    bm_command.add_command(module.bm_command, command)
