
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
        1. read csv file
        2. create transactions
        3. create history
        4. read history from db
        5. check checksum not available
        6. write transactions
        7. write history
        '''
        print(' # start execution *CmdImportNewCsv* # ')
        self.handler_r.CSVImporter(self.csv_path)
        self.handler_r.input_type = cfg.TransactionListClassic
        self.stack.create_history()
        self.repo.get_history()

        print(' # start execution *CmdImportNewCsv* # ')
        csv_meta = {}
        print(f'CmdImportNewCsv: {self.csv_file}')

        with open(self.csv_file, 'rb') as file:
            # calculate first the checksum of the given csv file
            checksum = hashlib.md5(file.read()).hexdigest().upper()

        # search the checksum in the meta table
        (return_c, lresults) = self.db_handler.find_checksum(checksum)
        # check the response code

        if return_c == RC.META_TABLE_OK:
            if len(lresults) > 0:
                # an entry was found in the meta table -> csv is already imported
                print('CmdImportNewCsv: CSV already imported')
                print(lresults)
                return RC.NONE
            else:
                # no entry was found -> import can be continued
                # 1. get data for meta entry
                with open(self.csv_file, 'r') as file:
                    for row in file:
                        # print(row.split(';'))
                        # Konto is in the first row
                        csv_meta['konto'] = row.split(';')[1]
                        break
                csv_meta['name'] = self.csv_file
                csv_meta['checksum'] = checksum
                # 2. import csv data
                (return_c, csv_ln) = self.dkb_ld.get_lines_as_list_of_dicts(self.csv_file)
                self.db_handler.import_dkb_csv(csv_ln, csv_meta)
                # 3. create meta entry
                self.db_handler.create_csv_meta(csv_meta)
                return RC.OK

        if return_c == RC.META_TABLE_NOK:
            return RC.NOK

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
