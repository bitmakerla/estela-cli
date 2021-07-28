from setuptools import setup, find_packages
from bm_cli.__main__ import __version__

setup(
    name="bitmaker",
    version=__version__,
    description="Bitmaker Command Line Interface",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "bitmaker = bm_cli.__main__:cli",
        ],
    },
    install_requires=[
        "requests",
        "docker",
        "pyyaml",
        "click",
    ],
)
