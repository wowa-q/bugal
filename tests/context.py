# pylint: skip-file
import os
import sys

# insearts the parent folder to the pythonpath
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# # now the bugal package can be imported and provided to all modules within this folder
# import bugal


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.insert(0, parent_dir)

# print(parent_dir)

import bugal
import bugal.cfg
import bugal.app
import bugal.srvc

if __name__ == "__main__":
    print(parent_dir)