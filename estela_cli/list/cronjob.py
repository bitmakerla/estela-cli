import click

from tabulate import tabulate
from estela_cli.login import login
from estela_cli.utils import (
    get_estela_settings,
    format_time,
    format_key_value_pairs,
    format_tags,
)

SHORT_HELP = "List cronjobs of a given spider"


@click.command(short_help=SHORT_HELP)
@click.argument("sid", required=True)
@click.argument("pid", required=False)
@click.option(
    "--tag",
    "-t",
    type=click.UNPROCESSED,
    help="Filter cronjobs by tag",
)
def estela_command(sid, pid, tag):
    """List cronjobs of a given spider

    \b
    SID is the spider's sid
    PID is the project's pid (active project by default)
    TAG is the tag used to filter cronjobs
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

    cronjobs = []
    if tag:
        cronjobs = estela_client.get_spider_cronjobs_with_tag(pid, sid, tag)
    else:
        cronjobs = estela_client.get_spider_cronjobs(pid, sid)

    cronjobs = [
        [
            cronjob["cjid"],
            cronjob["status"],
            cronjob["schedule"],
            format_tags(cronjob["ctags"]),
            format_key_value_pairs(cronjob["cargs"]),
            format_key_value_pairs(cronjob["cenv_vars"]),
        ]
        for cronjob in cronjobs
    ]

    headers = ["CJID", "STATUS", "SCHEDULE", "TAGS", "ARGS", "ENV VARS"]
    click.echo(tabulate(cronjobs, headers, numalign="left", tablefmt="plain"))
