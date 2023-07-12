import os
import click

from string import Template
from estela_cli.login import login
from estela_cli.utils import (
    get_project_path,
    get_estela_yaml_path,
    get_estela_dockerfile_path,
)
from estela_cli.templates import (
    DATA_DIR,
    DOCKER_DEFAULT_ENTRYPOINT,
    DOCKER_REQUESTS_ENTRYPOINT,
    DOCKERFILE,
    DOCKERFILE_NAME,
    ESTELA_YAML,
    ESTELA_YAML_NAME,
    DOCKER_DEFAULT_REQUIREMENTS,
    DOCKER_DEFAULT_PYTHON_VERSION,
    ESTELA_DIR,
)

ALLOWED_PLATFORMS = ["scrapy", "requests"]
SHORT_HELP = "Initialize estela project for existing web scraping project"


def gen_estela_yaml(estela_client, entrypoint_path, pid=None):
    estela_yaml_path = get_estela_yaml_path()

    if os.path.exists(estela_yaml_path):
        raise click.ClickException("{} file already exists.".format(ESTELA_YAML_NAME))

    try:
        if pid is None:
            pid = click.prompt("Project ID")

        project = estela_client.get_project(pid)
    except:
        raise click.ClickException(
            "The project with id '{}' does not exists.".format(pid)
        )

    template = Template(ESTELA_YAML)
    values = {
        "project_pid": pid,
        "project_data_path": DATA_DIR,
        "python_version": DOCKER_DEFAULT_PYTHON_VERSION,
        "requirements_path": DOCKER_DEFAULT_REQUIREMENTS,
        "entrypoint": entrypoint_path,
    }

    result = template.substitute(values)

    with open(estela_yaml_path, "w") as estela_yaml:
        estela_yaml.write(result)
        click.echo("{} file created successfully.".format(ESTELA_YAML_NAME))


def gen_dockerfile(requirements_path, entrypoint_path):
    dockerfile_path = get_estela_dockerfile_path()

    if os.path.exists(dockerfile_path):
        raise click.ClickException(
            "{}/{} already exists.".format(ESTELA_DIR, DOCKERFILE_NAME)
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
        "entrypoint": entrypoint_path,
    }
    result = template.substitute(values)

    with open(dockerfile_path, "w") as dockerfile:
        dockerfile.write(result)
        click.echo("{}/{} created successfully.".format(ESTELA_DIR, DOCKERFILE_NAME))


@click.command(short_help=SHORT_HELP)
@click.argument("pid", required=True)
@click.option(
    "-p",
    "--platform",
    type=click.Choice(ALLOWED_PLATFORMS, case_sensitive=False),
    default="scrapy",
    help="Platform to use, it can be 'scrapy' or 'requests'",
    show_default=True,
)
@click.option(
    "-r",
    "--requirements",
    default=DOCKER_DEFAULT_REQUIREMENTS,
    help="Relative path to requirements inside your project",
    show_default=True,
)
def estela_command(pid, platform, requirements):
    """Initialize estela project

    PID is the project's pid
    """
    platform_map = {
        "scrapy": DOCKER_DEFAULT_ENTRYPOINT,
        "requests": DOCKER_REQUESTS_ENTRYPOINT,
    }
    if not os.path.exists(ESTELA_DIR):
        os.makedirs(ESTELA_DIR)
    estela_client = login()
    try:
        response = estela_client.update_project(pid, framework=platform.upper(), action="update")
    except Exception as e:
        raise click.ClickException("Could not update framework project: %s" % str(e))
    finally:
        click.echo(f"{pid} is initialized as a {platform.capitalize()} project.")
    gen_estela_yaml(estela_client, platform_map[platform], pid)
    gen_dockerfile(requirements, platform_map[platform])
