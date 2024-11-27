"""Seervice layer of the bugal"""

import logging

from bugal import model
from bugal.libs import handler as hand
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


class CmdImportClassic(a.Command):
    def __init__(self,
                 trepo: a.AbstractRepository,
                 hrepo: a.AbstractRepository,
                 handler: a.AbstractInputHandler):
        self.hrepo = hrepo          # History repository where to import
        self.trepo = trepo          # Transation repository where to import

        self.handler = handler      # handler to read csv file
        logger.info("Command initialized: CmdImportNewCsv")

    def execute(self) -> None:
        '''
        1. get meta data with calculated csv hash
        2. search csv hash in DB: read history from db
        3. 
        4. 
        5. pull transaction hashes
        6. read csv line transaction
        7. create transactions
        8. check checksum not available
        9. write transactions
        10. archive csv
        11. write history
         interface API '''
        # raise NotImplementedError
        ctr_t = 0
        # 1. calculate csv hash
        meta = self.handler.get_meta_from_classic()
        
        # 2. search csv hash in DB: read history from db
        db_hash = self.hrepo.get_history(hash_=meta['checksum'])
        if db_hash is not None:
            if isinstance(db_hash, list):
                if len(db_hash) > 0:
                    raise err.ImportDuplicateHistory('csv file with hash found in History Table - LIST')
            else:
                raise err.ImportDuplicateHistory('csv file with hash found in History Table')
        
        # 3. pull transaction from csv
        for tr in self.handler.get_transaction_from_classic():
            # 4. check if transaction is already in DB
            checksum = hash(tr)
            db_tr = self.trepo.get_transaction(hash_=checksum)
            if db_tr is not None:
                # skip this transaction - it is already in DB
                continue
            # 5. push transaction to DB TODO: optimize - DB shall be saved only once and not at every transaction push
            self.trepo.add_transaction(tr)
            ctr_t += 1
        
        # 6. create History entry in DB
        if ctr_t > 0:
            history_entry = self.handler.get_history_from_classic(meta)
            self.hrepo.add_history(history_entry)
            # 7. archive the input file

    
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

def import_data(cfg_type):
    # hand.validate_path(cfg_type.path_)
    pth_check = hand.PathHandler().handle(cfg_type.path_)
    # invoker = Invoker()
    # invoker.set_main_command(CmdImportNewCsv())
    # invoker.set_on_start()
    # invoker.set_on_finish()
    # invoker.run_commands()
    return pth_check


#       *** PUBLIC APIs ***

def import_data(cfg_type):
    # hand.validate_path(cfg_type.path_)
    pth_check = hand.PathHandler().handle(cfg_type.path_)
    # invoker = Invoker()
    # invoker.set_main_command(CmdImportNewCsv())
    # invoker.set_on_start()
    # invoker.set_on_finish()
    # invoker.run_commands()
    return pth_check