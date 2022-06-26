import click
import os

from estela_cli.utils import get_home_path
from estela_cli.login import ESTELA_AUTH_NAME


SHORT_HELP = "Remove your credentials"


@click.command(short_help=SHORT_HELP)
def estela_command():
    home_path = get_home_path()
    estela_auth_path = os.path.join(home_path, ESTELA_AUTH_NAME)

    if not os.path.exists(estela_auth_path):
        raise click.ClickException("You have not logged in. Run 'estela login' first.")

    os.remove(estela_auth_path)
    click.echo("Successful logout.")
