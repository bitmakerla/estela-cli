import os

import click

from tabulate import tabulate

from estela_cli.templates import CERTS_DIR


SHORT_HELP = "List the proxy CA certs bundled with this CLI"


@click.command(name="certs", short_help=SHORT_HELP)
def estela_command():
    certs_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "assets", CERTS_DIR
    )
    if not os.path.isdir(certs_path):
        click.echo("No bundled certs found.")
        return

    rows = []
    for filename in sorted(os.listdir(certs_path)):
        if not filename.endswith(".crt"):
            continue
        name = filename[: -len(".crt")]
        rows.append([name, filename])

    headers = ["NAME", "FILE"]
    click.echo(tabulate(rows, headers, numalign="left", tablefmt="plain"))
