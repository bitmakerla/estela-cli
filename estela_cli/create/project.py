import click

from estela_cli.login import login


SHORT_HELP = "Create a new project"


@click.command(short_help=SHORT_HELP)
@click.argument("name", required=True)
def estela_command(name):
    """Create a new project

    NAME is the project's name
    """

    estela_client = login()
    try:
        response = estela_client.create_project(name)
        click.echo("project/{} created.".format(name))
        click.echo(
            "Hint: Use 'estela init {}' to activate this project as a Scrapy project.\nHint: Use 'estela init {} -p requests' to activate it as a Requests project.".format(
                response["pid"],
                response["pid"],
            )
        )
    except Exception as ex:
        raise click.ClickException(str(ex))
