import click

from estela_cli.login import login
from estela_cli.utils import get_estela_settings

SHORT_HELP = "Update a job"
VALID_STATUSES = ["ACTIVE", "DISABLED"]


@click.command(short_help=SHORT_HELP)
@click.argument("jid", required=True)
@click.argument("sid", required=True)
@click.argument("pid", required=False)
@click.option(
    "--persistent",
    "-p",
    type=click.BOOL,
    help="Set job data persistent",
)
@click.option(
    "--day",
    "-d",
    type=click.INT,
    help="Set spider job data expiry days",
)
def estela_command(jid, sid, pid, day, persistent):
    """Update a job

    \b
    SID is the spider's sid
    PID is the project's pid (active project by default)
    JID is the job's jid
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

    if day is None and persistent is None:
        raise click.ClickException(
            "Neither days nor data_status was not provided to update the job. Please specify the amount of days."
        )

    try:
        response = estela_client.update_spider_job(pid, sid, jid, day, persistent)
        click.echo(f"job/spider-job-{jid}-{pid} updated.")
    except Exception as ex:
        raise click.ClickException(
            "Some values are invalid or you do not have permission to perform this action."
        )
