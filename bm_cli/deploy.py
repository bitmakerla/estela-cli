import os
import docker
import base64
import click
import json

from bm_cli.utils import get_project_path, get_bm_settings, get_bm_dockerfile_path
from bm_cli.login import login
from bm_cli.templates import CLOCK_EMOJI, BITMAKER_DIR, BITMAKER_YAML_NAME


SHORT_HELP = "Deploy Scrapy project to Bitmaker Cloud"


def build_image():
    project_path = get_project_path()
    bm_settings = get_bm_settings()
    try:
        docker_client = docker.from_env()
        click.echo("{} Building image ...".format(CLOCK_EMOJI))
        docker_client.images.build(
            nocache=True,
            path=project_path,
            dockerfile=get_bm_dockerfile_path(),
            tag=bm_settings["project"]["bm_image"],
        )
        docker_client.containers.prune()
    except Exception as ex:
        raise click.ClickException(str(ex))

    click.echo("Image built successfully.")


def upload_image(bm_client):
    bm_settings = get_bm_settings()

    repository, image_name = bm_settings["project"]["bm_image"].split(":")
    project = bm_client.get_project(bm_settings["project"]["pid"])
    username, password = base64.b64decode(project["token"]).decode().split(":")
    auth_config = {"username": username, "password": password}

    try:
        docker_client = docker.from_env()
        click.echo("{} Uploading image ...".format(CLOCK_EMOJI))
        docker_client.images.push(
            repository=repository, tag=image_name, auth_config=auth_config
        )
    except Exception as ex:
        raise click.ClickException(str(ex))

    click.echo("Image uploaded successfully.")


def update_spider_list(bm_client):
    bm_settings = get_bm_settings()
    project = bm_client.get_project(bm_settings["project"]["pid"])
    click.echo("{} Updating spider list ...".format(CLOCK_EMOJI))

    try:
        docker_client = docker.from_env()
        output = docker_client.containers.run(
            bm_settings["project"]["bm_image"], "bm-describe-project", auto_remove=True
        )
        spiders = json.loads(output)["spiders"]
        bm_client.set_related_spiders(project["pid"], spiders)
    except Exception as ex:
        raise click.ClickException(str(ex))

    click.echo("Spider list updated successfully.")


@click.command(short_help=SHORT_HELP)
def bm_command():
    bm_client = login()
    bm_settings = get_bm_settings()

    try:
        docker_client = docker.from_env()
    except:
        raise click.ClickException(
            "Cannot connect to the Docker daemon. Is the docker daemon running?"
        )

    try:
        bm_client.get_project(bm_settings["project"]["pid"])
    except:
        raise click.ClickException(
            "Invalid project at {}/{}.".format(BITMAKER_DIR, BITMAKER_YAML_NAME)
        )

    build_image()
    upload_image(bm_client)
    update_spider_list(bm_client)
