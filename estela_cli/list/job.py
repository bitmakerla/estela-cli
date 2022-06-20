import click

from tabulate import tabulate
from estela_cli.login import login
from estela_cli.utils import (
    get_estela_settings,
    format_time,
    format_key_value_pairs,
    format_tags,
)

SHORT_HELP = "List jobs of a given spider"


@click.command(short_help=SHORT_HELP)
@click.argument("sid", required=True)
@click.argument("pid", required=False)
@click.option(
    "-t",
    "--tag",
    type=click.UNPROCESSED,
    help="Filter jobs by tag",
)
def estela_command(sid, pid, tag):
    """List jobs of a given spider

    \b
    SID is the spider's sid
    PID is the project's pid (active project by default)
    TAG is the tag used to filter jobs
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
        estela_client.get_spider(pid, sid)
    except Exception as ex:
        raise click.ClickException(
            "The spider does not exist, or you do not have permission to perform this action."
        )

    jobs = []
    if tag:
        jobs = estela_client.get_spider_jobs_with_tag(pid, sid, tag)
    else:
        jobs = estela_client.get_spider_jobs(pid, sid)

    jobs = [
        [
            job["jid"],
            job["job_status"].capitalize(),
            format_tags(job["tags"]),
            format_key_value_pairs(job["args"]),
            format_key_value_pairs(job["env_vars"]),
            format_time(job["created"]),
        ]
        for job in jobs
    ]

    headers = ["JID", "STATUS", "TAGS", "ARGS", "ENV VARS", "CREATED"]
    click.echo(tabulate(jobs, headers, numalign="left", tablefmt="plain"))
