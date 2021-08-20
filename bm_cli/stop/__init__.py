import click
import importlib


@click.group(short_help="Stop an active job or cronjob")
def bm_command():
    pass


commands = [
    "job",
]

for command in commands:
    module = importlib.import_module("bm_cli.stop.{}".format(command))
    bm_command.add_command(module.bm_command, command)
