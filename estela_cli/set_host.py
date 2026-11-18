import click
import requests

from estela_cli.templates import BAD_EMOJI, ESTELA_AUTH_NAME, OK_EMOJI
from estela_cli.utils import get_estela_auth, get_host, save_estela_auth


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
    """Save HOST as the estela API to use, e.g. https://hetzner-staging.bitmaker.dev

    Without one, estela-cli uses https://cloud.bitmaker.dev. A key works on one
    estela only, so changing the host logs you out.
    """
    host = host.rstrip("/")
    if not reachable(host):
        click.echo("{} {} does not answer like an estela API.".format(BAD_EMOJI, host))
        if not click.confirm("Save it anyway?", default=False):
            return

    # Keeping the key would send it to the new host with every command.
    token = (get_estela_auth() or {}).get("token")
    current = get_host()
    if token and host != current:
        # The fragment the web lists the key by; an old password-login token has none to show.
        shown = " with the key {}…".format(token[:19]) if token.startswith("estela_") else ""
        click.echo(
            "You are logged in to {}{}.\n"
            "A key works on one server only, so changing the host logs you out. The key\n"
            "keeps working until it expires or you revoke it in the web. To keep it, copy\n"
            "it from ~/{} now.".format(current, shown, ESTELA_AUTH_NAME)
        )
        if not click.confirm("Change the host and log out?", default=False):
            return
        save_estela_auth(host=host, token="")
        click.echo("{} Host set to {}. Run 'estela login' to log in there.".format(OK_EMOJI, host))
        return

    save_estela_auth(host=host)
    click.echo("{} Host set to {}, stored in ~/{}.".format(OK_EMOJI, host, ESTELA_AUTH_NAME))
