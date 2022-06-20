import click
import importlib


@click.group(short_help="Stop an active job or cronjob")
def estela_command():
    pass


commands = [
    "job",
]

for command in commands:
    module = importlib.import_module("estela_cli.stop.{}".format(command))
    estela_command.add_command(module.estela_command, command)
