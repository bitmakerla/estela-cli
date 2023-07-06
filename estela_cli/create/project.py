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
            f"Hint: Use 'estela init {response['pid']}' to initialize a Scrapy project.\n"
            f"Hint: Use 'estela init {response['pid']} -p requests' to initialize a Requests project."
        )
    except Exception as ex:
        raise click.ClickException(str(ex))
