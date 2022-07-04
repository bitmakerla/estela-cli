import click
import importlib


@click.group(short_help="Update a resource")
def estela_command():
    pass


commands = [
    "cronjob",
    "job",
]

for command in commands:
    module = importlib.import_module("estela_cli.update.{}".format(command))
    estela_command.add_command(module.estela_command, command)
