import click

from bm_cli.login import login


SHORT_HELP = "Delete an existing project"


@click.command(short_help=SHORT_HELP)
@click.argument("pid", required=True)
def bm_command(pid):
    """Delete a project

    PID is the project's pid
    """

    bm_client = login()
    try:
        bm_client.delete_project(pid)
        click.echo("project/{} deleted.".format(pid))
    except Exception as ex:
        raise click.ClickException(
            "The project does not exist, or you do not have permission to perform this action."
        )
