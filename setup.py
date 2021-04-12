from setuptools import setup, find_packages

setup(
    name='bitmaker mesh',
    version='0.1',
    description='Dockerfile creation',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bm-gen-dockerfile = cli.__main__:gen_dockerfile',
        ],
    },
)
