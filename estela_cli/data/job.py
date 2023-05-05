import time

import click

from estela_cli.login import login
from estela_cli.templates import BAD_EMOJI, CLOCK_EMOJI, OK_EMOJI
from estela_cli.utils import get_estela_settings, save_chunk_data, save_data

SHORT_HELP = "Retrieve data from a job"
ALLOWED_DATA_TYPES = ["items", "requests", "logs", "stats"]
ALLOWED_DATA_FORMATS = ["json", "csv"]


@click.command(short_help=SHORT_HELP)
@click.argument("jid", required=True)
@click.argument("sid", required=True)
@click.argument("pid", required=False)
@click.option(
    "-t",
    "--datatype",
    type=click.Choice(ALLOWED_DATA_TYPES, case_sensitive=False),
    default="items",
)
@click.option(
    "-f",
    "--format",
    type=click.Choice(ALLOWED_DATA_FORMATS, case_sensitive=False),
    default="json",
)
def estela_command(
    jid,
    sid,
    pid,
    datatype,
    format,
):
    """Retrieve data from a given job

    \b
    SID is the spider's sid
    PID is the project's pid (active project by default)
    JID is the job's id
    DATATYPE is the type of data to retrieve
    FORMAT is the format to retrieve data
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

    tmp_filename = ".{}-{}-{}-{}-tmp".format(jid, pid, datatype, time.time())
    filename = "{}-{}-{}.{}".format(jid, pid, datatype, format)
    try:
        response = estela_client.get_spider_job_data(pid, sid, jid, datatype)
        with click.progressbar(
            length=int(response["count"]),
            label="{} Downloading job data".format(CLOCK_EMOJI),
            show_eta=True,
            show_percent=True,
            show_pos=True,
        ) as progress_bar:
            next_chunk = None
            while True:
                response = estela_client.get_spider_job_data(pid, sid, jid, datatype, next_chunk)
                chunk = response.get("results")
                save_chunk_data(tmp_filename, chunk)
                progress_bar.update(len(chunk))
                next_chunk = response.get("next_chunk")
                if next_chunk is None:
                    break
        click.echo("{} Data downloaded succesfully.".format(OK_EMOJI))
    except:
        raise click.ClickException(
            "{} Could not download the job data".format(BAD_EMOJI)
        )

    try:
        save_data(filename, tmp_filename, format)
        click.echo("{} Data saved succesfully.".format(OK_EMOJI))
    except:
        raise click.ClickException("{} Could not save the job data".format(BAD_EMOJI))
