import os

import click
import yaml

from estela_cli.templates import ESTELA_AUTH_NAME, OK_EMOJI
from estela_cli.utils import get_estela_auth, get_estela_auth_path


SHORT_HELP = "Remove your credentials"


@click.command(name="logout", short_help=SHORT_HELP)
def estela_command():
    """Forget the stored key.

    The host is configuration, not a credential, so it stays — logging back in
    does not mean typing it again. Change it with 'estela set-host'.

    This only forgets the key locally. To stop it working everywhere, revoke it
    in the web app.
    """
    estela_auth = get_estela_auth()
    if estela_auth is None:
        raise click.ClickException("You have not logged in. Run 'estela set-token' first.")

    path = get_estela_auth_path()
    estela_auth.pop("token", None)

    if not estela_auth:
        os.remove(path)
    else:
        with open(path, "w") as estela_auth_yaml:
            yaml.safe_dump(estela_auth, estela_auth_yaml, default_flow_style=False)
        os.chmod(path, 0o600)

    click.echo("{} Logged out.".format(OK_EMOJI))
    if estela_auth.get("host"):
        click.echo("Host {} kept in ~/{}.".format(estela_auth["host"], ESTELA_AUTH_NAME))
