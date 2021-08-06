import os
import yaml
import click

from getpass import getpass
from string import Template
from bm_cli.bm_client import BmClient
from bm_cli.utils import (
    get_host_from_env,
    get_username_from_env,
    get_password_from_env,
    get_bm_auth,
    get_home_path,
)
from bm_cli.templates import BITMAKER_AUTH_NAME, BITMAKER_AUTH


DEFAULT_BM_API_HOST = "http://104.248.108.208:8000"


SHORT_HELP = "Save your credentials"


def env_login():
    host = get_host_from_env()
    username = get_username_from_env()
    password = get_password_from_env()

    try:
        bm_client = BmClient(host, username, password)
    except:
        raise Exception("Unable to login with environment credentials.")

    return bm_client


def yaml_login():
    bm_auth = get_bm_auth()

    if bm_auth is None:
        raise Exception(
            "File ~/{} not found. It is recommended to login with 'bitmaker login'.".format(
                BITMAKER_AUTH_NAME
            )
        )

    try:
        bm_client = BmClient(bm_auth["host"], token=bm_auth["token"])
    except:
        raise Exception(
            "Invalid context stored in ~/{}. Please login again.".format(
                BITMAKER_AUTH_NAME
            )
        )

    return bm_client


def prompt_login(username=None, password=None, host=None):
    try:
        if host is None:
            host = click.prompt("Host", default=DEFAULT_BM_API_HOST)
        if username is None:
            username = click.prompt("Username")
        if password is None:
            password = getpass()

        bm_client = BmClient(host, username, password)
    except:
        raise Exception("Unable to login with provided credentials.")

    return bm_client


def login(username=None, password=None, host=None):
    try:
        bm_client = env_login()
        click.echo(
            "You are currently using environment variables to configure bitmaker CLI."
        )
        return bm_client
    except:
        pass

    try:
        bm_client = yaml_login()
        return bm_client
    except Exception as ex:
        click.echo(str(ex))

    try:
        bm_client = prompt_login(username, password, host)
    except Exception as ex:
        raise click.ClickException(str(ex))

    return bm_client


@click.command(short_help=SHORT_HELP)
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
def bm_command(username, password, host):
    home_path = get_home_path()
    bm_auth_path = os.path.join(home_path, BITMAKER_AUTH_NAME)

    if os.path.exists(bm_auth_path):
        raise click.ClickException(
            "You already logged in. To change credentials run 'bitmaker logout' first."
        )

    try:
        bm_client = prompt_login(username, password, host)
    except Exception as ex:
        raise click.ClickException(str(ex))

    template = Template(BITMAKER_AUTH)
    values = {
        "bm_host": bm_client.host,
        "bm_token": bm_client.token,
    }
    result = template.substitute(values)

    with open(bm_auth_path, "w") as bm_auth_yaml:
        bm_auth_yaml.write(result)
        click.echo(
            "Successful login. API Token stored in ~/{}.".format(BITMAKER_AUTH_NAME)
        )
