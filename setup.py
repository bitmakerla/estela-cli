from setuptools import setup, find_packages

setup(
    name="bitmaker",
    version="0.1",
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
        "tabulate",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)
