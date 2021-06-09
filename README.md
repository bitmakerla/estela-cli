# Bitmaker Scraping Product CLI

## Install

```
python setup.py install
```

## Commands

To init a Bitmaker project (create Dockerfile and bitmaker.yaml)

```
$ bm-init
```

To build docker image

```
$ bm-build-image
```

To upload docker image

```
$ bm-upload-image
```

To deploy project (build and upload)

```
$ bm-deploy
```

## Testing

```
$ pip install -r requirements/test.txt
$ python tests.py
```
