import os
import yaml

from bm_cli.templates import BITMAKER_AUTH_NAME, BITMAKER_YAML_NAME


def get_project_path():
    return os.path.abspath(".")


def get_home_path():
    return os.path.expanduser("~")


def get_host_from_env():
    return os.environ.get("BM_API_HOST")


def get_username_from_env():
    return os.environ.get("BM_USERNAME")


def get_password_from_env():
    return os.environ.get("BM_PASSWORD")


def get_bm_settings():
    project_path = get_project_path()
    bm_yaml_path = os.path.join(project_path, BITMAKER_YAML_NAME)

    assert os.path.exists(bm_yaml_path), "{} not found.".format(BITMAKER_YAML_NAME)

    with open(bm_yaml_path, "r") as bm_yaml:
        bm_config = yaml.full_load(bm_yaml)

    return bm_config


def get_bm_auth():
    home_path = get_home_path()
    bm_auth_path = os.path.join(home_path, BITMAKER_AUTH_NAME)

    if not os.path.exists(bm_auth_path):
        return None

    with open(bm_auth_path, "r") as bm_auth_yaml:
        bm_auth = yaml.full_load(bm_auth_yaml)

    return bm_auth
