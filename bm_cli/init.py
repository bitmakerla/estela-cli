import os
import click

from string import Template
from bm_cli.login import login
from bm_cli.utils import (
    get_project_path,
    get_bm_yaml_path,
    get_bm_dockerfile_path,
)
from bm_cli.templates import (
    DATA_DIR,
    DOCKERFILE,
    DOCKERFILE_NAME,
    BITMAKER_YAML,
    BITMAKER_YAML_NAME,
    DOCKER_DEFAULT_REQUIREMENTS,
    DOCKER_DEFAULT_PYTHON_VERSION,
    BITMAKER_DIR,
)


SHORT_HELP = "Initialize bitmaker project for existing scrapy project"


def gen_bm_yaml(bm_client, pid=None):
    bm_yaml_path = get_bm_yaml_path()

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
        "project_data_path": DATA_DIR,
        "python_version": DOCKER_DEFAULT_PYTHON_VERSION,
        "requirements_path": DOCKER_DEFAULT_REQUIREMENTS,
    }

    result = template.substitute(values)

    with open(bm_yaml_path, "w") as bm_yaml:
        bm_yaml.write(result)
        click.echo(
            "{}/{} file created successfully.".format(BITMAKER_DIR, BITMAKER_YAML_NAME)
        )


def gen_dockerfile(requirements_path):
    dockerfile_path = get_bm_dockerfile_path()

    if os.path.exists(dockerfile_path):
        raise click.ClickException(
            "{}/{} already exists.".format(BITMAKER_DIR, DOCKERFILE_NAME)
        )

    project_path = get_project_path()
    requirements_local_path = os.path.join(project_path, requirements_path)
    if not os.path.exists(requirements_local_path):
        with open(requirements_local_path, "w") as requirementes:
            pass

    template = Template(DOCKERFILE)
    values = {
        "python_version": DOCKER_DEFAULT_PYTHON_VERSION,
        "requirements_path": requirements_path,
    }
    result = template.substitute(values)

    with open(dockerfile_path, "w") as dockerfile:
        dockerfile.write(result)
        click.echo("{}/{} created successfully.".format(BITMAKER_DIR, DOCKERFILE_NAME))


@click.command(short_help=SHORT_HELP)
@click.argument("pid", required=True)
@click.option(
    "-r",
    "--requirements",
    default=DOCKER_DEFAULT_REQUIREMENTS,
    help="Relative path to requirements inside your project",
    show_default=True,
)
def bm_command(pid, requirements):
    """Initialize bitmaker project

    PID is the project's pid
    LOCAL is a flag that indicate if the registry host is local
    """

    if not os.path.exists(BITMAKER_DIR):
        os.makedirs(BITMAKER_DIR)

    bm_client = login()
    gen_bm_yaml(bm_client, pid)
    gen_dockerfile(requirements)
