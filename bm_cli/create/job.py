import click

from bm_cli.login import login
from bm_cli.utils import get_bm_settings


SHORT_HELP = "Create a new job"


def validate_arg(ctx, param, value):
    try:
        args = []
        for pair in value:
            key, val = pair.split("=", 1)
            args.append({"name": key, "value": val})
        return args
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
    callback=validate_arg,
    help="Set spider job argument NAME=VALUE (may be repeated)",
)
def bm_command(sid, pid, arg):
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
        response = bm_client.create_spider_job(pid, sid, "SINGLE_JOB", arg)
        click.echo("job/{} created.".format(response["name"]))
    except Exception as ex:
        raise click.ClickException("Cannot create the job for given SID and PID.")
