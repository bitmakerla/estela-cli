import click

from getpass import getpass
from estela_cli.estela_client import EstelaClient
from estela_cli.utils import (
    get_host_from_env,
    get_username_from_env,
    get_password_from_env,
    get_estela_auth,
    save_estela_auth,
)
from estela_cli.templates import ESTELA_AUTH_NAME


DEFAULT_ESTELA_API_HOST = "http://localhost"


SHORT_HELP = "Save your credentials"


def env_login():
    host = get_host_from_env()
    username = get_username_from_env()
    password = get_password_from_env()

    try:
        estela_client = EstelaClient(host, username, password)
    except:
        raise Exception("Unable to login with environment credentials.")

    return estela_client


def yaml_login():
    estela_auth = get_estela_auth()

    if estela_auth is None:
        raise Exception(
            "File ~/{} not found. It is recommended to login with 'estela login'.".format(
                ESTELA_AUTH_NAME
            )
        )

    try:
        estela_client = EstelaClient(estela_auth["host"], token=estela_auth["token"])
    except:
        raise Exception(
            "Invalid context stored in ~/{}. Please login again.".format(
                ESTELA_AUTH_NAME
            )
        )

    return estela_client


def prompt_login(username=None, password=None, host=None):
    try:
        if host is None:
            stored = (get_estela_auth() or {}).get("host")
            host = click.prompt("Host", default=stored or DEFAULT_ESTELA_API_HOST)
        if username is None:
            username = click.prompt("Username")
        if password is None:
            password = getpass()

        estela_client = EstelaClient(host, username, password)
    except:
        raise Exception("Unable to login with provided credentials.")

    return estela_client


def login(username=None, password=None, host=None):
    try:
        estela_client = env_login()
        click.echo(
            "You are currently using environment variables to configure estela CLI."
        )
        return estela_client
    except:
        pass

    try:
        estela_client = yaml_login()
        return estela_client
    except Exception as ex:
        click.echo(str(ex))

    try:
        estela_client = prompt_login(username, password, host)
    except Exception as ex:
        raise click.ClickException(str(ex))

    return estela_client


@click.command(name="login", short_help=SHORT_HELP)
@click.option(
    "--username",
    help="Username for login. If username is not given, it will be asked",
)
@click.option(
    "--password",
    help="Password for login. If password is not given, it will be asked",
)
@click.option(
    "--host",
    help="API endpoint to send the requests. If host is not given, it will be asked",
)
def estela_command(username, password, host):
    # A stored host is configuration, not a session: only a stored token means
    # someone is already logged in.
    estela_auth = get_estela_auth() or {}
    if estela_auth.get("token"):
        raise click.ClickException(
            "You already logged in. To change credentials run 'estela logout' first."
        )

    if host is None:
        host = estela_auth.get("host")

    try:
        estela_client = prompt_login(username, password, host)
    except Exception as ex:
        raise click.ClickException(str(ex))

    save_estela_auth(host=estela_client.host, token=estela_client.token)
    click.echo("Successful login. API Token stored in ~/{}.".format(ESTELA_AUTH_NAME))
