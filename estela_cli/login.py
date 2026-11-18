import os
import time
import webbrowser
from contextlib import contextmanager

import click
import requests

from estela_cli import __version__
from estela_cli.estela_client import EstelaClient
from estela_cli.set_token import describe
from estela_cli.utils import (
    fail,
    get_host_from_env,
    get_username_from_env,
    get_password_from_env,
    get_estela_auth,
    save_estela_auth,
)
from estela_cli.templates import ESTELA_AUTH_NAME, OK_EMOJI


DEFAULT_ESTELA_API_HOST = "http://localhost"

# How often to ask whether the code was approved.
POLL_SECONDS = 5


SHORT_HELP = "Log in from the browser"


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
    except Exception as ex:
        # The API says why — revoked, expired, unknown — and that is the part
        # worth repeating, since each one calls for something different.
        raise Exception(str(ex))

    return estela_client


def login():
    try:
        estela_client = env_login()
        click.echo(
            "You are currently using environment variables to configure estela CLI."
        )
        return estela_client
    except:
        pass

    # A stored key that stops working is not a reason to start asking for a
    # password: the fix is a new key, so say so and stop.
    if (get_estela_auth() or {}).get("token"):
        try:
            return yaml_login()
        except Exception as ex:
            raise fail(
                "{}\n"
                "The key stored in ~/{} is not usable. Run 'estela logout', then "
                "'estela login' for a new one.".format(ex, ESTELA_AUTH_NAME)
            )

    raise fail("You have not logged in. Run 'estela login' first.")


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


@click.command(name="login", short_help=SHORT_HELP)
@click.option(
    "--host",
    help="The estela API to log in to. Defaults to the one 'estela set-host' stored.",
)
@click.option(
    "--device",
    is_flag=True,
    help="Print the link instead of opening a browser, to approve from another device.",
)
def estela_command(host, device):
    """Log in from the browser.

    estela gives this CLI a key and a code. Approve the code in the web, signed
    in as yourself, and the key is stored in ~/.estela.yaml.

    For a script or CI, use 'estela set-token' with a key created in the web.
    """
    # A stored host is configuration, not a session: only a stored token means
    # someone is already logged in.
    estela_auth = get_estela_auth() or {}
    if estela_auth.get("token"):
        raise fail("You already logged in. To change credentials run 'estela logout' first.")

    host = (host or estela_auth.get("host") or "").rstrip("/")
    if not host:
        raise fail("No host set. Run 'estela set-host <url>' first, or pass --host.")

    headers = {"User-Agent": "estela-cli/{}".format(__version__)}
    try:
        response = requests.post(
            "{}/api/account/api-keys/cli-login".format(host), headers=headers, timeout=10
        )
        response.raise_for_status()
        started = response.json()
    except Exception as ex:
        raise fail("Could not start the login at {}.".format(host), ex)

    url = started["url"]
    click.echo("Your code: {}".format(started["code"]))
    opened = False
    if not device:
        with quiet_fds():
            opened = webbrowser.open(url)
    if opened:
        click.echo("Opened {}".format(url))
    else:
        click.echo("Open this link where you are signed in to estela:\n  {}".format(url))
    click.echo("Check that the page shows the same code, then approve it. Waiting...")

    # The key works once the code is approved, so trying it is how to know.
    key = started["key"]
    headers["Authorization"] = "Token {}".format(key)
    deadline = time.time() + started["expires_in"]
    while True:
        if time.time() > deadline:
            raise fail("The code expired. Run 'estela login' again.")
        time.sleep(POLL_SECONDS)
        try:
            me = requests.get("{}/api/auth/whoami".format(host), headers=headers, timeout=10)
        except requests.RequestException:
            continue  # a blip; the next try may get through
        if me.status_code == 200:
            break

    save_estela_auth(host=host, token=key)
    me = me.json()
    click.echo(
        "{} Logged in as {}. Key stored in ~/{}.".format(
            OK_EMOJI, me.get("username"), ESTELA_AUTH_NAME
        )
    )
    click.echo("This key can: {}.".format(describe(me.get("scopes"))))
    click.echo("Your key, shown only this once: {}".format(key))
