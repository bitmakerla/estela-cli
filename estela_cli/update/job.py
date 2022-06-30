import click

from estela_cli.login import login
from estela_cli.utils import get_estela_settings

SHORT_HELP = "Update a job"
VALID_STATUSES = ["ACTIVE", "DISABLED"]


@click.command(short_help=SHORT_HELP)
@click.argument("jid", required=True)
@click.argument("sid", required=True)
@click.argument("pid", required=False)
# @click.option(
#     "--status",
#     type=click.Choice(VALID_STATUSES, case_sensitive=False),
#     help="Set cronjob status",
# )
# @click.option(
#     "--schedule",
#     "-s",
#     type=click.STRING,
#     help="Set cronjob crontab schedule",
# )
@click.option(
    "--day",
    "-d",
    type=click.INT,
    help="Set spider cronjob data expiry days",
)
def estela_command(jid, sid, pid, day):
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

    if day is None:
        raise click.ClickException(
            "Days was not provided to update the job. Please specify the amount of days."
        )

    try:
        response = estela_client.update_spider_job(pid, sid, jid, day)
        click.echo(f"job/spider-job-{jid}-{pid} updated.")
    except Exception as ex:
        raise click.ClickException(
            "Some values are invalid or you do not have permission to perform this action."
        )
