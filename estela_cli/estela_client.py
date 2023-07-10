from datetime import date, timedelta

import requests

from estela_cli import __version__


class EstelaSimpleClient:
    token = None

    def __init__(self, host, username=None, password=None, token=None):
        self.host = host
        self.api_base = "{}/api".format(self.host)
        if token is None:
            data = {
                "username": username,
                "password": password,
            }
            response = self.post("auth/login", data)
            self.check_status(response, 200, "non_field_errors")
            self.token = response.json()["key"]
        else:
            self.token = token
            response = self.get("projects")
            self.check_status(response, 200)

    def url_for(self, endpoint):
        return "{}/{}".format(self.api_base, endpoint)

    def get_default_headers(self):
        headers = {"User-Agent": f"estela-cli/{__version__}"}
        if self.token:
            headers["Authorization"] = "Token {}".format(self.token)
        return headers

    def post(self, endpoint, data=None, params=None, files=None):
        if files is None:
            files = {}
        if params is None:
            params = {}
        if data is None:
            data = {}
        headers = self.get_default_headers()
        return requests.post(
            self.url_for(endpoint),
            json=data,
            headers=headers,
            params=params,
            files=files,
        )

    def get(self, endpoint, params=None, paginated=False):
        if params is None:
            params = {}
        headers = self.get_default_headers()
        response = requests.get(self.url_for(endpoint), headers=headers, params=params)
        if paginated:
            self.check_status(response, 200)
            response = response.json()
            next_page = response["next"]
            content = response["results"]
            while next_page:
                response = requests.get(
                    self.url_for(endpoint), headers=headers, params=params
                )
                self.check_status(response, 200)
                response = response.json()
                content += response["results"]
                next_page = response["next"]
            return content
        return response

    def put(self, endpoint, data=None, params=None):
        if params is None:
            params = {}
        if data is None:
            data = {}
        headers = self.get_default_headers()
        return requests.put(
            self.url_for(endpoint), data=data, headers=headers, params=params
        )

    def delete(self, endpoint, data=None, params=None):
        if params is None:
            params = {}
        if data is None:
            data = {}
        headers = self.get_default_headers()
        return requests.delete(
            self.url_for(endpoint), headers=headers, data=data, params=params
        )

    def check_status(self, response, status_code, error_field="detail"):
        if response.status_code != status_code:
            response_json = response.json()
            if error_field in response_json:
                raise Exception(response_json[error_field])
            else:
                raise Exception(str(response_json))


