"""
Seervice layer of the bugal
Der user interface greift hier drauf zu um mit der bugal zu interagieren.
Enthält Kommandos
Kann importieren:
- model: busines logic
- handler: um verschiedene Formate zu bearbeiten

#TODO: Wie stelle ich die Typsicherheit ohne der importe?
"""

import logging

from bugal.app import model as bmodel
# from bugal.app import fmodel as bmodel
# from bugal.app import csv_handler
# from bugal.app import xls_handler
# from bugal.app import gen_handler
from bugal.srvc import srvc_if as a
from libs import exceptions as err


logger = logging.getLogger(__name__)


class CmdImportCsv(a.Command):
    ''' specifying command to import new csv file into db '''

    def __init__(self, config):
        self.config = config
        logger.info("Command initialized: CmdImportCsv")
        
    def execute(self):
        
        # do some validations and store some handlers and data in the stack
        try:
            bmodel.validate_import_file(self.config)
        except err.NoCsvFilesFound:
            logger.warning(f"# CSV file was not found {self.config.import_path}")
        
        try:
            stack = bmodel.make_stack(self.config)
        except err.NoInputTypeSet:
            logger.warning(f"Input type not recognised: {self.config.import_type}")
        
        if len(stack.import_meta['checksum']) == 0:
            logger.warning("CSV hash not calculated for stack")
            raise err.ModelStackError
        
        result = bmodel.compare_hash(stack.import_meta['checksum'], self.config.dbpath)
        if result is not None:
            logger.warning("CSV hash exists already")
            raise err.ImportDuplicateHistory
        
        logger.info("# start execution CmdImportCsv #")
        ctr_t = bmodel.start_csv_import(self.config, stack)
        
        if ctr_t > 0:
            logger.info("number of transaction imported: %s", ctr_t)
            bmodel.update_history(self.config, stack)    
        
        result = bmodel.archive_import_file(self.config)
        if not result:
            logger.warning("History was not updated")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} Service interface for bugal operations"


class CmdFake(a.Command):
    """FAke Command for testing purposes

    Args:
        a (_type_): _description_
    """
    def __init__(self, dut: str):
        self.invoker = dut

    def execute(self) -> int:
        logger.info("# start execution CmdFake # %s", self.invoker)
        return 1

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} Testing interface for bugal operations"

################################################################
#                        Invoker                                #
################################################################


class Invoker():
    ''' The Invoker is associated with one or several commands. It sends a request
    to the command. '''

    def __init__(self) -> None:
        self._on_start = None
        self._main_command = None
        self._on_finish = None

    # Initialize commands.
    def set_on_start(self, command: a.Command):
        ''' setter '''
        self._on_start = command

    def set_main_command(self, command: a.Command):
        ''' setter '''
        self._main_command = command

    def set_on_finish(self, command: a.Command):
        ''' setter '''
        self._on_finish = command

    def run_commands(self) -> None:
        """
        The Invoker does not depend on concrete command or receiver classes. The
        Invoker passes a request to a receiver indirectly, by executing a
        command.
        """
        if isinstance(self._on_start, a.Command):
            self._on_start.execute()

        if isinstance(self._main_command, a.Command):
            self._main_command.execute()

        if isinstance(self._on_finish, a.Command):
            self._on_finish.execute()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} Service invoker"


#       *** PUBLIC APIs ***

def import_data(config):
    """Import one csv file into DB

    Args:
        config (_type_): configuration

    Returns:
        (message, result): _description_
    """
    message = ''   
    invoker = Invoker()
    invoker.set_main_command(CmdImportCsv(config))
    # invoker.set_main_command(CmdFake(config))
    # invoker.set_on_start(CmdFake(config))
    # invoker.set_on_finish(CmdFake(config))
    result = None           # run_commands soll das Ergebnis liefern
    invoker.run_commands()
    return (message, result)

def export_data(config):
    # hier export to excel
    pass