import click

from estela_cli.login import login
from estela_cli.utils import get_estela_settings

SHORT_HELP = "Stop an active job"


@click.command(short_help=SHORT_HELP)
@click.argument("jid", required=True)
@click.argument("sid", required=True)
@click.argument("pid", required=False)
def estela_command(jid, sid, pid):
    """Stop an active job

    \b
    JID is the job's jid
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
        response = estela_client.stop_spider_job(pid, sid, jid)
        click.echo(f"job/spider-job-{jid}-{pid} stopped.")
    except Exception as ex:
        raise click.ClickException(
            "The job is not active, does not exist, or you do not have permission to perform this action."
        )
