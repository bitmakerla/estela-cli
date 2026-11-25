import sys
from getpass import getpass

import click
import requests

from estela_cli.templates import BAD_EMOJI, ESTELA_AUTH_NAME, OK_EMOJI
from estela_cli.utils import get_host, save_estela_auth, fail
from estela_cli import __version__


SHORT_HELP = "Save an API key created in the web app"


SCOPE_MEANING = {
    "data": "read job data",
    "run": "run jobs and cronjobs",
    "manage": "deploy and manage projects",
    "operator": "reach every customer's projects",
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
        raise fail("{} Could not reach {}.".format(BAD_EMOJI, host))

    if response.status_code == 200:
        body = response.json()
        return body.get("username"), body.get("scopes")
    if response.status_code in (401, 403):
        detail = ""
        try:
            detail = " " + response.json().get("detail", "")
        except Exception:
            pass
        raise fail("{} The API rejected that key.{}".format(BAD_EMOJI, detail))
    raise fail(
        "{} {} answered {}.".format(BAD_EMOJI, host, response.status_code)
    )


@click.command(name="set-token", short_help=SHORT_HELP)
def estela_command():
    """Save an API key so this CLI can use it.

    Asks for the key without echoing it. In a script, pipe it in instead:

        echo "$ESTELA_API_KEY" | estela set-token

    The key is never taken as an argument, because arguments are kept in shell
    history and are visible in the process list while the command runs.

    To create a key from the browser instead, run 'estela login'.
    """
    if sys.stdin.isatty():
        token = getpass("Paste your API key: ").strip()
    else:
        token = sys.stdin.readline().strip()
    if not token:
        raise fail("{} No key given.".format(BAD_EMOJI))

    username, scopes = whoami(get_host(), token)
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
