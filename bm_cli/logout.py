import click
import os

from bm_cli.utils import get_home_path
from bm_cli.login import BITMAKER_AUTH_NAME


SHORT_HELP = "Remove your credentials"


@click.command(short_help=SHORT_HELP)
def bm_command():
    home_path = get_home_path()
    bm_auth_path = os.path.join(home_path, BITMAKER_AUTH_NAME)

    if not os.path.exists(bm_auth_path):
        raise click.ClickException(
            "You have not logged in. Run 'bitmaker login' first."
        )

    os.remove(bm_auth_path)
    click.echo("Successful logout.")
