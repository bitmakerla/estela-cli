import click
import importlib


@click.group(short_help="Returns all the data of a job and saves it in a json file")
def estela_command():
    pass


commands = [
    "job",
]

for command in commands:
    module = importlib.import_module("estela_cli.data.{}".format(command))
    estela_command.add_command(module.estela_command, command)
