import click

from tabulate import tabulate
from bm_cli.login import login


SHORT_HELP = "List the user's projects"


@click.command(short_help=SHORT_HELP)
def bm_command():
    bm_client = login()
    projects = bm_client.get_projects()
    projects = [[project["name"], project["pid"]] for project in projects]

    headers = ["NAME", "PID"]
    click.echo(tabulate(projects, headers, numalign="left", tablefmt="plain"))
