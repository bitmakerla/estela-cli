import os
import docker
import yaml
import base64
import logging

from getpass import getpass
from configparser import ConfigParser
from string import Template
from .bm_client import BmClient


DOCKERFILE = """\
FROM python:$python_version

# must be in base image
RUN pip install git+https://github.com/bitmakerla/bitmaker-entrypoint.git

RUN mkdir -p /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN mkdir /fifo-data
"""

DOCKERFILE_NAME = 'Dockerfile-bitmaker'

BITMAKER_YAML = """\
project:
    pid: $project_pid
    bm_image: $container_image
"""

BITMAKER_YAML_NAME = 'bitmaker.yaml'


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


def get_project_path():
    return os.path.abspath('.')


def get_host():
    return os.environ.get('BM_HOST', 'http://localhost:8000')


def get_bm_settings():
    project_path = get_project_path()
    bm_yaml_path = os.path.join(project_path, 'bitmaker.yaml')
    assert os.path.exists(bm_yaml_path), 'bitmaker.yaml not found.'
    with open(bm_yaml_path, 'r') as bm_yaml:
        bm_config = yaml.full_load(bm_yaml)
    return bm_config


def gen_project_package():
    # Must be util for spider to be packaged
    project_path = get_project_path()
    cfg_path = os.path.join(project_path, 'scrapy.cfg')
    assert os.path.exists(cfg_path), 'No config file found'
    settings = ConfigParser()


def gen_bm_yaml(bm_client):
    project_path = get_project_path()
    bm_yaml_path = os.path.join(project_path, BITMAKER_YAML_NAME)

    if os.path.exists(bm_yaml_path):
        logging.info('bitmaker.yaml file already exist')
        return

    try:
        pid = input('Project ID: ')
        project = bm_client.get_project(pid)
    except Exception:
        logging.error('The project with id {} does not exist'.format(pid))
        return

    template = Template(BITMAKER_YAML)
    values = {
        'project_pid': pid,
        'container_image': project['container_image'],
    }
    result = template.substitute(values)

    with open(bm_yaml_path, 'w') as bm_yaml:
        bm_yaml.write(result)
        logging.info('bitmaker.yaml file created successfully')


def gen_dockerfile():
    project_path = get_project_path()
    dockerfile_path = os.path.join(project_path, DOCKERFILE_NAME)

    if os.path.exists(dockerfile_path):
        logging.info('Dockerfile already exists')
        return

    template = Template(DOCKERFILE)
    values = {
        'python_version': '3.6',
    }
    result = template.substitute(values)

    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write(result)
        logging.info('Dockerfile created successfully')


def build_image():
    project_path = get_project_path()
    bm_settings = get_bm_settings()
    docker_client = docker.from_env()
    docker_client.images.build(
        nocache=True,
        path=project_path,
        dockerfile=DOCKERFILE_NAME,
        tag=bm_settings['project']['bm_image'],
    )
    logging.info('Image built successfully')


def upload_image(bm_client):
    bm_settings = get_bm_settings()
    docker_client = docker.from_env()
    repository, image_name = bm_settings['project']['bm_image'].split(':')
    project = bm_client.get_project(bm_settings['project']['pid'])
    username, password = base64.b64decode(project['token']).decode().split(':')
    auth_config = {'username': username, 'password': password}
    docker_client.images.push(repository=repository, tag=image_name, auth_config=auth_config)
    logging.info('Image uploaded successfully')


def login():
    try:
        username = input('Username: ')
        password = getpass()
        bm_client = BmClient(username, password, get_host())
    except Exception:
        logging.error('You have entered an invalid username or password')
        return

    return bm_client


def init():
    bm_client = login()
    if not bm_client:
        return
    gen_bm_yaml(bm_client)
    gen_dockerfile()


def deploy():
    bm_client = login()
    if not bm_client:
        return
    logging.info('Building image...')
    build_image()
    logging.info('Uploading image...')
    upload_image(bm_client)
