<h1 align="center"> estela CLI </h1>

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![version](https://img.shields.io/badge/version-0.1-blue)](https://github.com/bitmakerla/estela-cli)
[![python-version](https://img.shields.io/badge/python-v3.10-orange)](https://www.python.org)


estela CLI is a command line client to interact with the estela API. It allows the user to perform the following actions:
- Link a Scrapy project with a project in estela.
- Create projects, jobs, and cronjobs in estela.
- Get the data of a job.

```bash
$ estela
Usage: estela [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  context  Show your current context
  create   Create a resource
  data     Retrieve data from a given job and save it locally
  delete   Delete a resource
  deploy   Deploy Scrapy project to estela API
  init     Initialize estela project for existing scrapy project
  list     Display the available resources
  login    Save your credentials
  logout   Remove your credentials
  stop     Stop an active job or cronjob
  update   Update a resource
```

## Installation

estela CLI is available on PyPI:

```bash
$ python -m pip install estela
```

Or, you can install estela CLI manually:

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
