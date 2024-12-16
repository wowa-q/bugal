"""command line interface for the bugal App
The user can access the services from bugal App throug this CLI
"""

from pathlib import Path
import logging
import sys

import click

from bugal.srvc import service
from bugal.cfg import cfg

logger = logging.getLogger(__name__)


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
