# Bitmaker Scraping Product CLI

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

```bash
$ bitmaker
Usage: bitmaker [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  context  Show your current context
  deploy   Deploy Scrapy project to Bitmaker Cloud
  init     Create Dockerfile and Bitmaker file for existing scrapy project
  login    Save your credentials
  logout   Remove your credentials
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
