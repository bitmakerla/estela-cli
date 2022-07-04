import click

from estela_cli.login import login
from estela_cli.utils import get_estela_settings, validate_positive

SHORT_HELP = "Update a cronjob"
VALID_STATUSES = ["ACTIVE", "DISABLED"]


@click.command(short_help=SHORT_HELP)
@click.argument("cjid", required=True)
@click.argument("sid", required=True)
@click.argument("pid", required=False)
@click.option(
    "--status",
    type=click.Choice(VALID_STATUSES, case_sensitive=False),
    help="Set cronjob status.",
)
@click.option(
    "--schedule",
    "-s",
    type=click.STRING,
    help="Set cronjob crontab schedule.",
)
@click.option(
    "--persistent",
    is_flag=True,
    default=None,
    help="Set job data as persistent.",
)
@click.option(
    "--day",
    "-d",
    type=click.INT,
    callback=validate_positive,
    help="Set spider cronjob data expiry days.",
)
def estela_command(cjid, sid, pid, status, schedule, day, persistent):
    """Update a cronjob

    \b
    SID is the spider's sid
    PID is the project's pid (active project by default)
    CJID is the cronjob's cjid
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

    if all([option is None for option in [status, schedule, day, persistent]]):
        raise click.ClickException(
            "No update option was provided to update the cronjob. Please specify at least one."
        )

    try:
        response = estela_client.update_spider_cronjob(
            pid, sid, cjid, status, schedule, day, persistent
        )
        click.echo(f"cronjob/spider-cjob-{cjid}-{pid} updated.")
    except Exception as ex:
        raise click.ClickException(
            "Some values are invalid or you do not have permission to perform this action."
        )
