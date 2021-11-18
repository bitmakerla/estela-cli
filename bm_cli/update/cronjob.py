import click

from bm_cli.login import login
from bm_cli.utils import get_bm_settings

SHORT_HELP = "Stop an active job"
VALID_STATUSES = ["ACTIVE", "DISABLED"]


@click.command(short_help=SHORT_HELP)
@click.argument("cjid", required=True)
@click.argument("sid", required=True)
@click.argument("pid", required=False)
@click.option(
    "--status",
    type=click.Choice(VALID_STATUSES, case_sensitive=False),
    help="Set cronjob status",
)
@click.option(
    "--schedule",
    "-s",
    type=click.STRING,
    help="Set cronjob crontab schedule",
)
def bm_command(cjid, sid, pid, status, schedule):
    """Update a cronjob

    \b
    SID is the spider's sid
    PID is the project's pid (active project by default)
    CJID is the cronjob's cjid
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

    if status is None and schedule is None:
        raise click.ClickException(
            "Neither status nor schedule was provided to update the cronjob. Please specify either or both."
        )

    try:
        response = bm_client.update_spider_cronjob(pid, sid, cjid, status, schedule)
        click.echo(f"cronjob/spider-cjob-{cjid}-{pid} updated.")
    except Exception as ex:
        raise click.ClickException(
            "Some values are invalid or you do not have permission to perform this action."
        )
