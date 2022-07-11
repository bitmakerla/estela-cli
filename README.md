<h1 align="center"> Estela CLI </h1>

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![version](https://img.shields.io/badge/version-0.1-blue)](https://github.com/bitmakerla/estela-cli)
[![python-version](https://img.shields.io/badge/python-v3.10-orange)](https://www.python.org)


Estela CLI is the command line client to interact with Estela API. Allows the user to perform the following actions:
- Link a Scrapy project with a project in Estela.
- Create projects, jobs, and cronjobs in Estela.
- Get the data of a job.

```bash
$ estela
Usage: estela [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.
  -l, --local When init a project, indicate that you use local-registry       

Commands:
  context  Show your current context
  create   Create a resource
  data     Returns all the data of a job and saves it in a json file
  delete   Delete a resource
  deploy   Deploy Scrapy project to Estela API
  init     Initialize estela project for existing scrapy project
  list     Display the available resources
  login    Save your credentials
  logout   Remove your credentials
  stop     Stop an active job or cronjob
  update   Update a resource

Args:
  project  All projects or a project if it is followed by the ID of that project
  spider   All the spiders or a spider if it is followed by the ID of that spider
  job      All jobs or a job if the ID of that job follows
  cronjob  All cronjobs or a cronjob if it is followed by the ID of that cronjob 
```

## Installation

```bash
$ python setup.py install
```

## Testing

```bash
$ pip install -r requirements/test.txt
$ python tests.py
```

## Formatting 

```bash
$ pip install -r requirements/dev.txt
$ black .
```
