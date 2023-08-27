
import pathlib

from . import cfg
from . import model
from . import abstract as a


class CmdImportNewCsv(a.Command):
    ''' specifying command to import new csv file into db '''

    def __init__(self, rep: a.AbstractRepository,
                 stack: model.Stack,
                 handler_r: a.HandlerReadIF,
                 csv_path: pathlib.Path):
        self.repo = rep
        self.stack = stack
        self.handler_r = handler_r
        self.csv_path = csv_path

    def execute(self) -> None:
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
        print(' # start execution *CmdImportNewCsv* # ')
        # self.handler_r.CSVImporter(self.csv_path)
        self.handler_r.input_type = cfg.TransactionListClassic
        meta = self.handler_r.get_meta_data()

        # leave the function if checksum exists in DB history
        # search the checksum in the meta table
        csv_checksum = self.handler_r.get_checksum(self.csv_path)
        # check if checksum already exists
        lresults = self.repo.find_csv_checksum(csv_checksum)
        if lresults:
            # an entry was found in the meta table -> csv is already imported
            print('CmdImportNewCsv: CSV already imported')
            # exit the execution
            return False
        else:
            history_entry = self.stack.create_history(meta)
            data = self.handler_r.get_transactions()
            transaction = self.stack.create_transaction(data)
            lresults = self.repo.find_transaction_checksum(hash(transaction))
            if lresults:
                # an entry was found with the same hash -> transaction exists already
                print('CmdImportNewCsv: transaction already imported')
                # exit the execution
                return False
            else:
                self.repo.write_to_transactions(transaction)
                self.repo.write_to_history(history_entry)

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
