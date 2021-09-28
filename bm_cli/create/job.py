import click

from bm_cli.login import login
from bm_cli.utils import get_bm_settings


SHORT_HELP = "Create a new job"


def validate_key_value_format(ctx, param, value):
    try:
        key_value_pairs = []
        for pair in value:
            key, value = pair.split("=", 1)
            key_value_pairs.append({"name": key, "value": value})
        return key_value_pairs
    except:
        raise click.BadParameter("format must be 'NAME=VALUE'")


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
def bm_command(sid, pid, arg, env):
    """Create a new job

    \b
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
        response = bm_client.create_spider_job(pid, sid, "SINGLE_JOB", arg, env)
        click.echo("job/{} created.".format(response["name"]))
    except Exception as ex:
        raise click.ClickException("Cannot create the job for given SID and PID.")
