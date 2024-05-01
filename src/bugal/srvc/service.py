"""Service layer
Service Layer: It takes care of orchestrating our workflows 
and defining the use cases of our system. It contains a sublayer 
and pattern called a Unit of Work that oversees the abstract of our 
idea of atomic operations.
"""
import pathlib

from bugal.cfg import config as cfg
from bugal.app import model as dom
from bugal.libs.abstract import HandlerReadIF, HandlerWriteIF, AbstractRepository 

def import_data(cfg_):
    if parse_cfg(cfg_)[0]:
        return 'Import successful'
    else:
        return f'configuration is invalid: {cfg_} \n' +  parse_cfg(cfg_)[1]
    
def parse_cfg(cfg_):
    pth = cfg_.path_
    csv_type = cfg_.import_type
    try:
        if pth.is_file():
            pth = pathlib.Path(cfg_.path_)
            csv_type = cfg_.import_type
            return (pth, csv_type)    
    except AttributeError as error:
        # logger.exception("datum provided with false format: %s", datum)
        # raise AttributeError(f"path provided with false format: {pth}") from error
        return (False, f' Can not to parse the file path {error}')