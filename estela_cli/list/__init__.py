import click
import importlib


@click.group(short_help="Display the available resources")
def estela_command():
    pass


commands = [
    "project",
    "spider",
    "job",
    "cronjob",
]

for command in commands:
    module = importlib.import_module("estela_cli.list.{}".format(command))
    estela_command.add_command(module.estela_command, command)
