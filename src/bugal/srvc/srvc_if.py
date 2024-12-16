"""Abstraction layer
"""
import abc

class Command(abc.ABC):
    ''' abstract class to alighn different commands '''
    __metaclass__ = abc.ABCMeta

    # to run standard commands
    @abc.abstractmethod
    def execute(self) -> None:
        ''' interface API '''
        raise NotImplementedError
