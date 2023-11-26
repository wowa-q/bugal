"""Seervice layer of the bugal"""

import logging

from bugal import cfg
from bugal import model
from bugal import abstract as a


logger = logging.getLogger(__name__)


class CmdImportNewCsv(a.Command):
    ''' specifying command to import new csv file into db '''

    def __init__(self, rep: a.AbstractRepository,
                 stack: model.Stack,
                 handler_r: a.HandlerReadIF):
        self.repo = rep
        self.stack = stack
        self.handler_r = handler_r
        logger.info("Command initialized: CmdImportNewCsv")
        # self.csv_path = csv_path

    def execute(self) -> int:
        ''' execution of the specified command
        1. calculate csv hash
        2. pull csv hash: read history from db
        3. compare csv hashes
        4. get meta data
        5. pull transaction hashes
        6. read csv line transaction
        7. create transactions
        8. check checksum not available
        9. write transactions
        10. archive csv
        11. write history
        '''
        logger.info("# start execution CmdImportNewCsv #")
        # leave the function if checksum exists in DB history
        # search the checksum in the meta table
        csv_checksum = self.handler_r.get_checksum()
        # check if checksum already exists
        lresults = self.repo.find_csv_checksum(csv_checksum)
        if not lresults:
            meta = self.handler_r.get_meta_data()
            # first build history and init some data
            history_entry = self.stack.create_history(meta[0])
            if history_entry is None:
                logger.debug("History could not be created")
                raise cfg.ModelStackError

            ctr_t = 0
            # get transaction row
            for _, transrow in enumerate(self.handler_r.get_transactions()):
                for _, transaction_c in enumerate(transrow, 1):
                    transaction_m = self.stack.create_transaction(transaction_c)
                    lresults = self.repo.find_transaction_checksum(hash(transaction_m))
                    if lresults:
                        # an entry was found with the same hash -> transaction exists already
                        logger.warning("CmdImportNewCsv: transaction already imported: %s", transaction_m)
                        # exit the execution
                        continue
                    else:
                        self.repo.write_to_transactions(transaction_m)
                        ctr_t += 1
            if ctr_t > 0:
                self.repo.write_to_history(history_entry)
                self.handler_r.archive()
                logger.info("number of transaction imported: %s", ctr_t)
            # return number of imported transactions
            return ctr_t
        else:
            logger.warning("CmdImportNewCsv: CSV already imported")
            return -1


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
