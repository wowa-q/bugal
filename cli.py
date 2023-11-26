"""command line interface for the bugal App
The user can access the services from bugal App throug this CLI
"""

from pathlib import Path
import logging
import sys

import click

from bugal import service
from bugal import model
from bugal import bugal_orm as repo     # TODO: needs to be replaced by the repo after refactoring
from bugal import handler
from bugal import cfg

logger = logging.getLogger(__name__)


def _get_receivers(csv_pth):

    repo_instance = repo.BugalOrm(cfg.DBFILE)
    # if cfg.TEST is True:
    #     repo_instance = repo.BugalOrm(cfg.FIXTURE_DIR, cfg.DB_NAME)
    # else:
    #     repo_instance = repo.BugalOrm(cfg.DBFILE)
    if cfg.TYPE == 'BETA':
        input_type = cfg.TransactionListBeta
    else:
        input_type = cfg.TransactionListClassic
    stack_instance = model.Stack(input_type)
    handler_instance = handler.CSVImporter(csv_pth)
    return repo_instance, stack_instance, handler_instance


def create_fake_invoker(dut: str):
    """creates invoker with FAKE command for testing cli

    Args:
        dut (str): The place from where the command was invoked

    Returns:
        Invoker: service.Invoker
    """
    invoker = service.Invoker()
    invoker.set_main_command(service.CmdFake(dut))
    return invoker


def create_import_csv_invoker(csv_pth: Path):
    """creates the import csv invoker by initialising receiver instances for commands

    Args:
        csv (Path): file path of th csv file to be imported

    Returns:
        service.Invoker: Invoker instance which can run the configured commands
    """

    rep, stack, handl = _get_receivers(csv_pth)
    import_invoker = service.Invoker()
    import_invoker.set_main_command(service.CmdImportNewCsv(rep, stack, handl))

    return import_invoker


@click.command()
@click.option("--cmd",
              "-cmd",
              required=True,
              help="Command to be executed")
def execute(cmd):
    """API for cli
    Args:
        import_csv (_type_): _description_
        classic (_type_): _description_
    """
    try:
        invoker = None
        # configure the invoker depndent on the provided command options
        if "import" in cmd:
            click.echo(f'Hello {cmd} will be executed!')
            csv_file = cfg.CSVFILE
            click.echo(f'Bugal Importing:  {csv_file}')
            logger.info("Import csv file requested: %s", csv_file)
            invoker = create_import_csv_invoker(csv_file)

        else:
            click.echo('INVALID COMMAND')
            sys.exit(1)
        # execute the invoker after configuration
        if invoker is not None:
            invoker.run_commands()
            click.echo(f'{cmd} finished')
        else:
            click.echo(f'{cmd} could not be executed. Invoker not configured')

    except NotImplementedError as err:
        logging.error(err.args[0])
        sys.exit(1)


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    execute()
