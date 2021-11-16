# Bitmaker Cloud CLI

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

```bash
$ bitmaker
Usage: bitmaker [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  context  Show your current context
  create   Create a resource
  delete   Delete a resource
  deploy   Deploy Scrapy project to Bitmaker Cloud
  init     Initialize bitmaker project for existing scrapy project
  list     Display the available resources
  login    Save your credentials
  logout   Remove your credentials
  stop     Stop an active job or cronjob
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
