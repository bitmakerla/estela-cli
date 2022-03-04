import os
import click

from string import Template
from zipfile import ZipFile, ZIP_DEFLATED
from bm_cli.utils import get_project_path, get_bm_settings, _in, get_bm_dockerfile_path
from bm_cli.login import login
from bm_cli.templates import OK_EMOJI, BITMAKER_DIR, BITMAKER_YAML_NAME, DOCKERFILE, DOCKERFILE_NAME


SHORT_HELP = "Deploy Scrapy project to Bitmaker Cloud"


def zip_project(pid, project_path):
    relroot = os.path.abspath(os.path.join(project_path, os.pardir))
    bm_settings = get_bm_settings()
    archives_to_ignore = bm_settings["deploy"]["ignore"]
    with ZipFile("{}.zip".format(pid), "w", ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(project_path):
            # ignoring dir with data from jobs
            rel_root = root.replace("{}/".format(project_path), "")
            if _in(rel_root, archives_to_ignore):
                continue
            # add directory (needed for empty dirs)
            zip.write(root, os.path.relpath(root, relroot))
            for file in files:
                filename = os.path.join(root, file)
                arcname = os.path.join(os.path.relpath(root, relroot), file)
                zip.write(filename, arcname)


def update_dockerfile(requirements_path, python_version):
    dockerfile_path = get_bm_dockerfile_path()

    project_path = get_project_path()
    requirements_local_path = os.path.join(project_path, requirements_path)
    if not os.path.exists(requirements_local_path):
        raise click.ClickException("The requirements file does not exist.")

    template = Template(DOCKERFILE)
    values = {
        "python_version": python_version,
        "requirements_path": requirements_path,
    }
    result = template.substitute(values)
    with open(dockerfile_path, "r") as dock:
        if result == dock.read():
            click.echo("{}/{} not changes to update.".format(BITMAKER_DIR, DOCKERFILE_NAME))
            return

    with open(dockerfile_path, "w+") as dockerfile:
        dockerfile.write(result)
        click.echo("{}/{} updated successfully.".format(BITMAKER_DIR, DOCKERFILE_NAME))


@click.command(short_help=SHORT_HELP)
def bm_command():
    bm_client = login()
    bm_settings = get_bm_settings()
    project_path = get_project_path()
    p_settings = bm_settings["project"]
    pid = p_settings["pid"]

    try:
        bm_client.get_project(pid)
    except:
        raise click.ClickException(
            "Invalid project at {}/{}.".format(BITMAKER_DIR, BITMAKER_YAML_NAME)
        )

    update_dockerfile(p_settings["requirements"], p_settings["python"])
    
    zip_project(pid, project_path)

    try:
        response = bm_client.upload_project(pid, open("{}.zip".format(pid), "rb"))
    except:
        click.ClickException("A problem occurred while uploading the project.")

    click.echo(
        "{} Project uploaded successfully. Deploy {} underway.".format(
            OK_EMOJI, response["did"]
        )
    )

    os.remove("{}.zip".format(pid))
