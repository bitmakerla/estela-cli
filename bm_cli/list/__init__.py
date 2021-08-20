import click
import importlib


@click.group(short_help="Display the available resources")
def bm_command():
    pass


commands = [
    "project",
    "spider",
    "job",
]

for command in commands:
    module = importlib.import_module("bm_cli.list.{}".format(command))
    bm_command.add_command(module.bm_command, command)
