import click

from estela_cli.login import login
from estela_cli.utils import (
    get_estela_settings,
    validate_key_value_format,
    set_tag_format,
    validate_positive,
)


SHORT_HELP = "Create a new job"


@click.command(short_help=SHORT_HELP)
@click.argument("sid", required=True)
@click.argument("pid", required=False)
@click.option(
    "--arg",
    "-a",
    multiple=True,
    type=click.UNPROCESSED,
    callback=validate_key_value_format,
    help="Set spider job argument NAME=VALUE (may be repeated)",
)
@click.option(
    "--env",
    "-e",
    multiple=True,
    type=click.UNPROCESSED,
    callback=validate_key_value_format,
    help="Set spider job environment variable NAME=VALUE (may be repeated)",
)
@click.option(
    "--tag",
    "-t",
    multiple=True,
    type=click.UNPROCESSED,
    callback=set_tag_format,
    help="Set spider job tag (may have multiple)",
)
@click.option(
    "--day",
    "-d",
    type=click.INT,
    callback=validate_positive,
    help="Set spider job data expiry days",
)
def estela_command(sid, pid, arg, env, tag, day):
    """Create a new job

    \b
    SID is the spider's sid
    PID is the project's pid (active project by default)
    """

    estela_client = login()
    if pid is None:
        try:
            estela_settings = get_estela_settings()
            pid = estela_settings["project"]["pid"]
        except:
            raise click.ClickException(
                "No active project in the current directory. Please specify the PID."
            )
    try:
        response = estela_client.create_spider_job(pid, sid, arg, env, tag, day)
        click.echo("job/{} created.".format(response["name"]))
    except Exception as ex:
        raise click.ClickException("Cannot create the job for given SID and PID.")
