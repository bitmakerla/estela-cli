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
    CERTS_DIR,
    DATA_DIR,
    DEFAULT_PROXY_CA,
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
    PROXY_CA_DOCKERFILE_BLOCK,
    PROXY_CA_FILENAME,
    SELENIUM_ENTRYPOINT_SH,
)

NO_PROXY_CA = "none"

ALLOWED_PLATFORMS = ["scrapy", "requests", "selenium"]
SHORT_HELP = "Initialize estela project for existing web scraping project"


def gen_estela_yaml(estela_client, entrypoint_path, proxy_ca, pid=None):
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
        "proxy_ca": proxy_ca,
    }

    result = template.substitute(values)

    with open(estela_yaml_path, "w") as estela_yaml:
        estela_yaml.write(result)
        click.echo("{} file created successfully.".format(ESTELA_YAML_NAME))


def gen_dockerfile(requirements_path, entrypoint_path, proxy_ca, platform="scrapy"):
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
    proxy_ca_block = PROXY_CA_DOCKERFILE_BLOCK if proxy_ca != NO_PROXY_CA else ""
    values = {
        "python_version": DOCKER_DEFAULT_PYTHON_VERSION,
        "requirements_path": requirements_path,
        "entrypoint": entrypoint_path,
        "proxy_ca_block": proxy_ca_block,
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


def resolve_proxy_ca_source(proxy_ca):
    """Return the absolute path of the cert to copy, or None for NO_PROXY_CA.

    - "none" -> None (skip)
    - "/abs/or/rel/path/foo.crt" (path-like) -> resolve to absolute path
    - "<name>" (no separator) -> assets/certs/<name>.crt bundled with the CLI
    """
    if proxy_ca == NO_PROXY_CA:
        return None

    looks_like_path = (
        os.sep in proxy_ca
        or proxy_ca.startswith(".")
        or proxy_ca.endswith(".crt")
        or proxy_ca.endswith(".pem")
    )
    if looks_like_path:
        return os.path.abspath(proxy_ca)

    return os.path.join(
        os.path.dirname(__file__), "assets", CERTS_DIR, "{}.crt".format(proxy_ca)
    )


def copy_proxy_ca(proxy_ca):
    src = resolve_proxy_ca_source(proxy_ca)
    if src is None:
        return
    if not os.path.exists(src):
        raise click.ClickException(
            "Proxy CA cert not found: {}. Use 'estela list certs' to see "
            "available bundled certs, or pass a local path.".format(src)
        )
    dst = os.path.join(ESTELA_DIR, PROXY_CA_FILENAME)
    if os.path.exists(dst):
        return
    shutil.copyfile(src, dst)
    click.echo("{}/{} created successfully.".format(ESTELA_DIR, PROXY_CA_FILENAME))


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
@click.option(
    "--proxy-ca",
    default=DEFAULT_PROXY_CA,
    help=(
        "Proxy CA cert to install in the spider image. Accepts a bundled "
        "name (see 'estela list certs'), a local path to a .crt/.pem file, "
        "or 'none' to disable."
    ),
    show_default=True,
)
def estela_command(pid, platform, requirements, proxy_ca):
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
    gen_estela_yaml(estela_client, platform_map[platform], proxy_ca, pid)
    copy_proxy_ca(proxy_ca)
    gen_dockerfile(requirements, platform_map[platform], proxy_ca, platform)
