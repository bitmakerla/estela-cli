# Auth templates

ESTELA_AUTH_NAME = ".estela.yaml"

ESTELA_AUTH = """\
token: $estela_token
host: $estela_host
"""


# Init project templates

ESTELA_DIR = ".estela"

DATA_DIR = "project_data"

DOCKER_APP_DIR = "/usr/src/app"

DOCKER_DEFAULT_PYTHON_VERSION = "3.6"

DOCKER_DEFAULT_REQUIREMENTS = "requirements.txt"

DOCKERFILE_NAME = "Dockerfile-estela"

DOCKERFILE = """\
FROM python:$python_version

# must be in base image
RUN pip install git+https://github.com/bitmakerla/estela-entrypoint.git

RUN mkdir -p {app_dir}
WORKDIR {app_dir}
COPY . {app_dir}

RUN pip install --no-cache-dir -r $requirements_path
RUN mkdir /fifo-data
""".format(
    app_dir=DOCKER_APP_DIR
)

ESTELA_YAML_NAME = "estela.yaml"

ESTELA_YAML = """\
project:
  pid: $project_pid
  python: $python_version
  requirements: $requirements_path
deploy:
  ignore: [$project_data_path]
"""

# General templates

OK_EMOJI = "\U00002705"
BAD_EMOJI = "\U0000274C"
CLOCK_EMOJI = "\U000023F3"
