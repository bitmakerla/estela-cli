import click

from estela_cli.login import login
from estela_cli.utils import (
    get_estela_settings,
    set_tag_format,
    validate_key_value_format,
    validate_limit,
    validate_positive,
)

SHORT_HELP = "Create a new cronjob"


@click.command(short_help=SHORT_HELP)
@click.argument("schedule", required=True, type=click.STRING)
@click.argument("sid", required=True)
@click.argument("pid", required=False)
@click.option(
    "--arg",
    "-a",
    multiple=True,
    type=click.UNPROCESSED,
    callback=validate_key_value_format,
    help="Set spider cronjob argument NAME=VALUE (may be repeated)",
)
@click.option(
    "--env",
    "-e",
    multiple=True,
    type=click.UNPROCESSED,
    callback=validate_key_value_format,
    help="Set spider cronjob environment variable NAME=VALUE (may be repeated)",
)
@click.option(
    "--memory",
    "-m",
    type=click.STRING,
    callback=validate_limit,
    help="Set spider job memory limit (e.g. 256Mi, 1Gi).",
)
@click.option(
    "--tag",
    "-t",
    multiple=True,
    type=click.UNPROCESSED,
    callback=set_tag_format,
    help="Set spider cronjob tag (may have multiple)",
)
@click.option(
    "--day",
    "-d",
    type=click.INT,
    callback=validate_positive,
    help="Set spider cronjob data expiry days",
)
def estela_command(sid, pid, schedule, arg, env, memory, tag, day):
    """Create a new cronjob

    \b
    SCHEDULE is the crontab schedule expression for the cronjob
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
        response = estela_client.create_spider_cronjob(
            pid, sid, schedule, arg, env, memory, tag, day
        )
        click.echo("cronjob/{} created.".format(response["name"]))
    except Exception as ex:
        raise click.ClickException(
            "Cannot create the cronjob for given SID and PID. Is the crontab valid?"
        )
