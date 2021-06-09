from setuptools import setup, find_packages

setup(
    name='bitmaker mesh',
    version='0.1',
    description='Dockerfile creation',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bm-build-image = cli.__main__:build_image',
            'bm-upload-image = cli.__main__:upload_image',
            'bm-init = cli.__main__:init',
            'bm-deploy = cli.__main__:deploy',
        ],
    },
    install_requires=[
        'requests',
        'docker',
        'pyyaml',
    ]
)
