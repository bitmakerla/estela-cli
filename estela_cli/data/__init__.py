import click
import importlib


@click.group(short_help="Retrieve data from a given job and save it locally")
def estela_command():
    pass


commands = [
    "job",
]

for command in commands:
    module = importlib.import_module("estela_cli.data.{}".format(command))
    estela_command.add_command(module.estela_command, command)
