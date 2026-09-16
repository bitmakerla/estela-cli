import os
import webbrowser
from contextlib import contextmanager

import click

from estela_cli.templates import BAD_EMOJI, CLOCK_EMOJI
from estela_cli.utils import get_estela_auth


SHORT_HELP = "Open the browser to create an API key"


@contextmanager
def quiet_fds():
    """Keeps the browser's own chatter off the terminal.

    The launcher inherits our stdout and writes to it once we have already
    returned, which lands after the shell prompt and reads as a hung command.
    """
    devnull = os.open(os.devnull, os.O_RDWR)
    saved_out, saved_err = os.dup(1), os.dup(2)
    try:
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        yield
    finally:
        os.dup2(saved_out, 1)
        os.dup2(saved_err, 2)
        for fd in (devnull, saved_out, saved_err):
            os.close(fd)


def web_url_for(api_host):
    """estela's web app sits on the API host without its `api.` prefix.

    Deployments that do not follow that shape pass --web-host.
    """
    for scheme in ("https://", "http://"):
        if api_host.startswith(scheme):
            rest = api_host[len(scheme) :]
            return scheme + (rest[4:] if rest.startswith("api.") else rest)
    return api_host


@click.command(name="create-api-token", short_help=SHORT_HELP)
@click.option("--web-host", help="Where the estela web app lives, if it is not the API host without `api.`")
def estela_command(web_host):
    """Open the page that creates a key for this CLI.

    The page arrives filled in and waits for a click. Copy the key it gives you
    and run `estela set-token`.
    """
    estela_auth = get_estela_auth()
    if web_host is None:
        if estela_auth is None or not estela_auth.get("host"):
            raise click.ClickException(
                "{} No host set. Run 'estela set-host <url>' first, or pass --web-host.".format(BAD_EMOJI)
            )
        web_host = web_url_for(estela_auth["host"])

    url = "{}/settings/apiKeys?cli=1".format(web_host.rstrip("/"))
    click.echo("{} Opening {}".format(CLOCK_EMOJI, url))
    with quiet_fds():
        opened = webbrowser.open(url)
    if not opened:
        click.echo("Could not open a browser. Go to that address yourself.")
    click.echo("Create the key there, then run 'estela set-token'.")
