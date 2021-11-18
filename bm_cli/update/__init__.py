import click
import importlib


@click.group(short_help="Update a resource")
def bm_command():
    pass


commands = [
    "cronjob",
]

for command in commands:
    module = importlib.import_module("bm_cli.update.{}".format(command))
    bm_command.add_command(module.bm_command, command)
