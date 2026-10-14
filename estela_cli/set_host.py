import click
import requests

from estela_cli.templates import BAD_EMOJI, ESTELA_AUTH_NAME, OK_EMOJI
from estela_cli.utils import save_estela_auth


SHORT_HELP = "Set the estela API this CLI talks to"


def reachable(host):
    try:
        response = requests.get("{}/api".format(host), timeout=5)
        return "projects" in response.json()
    except Exception:
        return False


@click.command(name="set-host", short_help=SHORT_HELP)
@click.argument("host", required=True)
def estela_command(host):
    """Save HOST as the estela API to use, e.g. https://api.cloud.bitmaker.dev

    It is remembered, so it does not have to be typed again.
    """
    host = host.rstrip("/")
    if not reachable(host):
        click.echo("{} {} does not answer like an estela API.".format(BAD_EMOJI, host))
        if not click.confirm("Save it anyway?", default=False):
            return

    save_estela_auth(host=host)
    click.echo("{} Host set to {}, stored in ~/{}.".format(OK_EMOJI, host, ESTELA_AUTH_NAME))
