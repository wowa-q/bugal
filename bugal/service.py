"""Seervice layer of the bugal"""

import logging
from datetime import date

from bugal import model
from bugal import repo
from bugal import abstract as a
from bugal import exceptions as err


logger = logging.getLogger(__name__)


class CmdImportNewCsv(a.Command):
    ''' specifying command to import new csv file into db '''

    def __init__(self,
                 trepo: a.AbstractRepository,
                 hrepo: a.AbstractRepository,
                 stack: model.Stack,
                 handler: a.HandlerReadIF):
        self.hrepo = hrepo          # History repository where to import
        self.trepo = trepo          # Transation repository where to import
        self.stack = stack          # stack model with business logic
        self.handler = handler      # handler to read csv file
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
        csv_checksum = self.handler.get_checksum()
        # check if checksum already exists
        found = self.hrepo.get_history(hash_=csv_checksum)
        if found is None:
            meta = self.handler.get_meta_data()
            # first build history and init some data
            history_entry = self.stack.create_history(meta[0])
            if history_entry is None:
                logger.debug("History could not be created")
                raise err.ModelStackError

            ctr_t = 0
            # get transaction row
            for _, transrow in enumerate(self.handler.get_transactions()):
                for _, transaction_c in enumerate(transrow, 1):
                    self.stack.set_src_account(meta[0]['account']) # TODO: the list needs to fit to the csv file
                    transaction_m = self.stack.create_transaction(transaction_c)
                    found = self.trepo.del_transaction(hash_=hash(transaction_m))
                    # only if no transaction with the same hash already exists
                    if found is not None:
                        # an entry was found with the same hash -> transaction exists already
                        logger.warning("CmdImportNewCsv: transaction already imported: %s", transaction_m)
                        # exit the execution
                        continue
                    else:
                        self.trepo.add_transaction(transaction_m)
                        ctr_t += 1
            if ctr_t > 0:
                self.hrepo.add_history(history_entry)
                self.handler.archive()
                logger.info("number of transaction imported: %s", ctr_t)
            # return number of imported transactions
            return ctr_t
        else:
            logger.warning("CmdImportNewCsv: CSV already imported")
            return -1

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} Service interface for bugal operations"


class CmdExportExcel(a.Command):
    """Specifying command to export excel file

    Args:
        a (_type_): _description_

    Returns:
        _type_: _description_
    """
    def __init__(self,
                 trepo: a.AbstractRepository,
                 handler: a.HandlerWriteIF) -> None:
        self.trepo = trepo          # Transation repository where to to get data
        self.handler = handler      # handler to write excel file
        self.date = None
        self.start_date = None
        self.end_date = None
        # self.db_pth = db_pth

    def set_filter(self, *args, **kwargs):
        """sets filter for retriving transactions

        Returns:
            _type_: _description_
        """
        if 'datum' == kwargs and len(args) == 2:
            self.date = args[0]
            self.end_date = args[1]
            # isinstance(args[0], datetime.Date)
        elif 'datum_range' in kwargs and len(args) == 2:
            self.start_date = args[0]
            self.end_date = args[1]
            print(f'Datum Range: {self.start_date} - {self.end_date}')
            if not isinstance(args[0], date):
                print(f'Transaction filter ist nicht datetime.date: {args} und {kwargs}')
                return
        else:

            print(f'Transaction filter wurden nicht gegesetzt: {args} und {kwargs}')
            return

    def execute(self) -> None:
        ''' execution of the specified command
        1. read data from DB
        2. ..
        '''
        # tctr = self.trepo.get_transaction_ctr()
        # print(f'# connection test, read transactions couters: {tctr}')
        # test = self.trepo.get_transaction(id_=1)
        # print(f'test conncetion with ID=1: {test}')
        self.handler.transactions = self.trepo.get_transaction(start_date=self.start_date,
                                                               end_date=self.end_date)
        # # print(f'# Anzahl der gefunden TRANSACTIONS: {self.handler.transactions}')

        if self.handler.transactions is None:
            print(f'Transactions wurden nicht gelesen zwischen: {self.start_date} und {self.end_date}')
            return
        self.trepo.deinit()
        self.handler.print()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} Service interface for bugal operations"


class CmdReadTransactions(a.Command):
    """Command to read transactions from DB
    """
    def __init__(self, db_pth) -> None:
        self.date = None
        self.start_date = None
        self.end_date = None
        self.db_pth = db_pth

    def set_filter(self, *args, **kwargs):
        """sets filter for retriving transactions

        Returns:
            _type_: _description_
        """
        if 'datum' in kwargs:
            self.date = args[0]
            self.end_date = args[1]
            # isinstance(args[0], datetime.Date)
        elif 'datum_range' in kwargs:
            self.start_date = args[0]
            self.end_date = args[1]
            # isinstance(args[0], datetime.Date)
        else:
            return None

    def execute(self) -> None:
        ''' interface API '''
        trepo = repo.TransactionsRepo(self.db_pth)
        trepo.get_transaction([self.start_date, self.end_date])
        print('READ TRANSACTIONS')


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