class EstelaClient(EstelaSimpleClient):
    def get_projects(self):
        endpoint = "projects"
        response = self.get(endpoint, paginated=True)
        return response

    def get_project(self, pid):
        endpoint = "projects/{}".format(pid)
        response = self.get(endpoint)
        self.check_status(response, 200)
        return response.json()

    def create_project(self, name):
        endpoint = "projects"
        data = {"name": name}
        response = self.post(endpoint, data=data)
        self.check_status(response, 201)
        return response.json()
    
    def update_project(self, pid, **kwargs):
        endpoint = "projects/{}".format(pid)
        data = {
            **kwargs,
        }
        response = self.put(endpoint, data=data)
        self.check_status(response, 200)
        return response.json()

    def delete_project(self, pid):
        endpoint = "projects/{}".format(pid)
        response = self.delete(endpoint)
        self.check_status(response, 204)

    def get_spiders(self, pid):
        endpoint = "projects/{}/spiders".format(pid)
        response = self.get(endpoint, paginated=True)
        return response

    def get_spider(self, pid, sid):
        endpoint = "projects/{}/spiders/{}".format(pid, sid)
        response = self.get(endpoint)
        self.check_status(response, 200)
        return response.json()

    def upload_project(self, pid, project_zip):
        endpoint = "projects/{}/deploys".format(pid)
        files = {"project_zip": project_zip}
        response = self.post(endpoint, files=files)
        self.check_status(response, 201)
        return response.json()

    def get_spider_cronjobs(self, pid, sid):
        endpoint = "projects/{}/spiders/{}/cronjobs".format(pid, sid)
        response = self.get(endpoint, paginated=True)
        return response

    def get_spider_cronjobs_with_tag(self, pid, sid, tag):
        endpoint = "projects/{}/spiders/{}/cronjobs?tag={}".format(pid, sid, tag)
        response = self.get(endpoint, paginated=True)
        return response

    def get_spider_cronjob(self, pid, sid, cjid):
        endpoint = "projects/{}/spiders/{}/cronjobs/{}".format(pid, sid, cjid)
        response = self.get(endpoint)
        self.check_status(response, 200)
        return response.json()

    def get_spider_jobs(self, pid, sid):
        endpoint = "projects/{}/spiders/{}/jobs".format(pid, sid)
        response = self.get(endpoint, paginated=True)
        return response

    def get_spider_jobs_with_tag(self, pid, sid, tag):
        endpoint = "projects/{}/spiders/{}/jobs?tag={}".format(pid, sid, tag)
        response = self.get(endpoint, paginated=True)
        return response

    def get_spider_job(self, pid, sid, jid):
        endpoint = "projects/{}/spiders/{}/jobs/{}".format(pid, sid, jid)
        response = self.get(endpoint)
        self.check_status(response, 200)
        return response.json()

    def get_spider_job_data(self, pid, sid, jid, datatype, last_chunk=None):
        endpoint = "projects/{}/spiders/{}/jobs/{}/data?type={}".format(
            pid, sid, jid, datatype
        )
        if last_chunk:
            endpoint += "&current_chunk={}".format(last_chunk)
        response = self.get(endpoint)
        self.check_status(response, 200)
        return response.json()

    def create_spider_job(self, pid, sid, args=[], env_vars=[], tags=[], day=None):
        endpoint = "projects/{}/spiders/{}/jobs".format(pid, sid)
        data = {
            "args": args,
            "env_vars": env_vars,
            "tags": tags,
            "data_status": "PENDING" if day else "PERSISTENT",
        }
        if day:
            data["data_expiry_days"] = f"{date.today() + timedelta(days=day)}"

        response = self.post(endpoint, data=data)
        self.check_status(response, 201)
        return response.json()

    def stop_spider_job(self, pid, sid, jid):
        endpoint = "projects/{}/spiders/{}/jobs/{}/stop".format(pid, sid, jid)
        response = self.put(endpoint)
        self.check_status(response, 200)
        return response.json()

    def create_spider_cronjob(
        self, pid, sid, schedule="", args=[], env_vars=[], tags=[], day=None
    ):
        endpoint = "projects/{}/spiders/{}/cronjobs".format(pid, sid)
        data = {
            "schedule": schedule,
            "cargs": args,
            "cenv_vars": env_vars,
            "ctags": tags,
            "data_status": "PENDING" if day else "PERSISTENT",
        }
        if day:
            data["data_expiry_days"] = f"0/{day}"

        response = self.post(endpoint, data=data)
        self.check_status(response, 201)
        return response.json()

    def update_spider_job(self, pid, sid, jid, day, persistent):
        endpoint = "projects/{}/spiders/{}/jobs/{}".format(pid, sid, jid)
        data = {}
        if persistent:
            data["data_status"] = "PERSISTENT"
        elif day and day >= 1:
            data["data_status"] = "PENDING"
            data["data_expiry_days"] = day

        response = self.put(endpoint, data=data)
        self.check_status(response, 200)
        return response.json()

    def update_spider_cronjob(self, pid, sid, cjid, status, schedule, day, persistent):
        endpoint = "projects/{}/spiders/{}/cronjobs/{}".format(pid, sid, cjid)
        data = {
            "status": status,
            "schedule": schedule,
        }
        if persistent:
            data["data_status"] = "PERSISTENT"
        if day and day >= 1:
            data["data_status"] = "PENDING"
            data["data_expiry_days"] = day

        response = self.put(endpoint, data=data)
        self.check_status(response, 200)
        return response.json()
