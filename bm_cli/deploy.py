import os
import click

from zipfile import ZipFile, ZIP_DEFLATED
from bm_cli.utils import get_project_path, get_bm_settings
from bm_cli.login import login
from bm_cli.templates import OK_EMOJI, BITMAKER_DIR, BITMAKER_YAML_NAME, DATA_DIR


SHORT_HELP = "Deploy Scrapy project to Bitmaker Cloud"


def zip_project(pid, project_path):
    relroot = os.path.abspath(os.path.join(project_path, os.pardir))
    project_data_path = os.path.join(project_path,DATA_DIR)
    with ZipFile("{}.zip".format(pid), "w", ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(project_path):
            # ignoring dir with data from jobs
            if root == project_data_path:
                continue
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                arcname = os.path.join(os.path.relpath(root, relroot), file)
                zip.write(filename, arcname)

@click.command(short_help=SHORT_HELP)
def bm_command():
    bm_client = login()
    bm_settings = get_bm_settings()
    project_path = get_project_path()
    pid = bm_settings["project"]["pid"]

    try:
        bm_client.get_project(pid)
    except:
        raise click.ClickException(
            "Invalid project at {}/{}.".format(BITMAKER_DIR, BITMAKER_YAML_NAME)
        )

    zip_project(pid, project_path)

    try:
        response = bm_client.upload_project(pid, open("{}.zip".format(pid), "rb"))
    except:
        click.ClickException(
            "A problem occurred while uploading the project."
        )
    
    click.echo("{} Project uploaded successfully. Deploy {} underway.".format(OK_EMOJI, response["did"]))
