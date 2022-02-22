import click

from bm_cli.login import login
from bm_cli.utils import get_bm_settings, validate_key_value_format, set_tag_format


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
    help="Set spider cronjob tag (may have multiple)",
)
def bm_command(sid, pid, schedule, arg, env, tag):
    """Create a new cronjob

    \b
    SCHEDULE is the crontab schedule expression for the cronjob
    SID is the spider's sid
    PID is the project's pid (active project by default)
    """

    bm_client = login()
    if pid is None:
        try:
            bm_settings = get_bm_settings()
            pid = bm_settings["project"]["pid"]
        except:
            raise click.ClickException(
                "No active project in the current directory. Please specify the PID."
            )
    try:
        response = bm_client.create_spider_cronjob(pid, sid, schedule, arg, env, tag)
        click.echo("cronjob/{} created.".format(response["name"]))
    except Exception as ex:
        raise click.ClickException(
            "Cannot create the cronjob for given SID and PID. Is the crontab valid?"
        )