import click

from tabulate import tabulate
from estela_cli.login import login


SHORT_HELP = "List the current user's projects"


@click.command(short_help=SHORT_HELP)
def estela_command():
    estela_client = login()
    projects = estela_client.get_projects()
    projects = [[project["name"], project["pid"]] for project in projects]

    headers = ["NAME", "PID"]
    click.echo(tabulate(projects, headers, numalign="left", tablefmt="plain"))
