import yaml
import click
import requests

from getpass import getpass
from estela_cli.login import env_login, yaml_login
from estela_cli.estela_client import EstelaClient
from estela_cli.utils import (
    get_estela_auth,
    update_estela_auth,
    get_estela_settings,
    get_estela_config,
    get_host_from_env,
    get_username_from_env,
    get_password_from_env,
    get_estela_config_path,
)
from estela_cli.templates import ESTELA_AUTH_NAME, ESTELA_CONFIG_NAME, OK_EMOJI, BAD_EMOJI


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


def prompt_context(name, username=None, password=None, host=None):
    try:
        if host is None:
            host = click.prompt("Host")
        if username is None:
            username = click.prompt("Username")
        if password is None:
            password = getpass()

        estela_config_path = get_estela_config_path()
        estela_config = get_estela_config()

        if estela_config is None:
            estela_config = {}

        estela_config[name] = {
            "host": host,
            "username": username,
            "password": password,
        }
        with open(estela_config_path, "w") as estela_config_yaml:
            yaml.dump(estela_config, estela_config_yaml)
            click.echo(
                "Successful login. Context {} stored in ~/{}.".format(
                    name, ESTELA_CONFIG_NAME
                )
            )
        estela_client = EstelaClient(host, username, password)

    except:
        raise Exception("Unable to login with provided credentials.")

    return estela_client


@click.command(name="context", short_help=SHORT_HELP)
@click.argument("name", required=False)
def estela_command(name):
    host = get_host_from_env()
    username = get_username_from_env()
    password = get_password_from_env()

    if name:
        click.echo(f"Checking your current context for {name}...")
        estela_config = get_estela_config()

        if estela_config and estela_config.get(name, None):
            click.echo("Context {} found.".format(name))
            try:
                test_host(estela_config[name]["host"])
                click.echo(OK_HOST.format(estela_config[name]["host"]))
                estela_client = EstelaClient(
                    estela_config[name]["host"],
                    estela_config[name]["username"],
                    estela_config[name]["password"],
                )
            except:
                click.echo(BAD_HOST)
                return
        else:
            click.echo(
                "Context {} not found.\nInitializing context...".format(name)
            )
            estela_client = prompt_context(name, username, password, host)
        update_estela_auth(estela_client.host, estela_client.token)
        return

    if host is None or username is None or password is None:
        estela_auth = get_estela_auth()

        if estela_auth is None:
            click.echo(
                "Environment variables not declared, ~/{} not found.".format(
                    ESTELA_AUTH_NAME
                )
            )
            return

        click.echo(
            "You are currently using ~/{} file to configure estela CLI.".format(
                ESTELA_AUTH_NAME
            )
        )

        try:
            test_host(estela_auth["host"])
            click.echo(OK_HOST.format(estela_auth["host"]))
        except:
            click.echo(BAD_HOST)
            return
        try:
            estela_client = yaml_login()
            click.echo(OK_AUTH)
        except:
            click.echo(BAD_AUTH)
            return
    else:
        click.echo(
            "You are currently using environment variables to configure estela CLI."
        )
        try:
            test_host(host)
            click.echo(OK_HOST.format(host))
        except:
            click.echo(BAD_HOST)
            return
        try:
            estela_client = env_login()
            click.echo(OK_AUTH)
        except:
            click.echo(BAD_AUTH)
            return

    try:
        settings = get_estela_settings()
        click.echo(ACTIVE_PROJECT.format(settings["project"]["pid"]))
    except:
        click.echo(NO_PROJECT)
