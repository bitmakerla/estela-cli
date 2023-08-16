import logging
import os
from zipfile import ZIP_DEFLATED, ZipFile

import click

from estela_cli.login import login
from estela_cli.templates import ESTELA_DIR, ESTELA_YAML_NAME, OK_EMOJI
from estela_cli.utils import _in, get_estela_settings, get_project_path

TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")


def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kws)


logging.Logger.trace = trace
logger = logging.getLogger(__name__)

SHORT_HELP = "Deploy Scrapy project to estela API"


def zip_project(pid, project_path, estela_settings):
    relroot = os.path.abspath(os.path.join(project_path, os.pardir))
    archives_to_ignore = estela_settings["deploy"]["ignore"]
    zip_file_path = "{}.zip".format(pid)
    with ZipFile(zip_file_path, "w", ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(project_path):
            # ignoring dir with data from jobs
            rel_root = root.replace("{}/".format(project_path), "")
            if _in(rel_root, archives_to_ignore):
                logger.trace(f"Ignoring {rel_root}")
                continue

            # add directory (needed for empty dirs)
            zip_file.write(root, os.path.relpath(root, relroot))

            for file in files:
                filename = os.path.join(root, file)

                if file == zip_file_path:
                    logger.trace(f"Ignoring {filename}")
                    continue

                arcname = os.path.join(os.path.relpath(root, relroot), file)
                logger.trace(f"Adding {filename} to the zip file.")
                zip_file.write(filename, arcname)


def verify_requrements(requirements_path):
    project_path = get_project_path()
    requirements_local_path = os.path.join(project_path, requirements_path)
    if not os.path.exists(requirements_local_path):
        raise click.ClickException("The requirements file does not exist.")


@click.command(name="deploy", short_help=SHORT_HELP)
@click.option(
    "-v", "--verbose", count=True, help="Increase verbosity level (e.g., -v, -vv)."
)
def estela_command(verbose):
    if verbose == 1:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose >= 2:
        logging.basicConfig(level=TRACE_LEVEL)
    else:
        logging.basicConfig(level=logging.INFO)

    estela_client = login()
    logger.debug(f"Successfully logged in to {estela_client.host}")
    estela_settings = get_estela_settings()
    logger.debug(f"Successfully read estela settings: {estela_settings}")
    project_path = get_project_path()
    p_settings = estela_settings["project"]
    pid = p_settings["pid"]
    logger.debug(f"Project path: {project_path}")

    try:
        logger.debug(f"Verifying project exists...")
        estela_client.get_project(pid)
        logger.debug(f"Verified project exists.")
    except:
        raise click.ClickException(
            "Invalid project at {}/{}.".format(ESTELA_DIR, ESTELA_YAML_NAME)
        )

    logger.debug(f"Verifying requirements...")
    verify_requrements(p_settings["requirements"])
    logger.debug(f"Successfully verified requirements.")

    logger.debug(f"Zipping project for upload to estela...")
    zip_project(pid, project_path, estela_settings)
    logger.debug(f"Successfully zipped the project.")

    response = {}
    try:
        logger.debug(f"Uploading project...")
        response = estela_client.upload_project(pid, "{}.zip".format(pid))
        logger.debug(f"Successfully uploaded the project.")
    except Exception as e:
        os.remove("{}.zip".format(pid))
        logger.debug(str(e))
        raise click.ClickException("A problem occurred while uploading the project.")

    click.echo(
        "{} Project uploaded successfully. Deploy {} underway.".format(
            OK_EMOJI, response.get("did")
        )
    )
    os.remove("{}.zip".format(pid))
