# Auth templates

BITMAKER_AUTH_NAME = ".bitmaker.yaml"

BITMAKER_AUTH = """\
token: $bm_token
host: $bm_host
"""


# Init project templates

DOCKER_APP_DIR = "/usr/src/app"

DOCKER_DEFAULT_REQUIREMENTS = "requirements.txt"

DOCKERFILE_NAME = "Dockerfile-bitmaker"

DOCKERFILE = """\
FROM python:$python_version

# must be in base image
RUN pip install git+https://github.com/bitmakerla/bitmaker-entrypoint.git

RUN mkdir -p {app_dir}
WORKDIR {app_dir}
COPY . {app_dir}

RUN pip install --no-cache-dir -r $requirements_path
RUN mkdir /fifo-data
""".format(
    app_dir=DOCKER_APP_DIR
)

BITMAKER_YAML_NAME = "bitmaker.yaml"

BITMAKER_YAML = """\
project:
  pid: $project_pid
  bm_image: $container_image
"""
