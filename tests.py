import unittest
from cli.bm_client import BmClient
from dotenv import load_dotenv
import os


class TestBMClient(unittest.TestCase):
    client = None

    def __init__(self, *args, **kwargs):
        self.client = BmClient()
        super().__init__(*args, **kwargs)

    def test_wrong_credentials(self):
        with self.assertRaises(Exception) as error:
            BmClient(username='wrong_user', password='wrong_password')
        self.assertEqual(str(error.exception), "['Unable to log in with provided credentials.']")

    def test_create_project(self):
        project_name = 'test_project'
        project = self.client.create_project(name=project_name)
        self.assertIn('pid', project)
        self.assertIn('name', project)
        self.assertIn('token', project)
        self.assertIn('container_image', project)
        self.assertIsNotNone(project['token'])
        self.assertIsNot(project['token'], '')
        self.assertEqual(project['name'], project_name)

        self.client.delete_project(project['pid'])

    def test_get_project(self):
        project_name = 'test_project'
        project = self.client.create_project(name=project_name)

        project = self.client.get_project(pid=project['pid'])

        self.assertIn('pid', project)
        self.assertIn('name', project)
        self.assertIn('token', project)
        self.assertIn('container_image', project)
        self.assertIsNotNone(project['token'])
        self.assertIsNot(project['token'], '')
        self.assertEqual(project['name'], project_name)

        self.client.delete_project(project['pid'])

    def test_not_found_project(self):
        with self.assertRaises(Exception) as error:
            self.client.get_project(pid='wrong_pid')
        self.assertEqual(str(error.exception), 'Not found.')

    def test_get_projects(self):
        project_name = 'test_project'
        project = self.client.create_project(name=project_name)

        projects = self.client.get_projects()

        project = [proj for proj in projects if proj['name'] == project_name and proj['pid'] == project['pid']][0]

        self.assertIn('pid', project)
        self.assertIn('name', project)
        self.assertIn('token', project)
        self.assertIn('container_image', project)
        self.assertIsNotNone(project['token'])
        self.assertIsNot(project['token'], '')
        self.assertEqual(project['name'], project_name)

        self.client.delete_project(project['pid'])

    def test_create_spider(self):
        project = self.client.create_project(name='test_project')
        spider = self.client.create_spider(pid=project['pid'], name='test_spider')
        self.assertIn('sid', spider)
        self.assertIn('project', spider)
        self.assertEqual(spider['project'], project['pid'])
        self.client.delete_spider(project['pid'], spider['sid'])
        self.client.delete_project(project['pid'])

    def test_get_spider(self):
        project = self.client.create_project(name='test_project')
        spider = self.client.create_spider(pid=project['pid'], name='test_spider')
        spider = self.client.get_spider(pid=project['pid'], sid=spider['sid'])
        self.assertIn('sid', spider)
        self.assertIn('project', spider)
        self.assertEqual(spider['project'], project['pid'])
        self.client.delete_spider(project['pid'], spider['sid'])
        self.client.delete_project(project['pid'])

    def test_get_spiders(self):
        project_name = 'test_project'
        project = self.client.create_project(name=project_name)

        spider = self.client.create_spider(pid=project['pid'], name='test_spider')
        spiders = self.client.get_spiders(pid=project['pid'])

        spider = [spid for spid in spiders if spid['name'] == spider['name'] and spid['sid'] == spider['sid']][0]

        self.assertIn('sid', spider)
        self.assertIn('project', spider)
        self.assertEqual(spider['project'], project['pid'])

        self.client.delete_spider(project['pid'], spider['sid'])
        self.client.delete_project(project['pid'])

    def test_create_spider_job(self):
        project = self.client.create_project(name='test_project')
        spider = self.client.create_spider(pid=project['pid'], name='test_spider')
        job = self.client.create_spider_job(pid=project['pid'], sid=spider['sid'])

        self.assertIn('jid', job)
        self.assertIn('spider', job)
        self.assertIn('created', job)
        self.assertIn('status', job)
        self.assertIn('name', job)
        self.assertEqual(job['status'], 'RUNNING')
        self.assertEqual(job['spider'], spider['sid'])

        self.client.delete_spider_job(pid=project['pid'], sid=spider['sid'], jid=job['jid'])
        self.client.delete_spider(project['pid'], spider['sid'])
        self.client.delete_project(project['pid'])

    def test_get_spider_job(self):
        project = self.client.create_project(name='test_project')
        spider = self.client.create_spider(pid=project['pid'], name='test_spider')
        job = self.client.create_spider_job(pid=project['pid'], sid=spider['sid'])
        self.client.delete_spider_job(pid=project['pid'], sid=spider['sid'], jid=job['jid'])
        self.client.delete_spider(project['pid'], spider['sid'])
        self.client.delete_project(project['pid'])


if __name__ == '__main__':
    load_dotenv()
    unittest.main()
