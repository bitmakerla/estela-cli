import click

from bm_cli.login import login
from bm_cli.utils import get_bm_settings, get_project_path, save_data
from bm_cli.templates import OK_EMOJI, BAD_EMOJI

SHORT_HELP = "Get data from a job"

@click.command(short_help=SHORT_HELP)
@click.argument("jid", required=True)
@click.argument("sid", required=True)
@click.argument("pid", required=False)
def bm_command(jid, sid, pid, ):
    """Get data from a job

    \b
    SID is the spider's sid
    PID is the project's pid (active project by default)
    JID is the job's id
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
        response = bm_client.get_spider_job_data(pid, sid, jid)
        click.echo("{} Data retrieve succesfully.".format(OK_EMOJI))
    except Exception as ex:
        raise click.ClickException("{} Cannot get data".format(BAD_EMOJI))
    save_data("{}-{}.json".format(jid,pid), response)
    click.echo("{} Data saved succesfully.".format(OK_EMOJI))