import os
import shutil
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
    DOCKERFILE_SELENIUM,
    ESTELA_YAML,
    ESTELA_YAML_NAME,
    DOCKER_DEFAULT_REQUIREMENTS,
    DOCKER_DEFAULT_PYTHON_VERSION,
    ESTELA_DIR,
    PROXY_CA_NAME,
    SELENIUM_ENTRYPOINT_SH,
)

ALLOWED_PLATFORMS = ["scrapy", "requests", "selenium"]
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


def gen_dockerfile(requirements_path, entrypoint_path, platform="scrapy"):
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

    dockerfile_template = DOCKERFILE_SELENIUM if platform == "selenium" else DOCKERFILE
    template = Template(dockerfile_template)
    values = {
        "python_version": DOCKER_DEFAULT_PYTHON_VERSION,
        "requirements_path": requirements_path,
        "entrypoint": entrypoint_path,
    }
    result = template.substitute(values)

    with open(dockerfile_path, "w") as dockerfile:
        dockerfile.write(result)
        click.echo("{}/{} created successfully.".format(ESTELA_DIR, DOCKERFILE_NAME))

    if platform == "selenium":
        entrypoint_sh_path = os.path.join(ESTELA_DIR, "entrypoint.sh")
        with open(entrypoint_sh_path, "w") as f:
            f.write(SELENIUM_ENTRYPOINT_SH)
        click.echo("{}/entrypoint.sh created successfully.".format(ESTELA_DIR))


def copy_proxy_ca():
    src = os.path.join(os.path.dirname(__file__), "assets", PROXY_CA_NAME)
    dst = os.path.join(ESTELA_DIR, PROXY_CA_NAME)
    if os.path.exists(dst):
        return
    shutil.copyfile(src, dst)
    click.echo("{}/{} created successfully.".format(ESTELA_DIR, PROXY_CA_NAME))


@click.command(name="init", short_help=SHORT_HELP)
@click.argument("pid", required=True)
@click.option(
    "-p",
    "--platform",
    type=click.Choice(ALLOWED_PLATFORMS, case_sensitive=False),
    default="scrapy",
    help="Platform to use: 'scrapy', 'requests', or 'selenium'",
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

    - PID is the project's pid
    """
    platform_map = {
        "scrapy": DOCKER_DEFAULT_ENTRYPOINT,
        "requests": DOCKER_REQUESTS_ENTRYPOINT,
        "selenium": DOCKER_REQUESTS_ENTRYPOINT,
    }
    # Selenium uses REQUESTS framework in the API
    framework = "REQUESTS" if platform == "selenium" else platform.upper()
    if not os.path.exists(ESTELA_DIR):
        os.makedirs(ESTELA_DIR)
    estela_client = login()
    try:
        response = estela_client.update_project(pid, framework=framework, action="update")
    except Exception as e:
        raise click.ClickException("Could not update framework project: %s" % str(e))
    finally:
        click.echo(f"{pid} is initialized as a {platform.capitalize()} project.")
    gen_estela_yaml(estela_client, platform_map[platform], pid)
    copy_proxy_ca()
    gen_dockerfile(requirements, platform_map[platform], platform)
