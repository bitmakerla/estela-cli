import os
import unittest

from estela_cli.estela_client import EstelaClient, DefaultEstelaClient
from estela_cli.login import env_login, DEFAULT_ESTELA_API_HOST
from estela_cli.init import delete_estela_template, gen_estela_yaml, gen_dockerfile, delete_dockerfile
from estela_cli.utils import get_estela_settings, get_estela_dockerfile_path
from estela_cli.templates import (
    DATA_DIR,
    DOCKERFILE,
    DOCKERFILE_NAME,
    ESTELA_YAML,
    ESTELA_YAML_NAME,
    DOCKER_DEFAULT_REQUIREMENTS,
    DOCKER_DEFAULT_PYTHON_VERSION,
    ESTELA_DIR,
)
from dotenv import load_dotenv


class TestEstelaClient(unittest.TestCase):
    # client = None

    # def __init__(self, *args, **kwargs):
    #     self.client = env_login()
    #     super().__init__(*args, **kwargs)

    def test_gen_estela_yaml(self):
        estela_client = DefaultEstelaClient()
        gen_estela_yaml(estela_client, pid="ESTELA_PROJECT_ID")
        
        estela_settings = get_estela_settings()
        p_settings = estela_settings["project"]
        d_settings = estela_settings["deploy"]
        self.assertEqual(p_settings["pid"], "ESTELA_PROJECT_ID")
        self.assertEqual(str(p_settings["python"]), DOCKER_DEFAULT_PYTHON_VERSION)
        self.assertEqual(p_settings["requirements"], DOCKER_DEFAULT_REQUIREMENTS)
        self.assertEqual(d_settings["ignore"], [DATA_DIR])

        delete_estela_template()

    def test_generate_dockerfile(self):
        gen_dockerfile(DOCKER_DEFAULT_REQUIREMENTS)

        self.assertIn("FROM python", DOCKERFILE)
        self.assertIn("RUN", DOCKERFILE)

        delete_dockerfile()

    # def test_wrong_credentials(self):
    #     with self.assertRaises(Exception) as error:
    #         EstelaClient(
    #             DEFAULT_ESTELA_API_HOST,
    #             username="wrong_user",
    #             password="wrong_password",
    #         )
    #         self.assertEqual(
    #             str(error.exception), "['Unable to log in with provided credentials.']"
    #         )

    # def test_create_project(self):
    #     project_name = "test_project"
    #     project = self.client.create_project(name=project_name)
    #     self.assertIn("pid", project)
    #     self.assertIn("name", project)
    #     self.assertIn("container_image", project)
    #     self.assertEqual(project["name"], project_name)

    #     self.client.delete_project(project["pid"])

    # def test_get_project(self):
    #     project_name = "test_project"
    #     project = self.client.create_project(name=project_name)

    #     project = self.client.get_project(pid=project["pid"])

    #     self.assertIn("pid", project)
    #     self.assertIn("name", project)
    #     self.assertIn("container_image", project)
    #     self.assertEqual(project["name"], project_name)

    #     self.client.delete_project(project["pid"])

    # def test_not_found_project(self):
    #     with self.assertRaises(Exception) as error:
    #         self.client.get_project(pid="wrong_pid")
    #         self.assertIn("Not found.", str(error.exception))

    # def test_get_projects(self):
    #     project_name = "test_project"
    #     project = self.client.create_project(name=project_name)

    #     projects = self.client.get_projects()

    #     project = [
    #         proj
    #         for proj in projects
    #         if proj["name"] == project_name and proj["pid"] == project["pid"]
    #     ][0]

    #     self.assertIn("pid", project)
    #     self.assertIn("name", project)
    #     self.assertIn("container_image", project)
    #     self.assertEqual(project["name"], project_name)

    #     self.client.delete_project(project["pid"])


if __name__ == "__main__":
    load_dotenv()
    unittest.main()
