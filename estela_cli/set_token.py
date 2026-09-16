from getpass import getpass

import click
import requests

from estela_cli.templates import BAD_EMOJI, ESTELA_AUTH_NAME, OK_EMOJI
from estela_cli.utils import get_estela_auth, save_estela_auth
from estela_cli import __version__


SHORT_HELP = "Save an API key created in the web app"


def whoami(host, token):
    """Returns the username the key belongs to, or None if it is not accepted."""
    try:
        response = requests.get(
            "{}/api/auth/whoami".format(host),
            headers={
                "Authorization": "Token {}".format(token),
                "User-Agent": "estela-cli/{}".format(__version__),
            },
            timeout=10,
        )
    except Exception:
        raise click.ClickException("{} Could not reach {}.".format(BAD_EMOJI, host))

    if response.status_code == 200:
        return response.json().get("username")
    if response.status_code in (401, 403):
        detail = ""
        try:
            detail = " " + response.json().get("detail", "")
        except Exception:
            pass
        raise click.ClickException("{} The API rejected that key.{}".format(BAD_EMOJI, detail))
    raise click.ClickException(
        "{} {} answered {}.".format(BAD_EMOJI, host, response.status_code)
    )


@click.command(name="set-token", short_help=SHORT_HELP)
@click.argument("token", required=False)
def estela_command(token):
    """Save an API key so this CLI can use it.

    Pass it as TOKEN, or leave it out and it will be asked for without echoing.
    Run 'estela create-api-token' first if you do not have one.
    """
    estela_auth = get_estela_auth()
    if estela_auth is None or not estela_auth.get("host"):
        raise click.ClickException(
            "{} No host set. Run 'estela set-host <url>' first.".format(BAD_EMOJI)
        )

    if not token:
        token = getpass("Paste your API key: ").strip()
    if not token:
        raise click.ClickException("{} No key given.".format(BAD_EMOJI))

    username = whoami(estela_auth["host"], token)
    save_estela_auth(token=token)
    click.echo("{} Logged in as {}. Key stored in ~/{}.".format(OK_EMOJI, username, ESTELA_AUTH_NAME))
