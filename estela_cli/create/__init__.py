import click
import importlib


@click.group(short_help="Create a resource")
def estela_command():
    pass


commands = [
    "project",
    "job",
    "cronjob",
]

for command in commands:
    module = importlib.import_module("estela_cli.create.{}".format(command))
    estela_command.add_command(module.estela_command, command)
