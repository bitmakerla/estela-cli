import os
import sys

from configparser import ConfigParser
from string import Template


# This is a template
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


def gen_project_package():
    # Must be util for spider to be packaged
    project_path = os.path.abspath('.')
    cfg_path = os.path.join(project_path, 'scrapy.cfg')
    assert os.path.exists(cfg_path), 'No config file found'
    settings = ConfigParser()
    

def gen_dockerfile():
    project_path = os.path.abspath('.')
    dockerfile_path = os.path.join(project_path, 'Dockerfile')
    assert not os.path.exists(dockerfile_path), 'Dockerfile already exists'
    # crerate Dockerfile
    template = Template(DOCKERFILE)
    values = {
        'python_version':   '3',
    }
    result = template.substitute(values)
    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write(result)

