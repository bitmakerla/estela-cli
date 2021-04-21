# Bitmaker Scraping Product CLI

## Install

```
python setup.py install
```

## Commands

To create Dockerfile

```
$ bm-gen-dockerfile
```

To create bitmaker.yaml

```
$ bm-gen-config
```

To build docker image

```
$ bm-build-image
```

To upload docker image

```
$ bm-upload-image
```

To deploy project (run spiders)

```
$ bm-deploy
```

## Testing

```
$ pip install -r requirements/test.txt
$ python tests.py
```
