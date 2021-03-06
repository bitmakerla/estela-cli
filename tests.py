import os
import unittest

from estela_cli.estela_client import EstelaClient
from estela_cli.login import login, DEFAULT_ESTELA_API_HOST
from dotenv import load_dotenv


class TestEstelaClient(unittest.TestCase):
    client = None

    def __init__(self, *args, **kwargs):
        self.client = login()
        super().__init__(*args, **kwargs)

    def test_wrong_credentials(self):
        with self.assertRaises(Exception) as error:
            EstelaClient(
                DEFAULT_ESTELA_API_HOST,
                username="wrong_user",
                password="wrong_password",
            )
            self.assertEqual(
                str(error.exception), "['Unable to log in with provided credentials.']"
            )

    def test_create_project(self):
        project_name = "test_project"
        project = self.client.create_project(name=project_name)
        self.assertIn("pid", project)
        self.assertIn("name", project)
        self.assertIn("container_image", project)
        self.assertEqual(project["name"], project_name)

        self.client.delete_project(project["pid"])

    def test_get_project(self):
        project_name = "test_project"
        project = self.client.create_project(name=project_name)

        project = self.client.get_project(pid=project["pid"])

        self.assertIn("pid", project)
        self.assertIn("name", project)
        self.assertIn("container_image", project)
        self.assertEqual(project["name"], project_name)

        self.client.delete_project(project["pid"])

    def test_not_found_project(self):
        with self.assertRaises(Exception) as error:
            self.client.get_project(pid="wrong_pid")
            self.assertIn("Not found.", str(error.exception))

    def test_get_projects(self):
        project_name = "test_project"
        project = self.client.create_project(name=project_name)

        projects = self.client.get_projects()

        project = [
            proj
            for proj in projects
            if proj["name"] == project_name and proj["pid"] == project["pid"]
        ][0]

        self.assertIn("pid", project)
        self.assertIn("name", project)
        self.assertIn("container_image", project)
        self.assertEqual(project["name"], project_name)

        self.client.delete_project(project["pid"])


if __name__ == "__main__":
    load_dotenv()
    unittest.main()
