import sys
from getpass import getpass

import click
import requests

from estela_cli.templates import BAD_EMOJI, ESTELA_AUTH_NAME, OK_EMOJI
from estela_cli.utils import get_estela_auth, save_estela_auth
from estela_cli import __version__


SHORT_HELP = "Save an API key created in the web app"


SCOPE_MEANING = {
    "data": "read job data",
    "run": "run jobs and cronjobs",
    "manage": "deploy and manage projects",
}


def describe(scopes):
    """Says what a key can do, in the words the commands use."""
    if not scopes:
        return "read-only"
    return ", ".join(SCOPE_MEANING.get(s, s) for s in scopes)


def whoami(host, token):
    """Returns (username, scopes) for the key, raising if it is not accepted.

    scopes is None when a session was used, since only keys carry them.
    """
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
        body = response.json()
        return body.get("username"), body.get("scopes")
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
def estela_command():
    """Save an API key so this CLI can use it.

    Asks for the key without echoing it. In a script, pipe it in instead:

        echo "$ESTELA_API_KEY" | estela set-token

    The key is never taken as an argument, because arguments are kept in shell
    history and are visible in the process list while the command runs.

    Run 'estela create-api-token' first if you do not have a key.
    """
    estela_auth = get_estela_auth()
    if estela_auth is None or not estela_auth.get("host"):
        raise click.ClickException(
            "{} No host set. Run 'estela set-host <url>' first.".format(BAD_EMOJI)
        )

    if sys.stdin.isatty():
        token = getpass("Paste your API key: ").strip()
    else:
        token = sys.stdin.readline().strip()
    if not token:
        raise click.ClickException("{} No key given.".format(BAD_EMOJI))

    username, scopes = whoami(estela_auth["host"], token)
    save_estela_auth(token=token)
    click.echo("{} Logged in as {}. Key stored in ~/{}.".format(OK_EMOJI, username, ESTELA_AUTH_NAME))
    if scopes is not None:
        click.echo("This key can: {}.".format(describe(scopes)))
        missing = [s for s in ("run", "manage") if s not in scopes]
        if missing:
            click.echo(
                "It cannot {}. Create a key with those permissions if you need them.".format(
                    " or ".join(SCOPE_MEANING[s] for s in missing)
                )
            )
