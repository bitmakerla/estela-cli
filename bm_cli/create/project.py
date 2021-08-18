import click

from bm_cli.login import login


SHORT_HELP = "Create a new project"


@click.command(short_help=SHORT_HELP)
@click.argument("name", required=True)
def bm_command(name):
    """Create a new project

    NAME is the project's name
    """

    bm_client = login()
    try:
        response = bm_client.create_project(name)
        click.echo("project/{} created.".format(name))
        click.echo(
            "Hint: Run 'bitmaker init {}' to activate this project".format(
                response["pid"]
            )
        )
    except Exception as ex:
        raise click.ClickException(str(ex))
