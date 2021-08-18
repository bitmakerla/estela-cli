import click
import requests

from bm_cli.login import env_login, yaml_login
from bm_cli.utils import (
    get_bm_auth,
    get_bm_settings,
    get_host_from_env,
    get_username_from_env,
    get_password_from_env,
)
from bm_cli.templates import BITMAKER_AUTH_NAME, OK_EMOJI, BAD_EMOJI


SHORT_HELP = "Show your current context"


OK_HOST = OK_EMOJI + " Host: {}."
BAD_HOST = "{} Cannot connect to the Host.".format(BAD_EMOJI)

OK_AUTH = "{} Valid Auth.".format(OK_EMOJI)
BAD_AUTH = "{} Invalid Auth.".format(BAD_EMOJI)

NO_PROJECT = "No active project in the current directory."
ACTIVE_PROJECT = "Active project: {}."


def test_host(host):
    response = requests.get("{}/api".format(host), timeout=1)
    assert "projects" in response.json()


@click.command(short_help=SHORT_HELP)
def bm_command():
    host = get_host_from_env()
    username = get_username_from_env()
    password = get_password_from_env()

    if host is None or username is None or password is None:
        bm_auth = get_bm_auth()

        if bm_auth is None:
            click.echo(
                "Environment variables not declared, ~/{} not found.".format(
                    BITMAKER_AUTH_NAME
                )
            )
            return

        click.echo(
            "You are currently using ~/{} file to configure bitmaker CLI.".format(
                BITMAKER_AUTH_NAME
            )
        )

        try:
            test_host(bm_auth["host"])
            click.echo(OK_HOST.format(bm_auth["host"]))
        except:
            click.echo(BAD_HOST)
            return
        try:
            bm_client = yaml_login()
            click.echo(OK_AUTH)
        except:
            click.echo(BAD_AUTH)
            return
    else:
        click.echo(
            "You are currently using environment variables to configure bitmaker CLI."
        )
        try:
            test_host(host)
            click.echo(OK_HOST.format(host))
        except:
            click.echo(BAD_HOST)
            return
        try:
            bm_client = env_login()
            click.echo(OK_AUTH)
        except:
            click.echo(BAD_AUTH)
            return

    try:
        settings = get_bm_settings()
        click.echo(ACTIVE_PROJECT.format(settings["project"]["pid"]))
    except:
        click.echo(NO_PROJECT)
