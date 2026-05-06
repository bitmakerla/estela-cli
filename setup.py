from setuptools import setup, find_packages

setup(
    name="estela",
    version="0.3.4",
    description="Estela Command Line Interface",
    packages=find_packages(),
    include_package_data=True,
    package_data={"estela_cli": ["assets/certs/*.crt"]},
    entry_points={
        "console_scripts": [
            "estela = estela_cli.__main__:cli",
        ],
    },
    install_requires=[
        "requests",
        "docker",
        "pyyaml",
        "click",
        "tabulate",
        "requests",
        "requests-toolbelt",
        "tqdm",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
)
