import os
import unittest

from bm_cli.bm_client import BmClient
from bm_cli.login import login, DEFAULT_BM_API_HOST
from dotenv import load_dotenv


class TestBMClient(unittest.TestCase):
    client = None

    def __init__(self, *args, **kwargs):
        self.client = login()
        super().__init__(*args, **kwargs)

    def test_wrong_credentials(self):
        with self.assertRaises(Exception) as error:
            BmClient(
                DEFAULT_BM_API_HOST, username="wrong_user", password="wrong_password"
            )
        self.assertEqual(
            str(error.exception), "['Unable to log in with provided credentials.']"
        )

    def test_create_project(self):
        project_name = "test_project"
        project = self.client.create_project(name=project_name)
        self.assertIn("pid", project)
        self.assertIn("name", project)
        self.assertIn("token", project)
        self.assertIn("container_image", project)
        self.assertIsNotNone(project["token"])
        self.assertIsNot(project["token"], "")
        self.assertEqual(project["name"], project_name)

        self.client.delete_project(project["pid"])

    def test_get_project(self):
        project_name = "test_project"
        project = self.client.create_project(name=project_name)

        project = self.client.get_project(pid=project["pid"])

        self.assertIn("pid", project)
        self.assertIn("name", project)
        self.assertIn("token", project)
        self.assertIn("container_image", project)
        self.assertIsNotNone(project["token"])
        self.assertIsNot(project["token"], "")
        self.assertEqual(project["name"], project_name)

        self.client.delete_project(project["pid"])

    def test_not_found_project(self):
        with self.assertRaises(Exception) as error:
            self.client.get_project(pid="wrong_pid")
        self.assertIn("Expecting value:", str(error.exception))

    def test_not_permission_project(self):
        with self.assertRaises(Exception) as error:
            self.client.get_project(pid="00000000-0000-0000-0000-000000000000")
        self.assertEqual(
            str(error.exception), "You do not have permission to perform this action."
        )

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
        self.assertIn("token", project)
        self.assertIn("container_image", project)
        self.assertIsNotNone(project["token"])
        self.assertIsNot(project["token"], "")
        self.assertEqual(project["name"], project_name)

        self.client.delete_project(project["pid"])

    def test_get_spiders_and_set_related_spiders(self):
        project = self.client.create_project(name="test_project")

        response = self.client.set_related_spiders(
            pid=project["pid"], spiders=["spider1", "spider2"]
        )
        spiders = self.client.get_spiders(pid=project["pid"])

        spider1 = [
            sp
            for sp in spiders
            if sp["name"] == "spider1" and sp["project"] == project["pid"]
        ][0]
        spider2 = [
            sp
            for sp in spiders
            if sp["name"] == "spider2" and sp["project"] == project["pid"]
        ][0]

        self.assertIn("spiders_names", response)
        self.assertIn("sid", spider1)
        self.assertIn("sid", spider2)

        self.client.delete_project(project["pid"])

    def test_create_spider_job(self):
        project = self.client.create_project(name="test_project")
        self.client.set_related_spiders(pid=project["pid"], spiders=["spider1"])
        spider = self.client.get_spiders(pid=project["pid"])[0]
        job = self.client.create_spider_job(
            pid=project["pid"], sid=spider["sid"], job_type="SINGLE_JOB"
        )

        self.assertIn("jid", job)
        self.assertIn("name", job)
        self.assertIn("args", job)
        self.assertIn("env_vars", job)
        self.assertIn("job_type", job)
        self.assertIn("schedule", job)
        self.assertEqual(job["job_status"], "WAITING")

        response = self.client.stop_spider_job(
            pid=project["pid"], sid=spider["sid"], jid=job["jid"]
        )
        self.assertEqual(response["job_status"], "STOPPED")

        self.client.delete_project(project["pid"])

    def test_get_spider_jobs(self):
        project = self.client.create_project(name="test_project")
        self.client.set_related_spiders(pid=project["pid"], spiders=["spider"])
        spider = self.client.get_spiders(pid=project["pid"])[0]
        job1 = self.client.create_spider_job(
            pid=project["pid"], sid=spider["sid"], job_type="SINGLE_JOB"
        )
        job2 = self.client.create_spider_job(
            pid=project["pid"], sid=spider["sid"], job_type="CRON_JOB"
        )

        jobs = self.client.get_spider_jobs(pid=project["pid"], sid=spider["sid"])

        job1 = [
            job
            for job in jobs
            if job["jid"] == job1["jid"] and job["spider"] == spider["sid"]
        ][0]
        job2 = [
            job
            for job in jobs
            if job["jid"] == job2["jid"] and job["spider"] == spider["sid"]
        ][0]

        self.assertIn("jid", job1)
        self.assertIn("jid", job2)
        self.assertEqual(job1["job_type"], "SINGLE_JOB")
        self.assertEqual(job2["job_type"], "CRON_JOB")

        self.client.stop_spider_job(
            pid=project["pid"], sid=spider["sid"], jid=job1["jid"]
        )
        self.client.stop_spider_job(
            pid=project["pid"], sid=spider["sid"], jid=job2["jid"]
        )
        self.client.delete_project(project["pid"])


if __name__ == "__main__":
    load_dotenv()
    unittest.main()
