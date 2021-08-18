import click

from tabulate import tabulate
from bm_cli.login import login
from bm_cli.utils import get_bm_settings


SHORT_HELP = "List the project's spiders"


@click.command(short_help=SHORT_HELP)
@click.argument("pid", required=False)
def bm_command(pid):
    """List spiders of a given project

    PID is the project's pid (active project by default)
    """

    bm_client = login()

    if pid is None:
        try:
            bm_settings = get_bm_settings()
            pid = bm_settings["project"]["pid"]
        except:
            raise click.ClickException(
                "No active project in the current directory. Please specify the PID."
            )

    try:
        bm_client.get_project(pid)
    except Exception as ex:
        raise click.ClickException(
            "The project does not exist, or you do not have permission to perform this action."
        )

    spiders = bm_client.get_spiders(pid)
    spiders = [[spider["name"], str(spider["sid"])] for spider in spiders]

    headers = ["NAME", "SID"]
    click.echo(tabulate(spiders, headers, numalign="left", tablefmt="plain"))
