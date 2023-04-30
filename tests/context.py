# pylint: skip-file
import os
import sys

# insearts the parent folder to the pythonpath
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# now the bugal package can be imported and provided to all modules within this folder
import bugal