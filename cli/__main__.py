import os
import docker
import yaml
import base64

from configparser import ConfigParser
from string import Template
from .bm_client import BmClient


DOCKERFILE = """\
FROM python:$python_version

RUN pip install scrapy # must be requirements.txt

RUN mkdir -p /usr/src/app
COPY . /usr/src/app

# Entrypoint must be in pypi
# For now, the entrypoint should be in the folder
WORKDIR /usr/src/app/scraping-product-entrypoint
RUN python setup.py install

WORKDIR /usr/src/app
"""

BITMAKER_YAML = """\
project:
    pid: $project_pid
    bm_image: $container_image
"""


def get_project_path():
    return os.path.abspath('.')


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


def gen_dockerfile():
    project_path = get_project_path()
    dockerfile_path = os.path.join(project_path, 'Dockerfile')
    assert not os.path.exists(dockerfile_path), 'Dockerfile already exists'

    template = Template(DOCKERFILE)
    values = {
        'python_version':   '3',
    }
    result = template.substitute(values)
    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write(result)


def generate_config():
    project_path = get_project_path()
    bm_yaml_path = os.path.join(project_path, 'bitmaker.yaml')
    assert not os.path.exists(bm_yaml_path), 'bitmaker.yaml already exists.'

    bm_client = BmClient()
    project = bm_client.create_project('test')

    template = Template(BITMAKER_YAML)
    values = {
        'project_pid': project['pid'],
        'container_image': project['container_image']
    }
    result = template.substitute(values)
    with open(bm_yaml_path, 'w') as bm_yaml:
        bm_yaml.write(result)


def build_image():
    project_path = get_project_path()
    bm_settings = get_bm_settings()
    docker_client = docker.from_env()
    docker_client.images.build(path=project_path, tag=bm_settings['project']['bm_image'])


def upload_image():
    bm_settings = get_bm_settings()
    docker_client = docker.from_env()
    bm_client = BmClient()
    repository, image_name = bm_settings['project']['bm_image'].split(':')
    project = bm_client.get_project(bm_settings['project']['pid'])
    username, password = base64.b64decode(project['token']).decode().split(':')
    auth_config = {'username': username, 'password': password}
    docker_client.images.push(repository=repository, tag=image_name, auth_config=auth_config)


def deploy():
    bm_settings = get_bm_settings()
    bm_client = BmClient()
    spider = bm_client.create_spider(pid=bm_settings['project']['pid'], name='spider')
    bm_client.create_spider_job(pid=bm_settings['project']['pid'], sid=spider['sid'])
