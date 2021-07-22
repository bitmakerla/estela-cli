import os
import click

from string import Template
from bm_cli.login import login
from bm_cli.utils import get_project_path
from bm_cli.templates import (
    DOCKERFILE,
    DOCKERFILE_NAME,
    BITMAKER_YAML,
    BITMAKER_YAML_NAME,
    DOCKER_DEFAULT_REQUIREMENTS,
)


SHORT_HELP = "Create Dockerfile and Bitmaker file for existing scrapy project"


def gen_bm_yaml(bm_client, pid=None):
    project_path = get_project_path()
    bm_yaml_path = os.path.join(project_path, BITMAKER_YAML_NAME)

    if os.path.exists(bm_yaml_path):
        raise click.ClickException("{} file already exists.".format(BITMAKER_YAML_NAME))

    try:
        if pid is None:
            pid = click.prompt("Project ID")

        project = bm_client.get_project(pid)
    except:
        raise click.ClickException(
            "The project with id '{}' does not exists.".format(pid)
        )

    template = Template(BITMAKER_YAML)
    values = {
        "project_pid": pid,
        "container_image": project["container_image"],
    }
    result = template.substitute(values)

    with open(bm_yaml_path, "w") as bm_yaml:
        bm_yaml.write(result)
        click.echo("{} file created successfully.".format(BITMAKER_YAML_NAME))


def gen_dockerfile(requirements_path):
    project_path = get_project_path()
    dockerfile_path = os.path.join(project_path, DOCKERFILE_NAME)

    if os.path.exists(dockerfile_path):
        raise click.ClickException("{} already exists.".format(DOCKERFILE_NAME))

    requirements_local_path = os.path.join(project_path, requirements_path)
    if not os.path.exists(requirements_local_path):
        with open(requirements_local_path, "w") as requirementes:
            pass

    template = Template(DOCKERFILE)
    values = {
        "python_version": "3.6",
        "requirements_path": requirements_path,
    }
    result = template.substitute(values)

    with open(dockerfile_path, "w") as dockerfile:
        dockerfile.write(result)
        click.echo("{} created successfully.".format(DOCKERFILE_NAME))


@click.command(short_help=SHORT_HELP)
@click.option("--pid", help="Bitmaker project ID")
@click.option(
    "-r",
    "--requirements",
    default=DOCKER_DEFAULT_REQUIREMENTS,
    help="Relative path to requirements inside your project",
    show_default=True,
)
def bm_command(pid, requirements):
    bm_client = login()
    gen_bm_yaml(bm_client, pid)
    gen_dockerfile(requirements)
