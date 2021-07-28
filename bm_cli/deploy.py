import os
import docker
import base64
import click

from bm_cli.utils import get_project_path, get_bm_settings
from bm_cli.login import login
from bm_cli.templates import DOCKERFILE_NAME


SHORT_HELP = "Deploy Scrapy project to Bitmaker Cloud"


def build_image():
    project_path = get_project_path()
    bm_settings = get_bm_settings()
    try:
        docker_client = docker.from_env()
        click.echo("Building image...")
        docker_client.images.build(
            nocache=True,
            path=project_path,
            dockerfile=DOCKERFILE_NAME,
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
        click.echo("Uploading image...")
        docker_client.images.push(
            repository=repository, tag=image_name, auth_config=auth_config
        )
    except Exception as ex:
        raise click.ClickException(str(ex))

    click.echo("Image uploaded successfully.")


@click.command(short_help=SHORT_HELP)
def bm_command():
    bm_client = login()
    build_image()
    upload_image(bm_client)
