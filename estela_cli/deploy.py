import os
import click

from string import Template
from zipfile import ZipFile, ZIP_DEFLATED
from estela_cli.utils import (
    get_project_path,
    get_estela_settings,
    _in,
    get_estela_dockerfile_path,
)
from estela_cli.login import login
from estela_cli.templates import (
    OK_EMOJI,
    ESTELA_DIR,
    ESTELA_YAML_NAME,
    DOCKERFILE,
    DOCKERFILE_NAME,
)


SHORT_HELP = "Deploy Scrapy project to estela API"


def zip_project(pid, project_path):
    relroot = os.path.abspath(os.path.join(project_path, os.pardir))
    estela_settings = get_estela_settings()
    archives_to_ignore = estela_settings["deploy"]["ignore"]
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


def update_dockerfile(requirements_path, python_version, entrypoint):
    dockerfile_path = get_estela_dockerfile_path()

    project_path = get_project_path()
    requirements_local_path = os.path.join(project_path, requirements_path)
    if not os.path.exists(requirements_local_path):
        raise click.ClickException("The requirements file does not exist.")

    template = Template(DOCKERFILE)
    values = {
        "python_version": python_version,
        "requirements_path": requirements_path,
        "entrypoint": entrypoint,
    }
    result = template.substitute(values)
    with open(dockerfile_path, "r") as dock:
        if result == dock.read():
            click.echo(
                "{}/{} not changes to update.".format(ESTELA_DIR, DOCKERFILE_NAME)
            )
            return

    with open(dockerfile_path, "w+") as dockerfile:
        dockerfile.write(result)
        click.echo("{}/{} updated successfully.".format(ESTELA_DIR, DOCKERFILE_NAME))


@click.command(short_help=SHORT_HELP)
def estela_command():
    estela_client = login()
    estela_settings = get_estela_settings()
    project_path = get_project_path()
    p_settings = estela_settings["project"]
    pid = p_settings["pid"]

    try:
        estela_client.get_project(pid)
    except:
        raise click.ClickException(
            "Invalid project at {}/{}.".format(ESTELA_DIR, ESTELA_YAML_NAME)
        )

    update_dockerfile(
        p_settings["requirements"],
        p_settings["python"],
        p_settings["entrypoint"],
    )

    zip_project(pid, project_path)

    response = {}
    try:
        response = estela_client.upload_project(pid, open("{}.zip".format(pid), "rb"))
    except:
        os.remove("{}.zip".format(pid))
        raise click.ClickException("A problem occurred while uploading the project.")

    click.echo(
        "{} Project uploaded successfully. Deploy {} underway.".format(
            OK_EMOJI, response.get("did")
        )
    )
    os.remove("{}.zip".format(pid))
