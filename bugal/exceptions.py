"""Global Bugal exceptions
"""


### Busyness logic Errors ###
class BaseBugalModelError(Exception):
    """Base Busyness logic Error
    """
    messages: list[str]

    def __init__(self, messages: list[str] = 'Bugal base error'):
        self.messages = messages


class NoInputTypeSet(BaseBugalModelError):
    """Input type is required for correct processing of the input
    """


class NoValidTransactionData(BaseBugalModelError):
    """ Raised if not valid transaction data were provided
    """


class NoValidHistoryData(BaseBugalModelError):
    """ Raised if not valid history data were provided
    """


class ImportDuplicateTransaction(BaseBugalModelError):
    """ Raised if duplicate transaction data were provided
    """


class ImportDuplicateHistory(BaseBugalModelError):
    """ Raised if duplicate history data were provided
    """


class NoValidInputFilesFound(BaseBugalModelError):
    """ Raised if not valid transaction data file was found
    """


class DbConnectionFaild(Exception):
    """ Raised if connection to DB is failing
    """


class ImportFileDuplicate(Exception):
    """ Raised if the file was already imported
    """


class ModelStackError(BaseBugalModelError):
    """ Raised if stack produce an error
    """


class NoCsvFilesFound(Exception):
    """Exception if in given folder no CSV files could be found"""


class DouplicateCsvFile(Exception):
    """Exception if user try to import the same csv file twice"""
