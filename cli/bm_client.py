import requests
import os


class BmSimpleClient:
    token = None

    def __init__(self, username=None, password=None, host='http://localhost:8000'):
        if username is None:
            username = os.environ.get('BM_USERNAME'),
        if password is None:
            password = os.environ.get('BM_PASSWORD')
        self.api_base = '{}/api'.format(host)
        data = {
            'username': username,
            'password': password,
        }
        response = self.post('login/', data)
        self.check_status(response, 200, 'non_field_errors')
        self.token = response.json()['token']

    def url_for(self, endpoint):
        return '{}/{}'.format(self.api_base, endpoint)

    def get_default_headers(self):
        headers = {}
        if self.token:
            headers['Authorization'] = 'Token {}'.format(self.token)
        return headers

    def post(self, endpoint, data=None, params=None):
        if params is None:
            params = {}
        if data is None:
            data = {}
        headers = self.get_default_headers()
        return requests.post(self.url_for(endpoint),
                             data=data,
                             headers=headers,
                             params=params)

    def get(self, endpoint, params=None, paginated=False):
        if params is None:
            params = {}
        headers = self.get_default_headers()
        response = requests.get(self.url_for(endpoint),
                                headers=headers,
                                params=params)
        if paginated:
            self.check_status(response, 200)
            response = response.json()
            next_page = response["next"]
            content = response["results"]
            while next_page:
                response = requests.get(self.url_for(endpoint),
                                        headers=headers,
                                        params=params)
                self.check_status(response, 200)
                response = response.json()
                content += response["results"]
                next_page = response["next"]
            return content
        return response

    def put(self, endpoint, data, params=None):
        if params is None:
            params = {}
        if data is None:
            data = {}
        headers = self.get_default_headers()
        return requests.put(self.url_for(endpoint),
                            data=data,
                            headers=headers,
                            params=params)

    def delete(self, endpoint, data=None, params=None):
        if params is None:
            params = {}
        if data is None:
            data = {}
        headers = self.get_default_headers()
        return requests.delete(self.url_for(endpoint),
                               headers=headers,
                               data=data,
                               params=params)

    def check_status(self, response, status_code, error_field='detail'):
        if response.status_code != status_code:
            response_json = response.json()
            if error_field in response_json:
                raise Exception(response_json[error_field])
            else:
                raise Exception(str(response_json))


class BmClient(BmSimpleClient):
    def get_projects(self):
        endpoint = 'projects'
        response = self.get(endpoint, paginated=True)
        return response

    def get_project(self, pid):
        endpoint = 'projects/{}'.format(pid)
        response = self.get(endpoint)
        self.check_status(response, 200)
        return response.json()

    def create_project(self, name):
        endpoint = 'projects'
        data = {'name': name}
        response = self.post(endpoint, data=data)
        self.check_status(response, 201)
        return response.json()

    def delete_project(self, pid):
        endpoint = 'projects/{}'.format(pid)
        response = self.delete(endpoint)
        self.check_status(response, 204)

    def get_spiders(self, pid):
        endpoint = 'projects/{}/spiders'.format(pid)
        response = self.get(endpoint, paginated=True)
        return response

    def get_spider(self, pid, sid):
        endpoint = 'projects/{}/spiders/{}'.format(pid, sid)
        response = self.get(endpoint)
        self.check_status(response, 200)
        return response.json()

    def create_spider(self, pid, name):
        endpoint = 'projects/{}/spiders'.format(pid)
        data = {'name': name}
        response = self.post(endpoint, data=data)
        self.check_status(response, 201)
        return response.json()

    def delete_spider(self, pid, sid):
        endpoint = 'projects/{}/spiders/{}'.format(pid, sid)
        response = self.delete(endpoint)
        self.check_status(response, 204)

    def get_spider_jobs(self, pid, sid):
        endpoint = 'projects/{}/spiders/{}/jobs'.format(pid, sid)
        response = self.get(endpoint, paginated=True)
        return response

    def get_spider_job(self, pid, sid, jid):
        endpoint = 'projects/{}/spiders/{}/jobs/{}'.format(pid, sid, jid)
        response = self.get(endpoint)
        self.check_status(response, 200)
        return response.json()

    def create_spider_job(self, pid, sid):
        endpoint = 'projects/{}/spiders/{}/jobs'.format(pid, sid)
        response = self.post(endpoint)
        self.check_status(response, 201)
        return response.json()

    def delete_spider_job(self, pid, sid, jid):
        endpoint = 'projects/{}/spiders/{}/jobs/{}'.format(pid, sid, jid)
        response = self.delete(endpoint)
        self.check_status(response, 204)