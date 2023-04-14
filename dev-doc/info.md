
# Project setup

For Mark Down rules, check [here](https://github.com/DavidAnson/markdownlint/tree/v0.27.0/doc)

## Setup VS Code

1. install the extension packages for VSCode:
   1. *franneck94*:
      1. **Coding Tools Extension Pack**: independent from the programming language
      2. **Python Dev Extension Pack**: tools for development with Paython
         1. python docstring generator: to generate the doc strings
2. Generate Python Config Files
   1. 'strg'+'shift'+'p'
   2. Python Config: Generate Python Config Files: will generate some cofiguration and setting files
3. Select the Python interpreter
4. *Terminal: Create new Terminal* and select the virtual environment
5. setup docstring:
   1. open settings by *str+*
   2. go to extensions/Python Docstring Generator config
   3. set the Docstring formate to numpy, google or sphinx - google is prefered

## Setup project environment

1. Create virtual environment
2. swith to the virtual environment
3. Install the packages by: `pip install -r requirements.txt`

## Development Tools

### PYLINT [pylint](https://pylint.pycqa.org/en/latest/user_guide/usage/run.html)

pylint scans the code about potential issues or error that might occur. It check also some PEP8 rules. => checking the coding style

`pylint file.py` run in the terminal the results will be printed into the terminal.
`pylint folder` to run pylint over the whole folder

#### PYLINT configuration file

generate the configuration file by `pylint --generate-rcfile > .pylintrc`
will genrate the ***.pylintrc*** file, which is configuring the pylint for the whole project.

Instead of the ***.pylintrc*** file, which is only for the pylint the ***setup.cfg*** can be used.

### FLAKE8 [flake8](https://flake8.pycqa.org/en/latest/)

flake8 is checking the PEP8 rules.

`flake8 file.py` run in the terminal the results will be printed into the terminal, similar to the pylint.

.flake8 configuration file can be created, or setup.cfg

### AUTOPEP8 [autopep8](https://github.com/peter-evans/autopep8)

The tool is formating the code according to PEP8. It uses the flake8 configuration file.

`autopep8 --in-place file.py` will update the source file. `autopep8 file.py --diff` will just show what will be modified in the file, but not change it.

### MYPY [mypy](https://mypy.readthedocs.io/en/stable/)

The tool is checking the types e.g.: `def fun(var: str) -> str`
With `mypy file.py` the results will be printed in the terminal e.g. inconsistoncies in the types.
`from typing import Iterable`

## Testing Tools

### PYTEST [pytest](https://pytest.org/en/latest/contents.html)

Unit test framework

To run the tests `pytest test_file.py`

#### Use Cases

1. parametrize the test - the test will be executed 3 times

```python
V1 = Vector2D(0, 0)
V2 = Vector2D(-1, 1)
V3 = Vector2D(2.5, -2.5)

@pytest.mark.parametrize(
    ('lhs', 'rhs', 'exp_res'),
    (
        (V1, V2, Vector2D(-1, 1)),
        (V1, V3, Vector2D(2.5, -2.5)),
        (V3, V2, Vector2D(1.5, -1.5)),
    )
)

def test_add(lhs: Vector2D, rhs: Vector2D, exp_res: Vector2D) -> None:
    assert lhs + rhs == exp_res
```

1. skip the test: `@pytest.mark.skip(reason="not implemented")`
2. Test the function under test can raise an exception correctly

```python
@pytest.mark.parametrize(
    ('x', 'y'),
    (
        (None, -1),
        (0, None),
    )
)
def test_raises(x: Any, y: Any) -> None:
    with pytest.raises(TypeError):
        _ = Vector2D(x, y)
```

### VS Code Debugger

The debugger is configured to run the debugger on the current open file (see first configuration). In `launch.json` file from *.vscode* folder it can be configured to always start from the main file. (see second configuration).

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debug: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ]
}

{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debug: Current File",
            "type": "python",
            "request": "launch",
            "program": "${workspacefolder}/dkb/api.py",
            "console": "integratedTerminal"
        }
    ]
}

```

### Timing

The library from Python [timeit](https://docs.python.org/3/library/timeit.html) can measure the runtime of the application. Therefore a python module needs to be created to measure the run time. The first measurement is slowlier, because the timeit first does the import of the code.

### Profiling

For measurement of how long any function runs the `@profiling` decorator needs to be created and used in the code. First a module shall be created to use the `cProfile` from standard Python library. The module implementation can be taken from internet. **SnakeViz** can be used for visualization of the profiling results.

Another profiling tool can be used is **pyinstrument**, which needs to be installed and is easier to use. example:

```python
from pyinstrument import Profiler

def main() -> None:
    profiler = Profiler()
    profiler.start()
    # some user code which needs to run
    profiler.stop()
    profiler.print()
if __name__ == "__main__":
    main()

```

## Packaging

`__init__.py` is the main file of a python package. It needs to exist to be able to import the package. `__init__.py` needs to exist in every subfolder which needs to be imported.

### Verioning

In the `__init__.py` the package verion will be defined like this:

```python
__major_version__ = "0" # breaking change
__minor_version__ = "1" # new feature without breaking
__patch_version__ = "0" # bugfixes

__version__ = f"{__major_version__}.{__minor_version__}.{__patch_version__}"
```

## Documentation

### MKDOCS [mkdocs](https://www.mkdocs.org/)

to setup the tool:

- `pip install mkdocs`

To generate the documentation from the docstrings from code. [mkdocstrings](https://mkdocstrings.github.io/)

- `pip install "mkdocstrings[python]"`

The last is the theme [mkdocs-material-theme](https://github.com/squidfunk/mkdocs-material).

- `pip install mkdocs-material`

Tool to generate documentation from the source code. To configure the project: `mkdocs new .` will genrate docs folder with index.md inside. and mkdocs.yml file for configuration.

#### Configuration of mkdocs

in mkdocs.yml

```yml
# document name
site_name: My Doc

# setting up the theme for documentation
theme:
  name: "material"

# to generate documentation from docstrings from code
plugins:
  - mkdocstrings
  
# include new chapter / md files
nav:
  - index.md
  - tutorials.md
  - how-to-guides.md
  - reference.md
  - explanation.md
```

This is how the subpages can be added in index.md file:

```md
1. [Tutorials](tutorials.md)
2. [How-To Guides](how-to-guides.md)
3. [Reference](reference.md)
4. [Explanation](explanation.md)
```

To use the docstrings in documentation: `::: udentifier`

```md
::: spec_handler.handler
```

spec_handler: folder with `__init__.py`
handler: is the handler.py within the spec_handöer folder.

- to build the documentation as html file: `mkdocs build`
- to generate the documentation and to show it on a local host: `mkdocs serve`

----------------------------------------------------------------

# Libraries

## Directory

- [pathlib](https://docs.python.org/3/library/pathlib.html )
- [import error: ModuleNotFound](https://towardsdatascience.com/how-to-fix-modulenotfounderror-and-importerror-248ce5b69b1c)

## DB

- [sqlite3-tutorial](https://www.sqlitetutorial.net/)
- [pandas-docu](https://pandas.pydata.org/pandas-docs/stable/reference/frame.html)
- [pandas-csv](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_csv.html)
- [pandas-sqlite3-fullstack](https://www.fullstackpython.com/blog/export-pandas-dataframes-sqlite-sqlalchemy.html)
- [pandas-sqlite3](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html)
- [sqllite browser](https://sqlitebrowser.org/about/)
- [ORM: SQL Alchemy](https://www.sqlalchemy.org/)
- [SQLAlchemy tutotial](https://docs.sqlalchemy.org/en/13/core/tutorial.html)

get the table related by a foreign key

- `employees`: table name
- `employee_dept`: column Foreign Kex

`list(employees.columns.employee_dept.foreign_keys)[0].column.table`

get the "key" of a column, which defaults to its name, but can be any user-defined string:
`employees.columns.employee_name.key`

## Pandas Excel

- [pandas-excel](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#excel-files)
- [convert to excel](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_excel.html#pandas.DataFrame.to_excel)

  ```python
  DataFrame.to_excel(excel_writer, sheet_name='Sheet1', na_rep='', float_format=None, columns=None, header=True, index=True, index_label=None, startrow=0, startcol=0, engine=None, merge_cells=True, encoding=None, inf_rep='inf', verbose=True, freeze_panes=None, storage_options=None)
  ```

>`freeze_panes`: tuple of int (length 2), optional
Specifies the one-based bottommost row and rightmost column that is to be frozen.

If you wish to write to more than one sheet in the workbook, it is necessary to specify an ExcelWriter object:

```python
df2 = df1.copy()
with pd.ExcelWriter('output.xlsx') as writer:  
    df1.to_excel(writer, sheet_name='Sheet_name_1')
    df2.to_excel(writer, sheet_name='Sheet_name_2')
```

## Excel libs

### xlwings

[xlwings quickstart](https://docs.xlwings.org/en/stable/quickstart.html)
[xlwings API](https://docs.xlwings.org/en/stable/api.html)

#### in nutshell

```python
import xlwings as xw

wb = xw.Book()  # opens a new workbook
wb = xw.Book("FileName.xlsx") # connect to a file
wb = xw.Book(r'C:\path\to\file.xlsx') # with the full path
sheet = wb.sheets['sheet name']
sheet.range("A1")
sheet.range("A1:C3")
sheet.range((1,1))
sheet.range((1,1), (3,3))
sheet.range("NamedRange")
# Or using index/slice notation
sheet["A1"]
sheet["A1:C3"]
sheet[0, 0]
sheet[0:4, 0:4]
sheet["NamedRange"]
```

## openpyxl

[openpyxl](https://openpyxl.readthedocs.io/en/stable/)

```python
from openpyxl import Workbook
wb = Workbook()
```

grab the active worksheet

```python
ws = wb.active
```

Data can be assigned directly to cells

```python
ws['A1'] = 42
```

Rows can also be appended

```python
ws.append([1, 2, 3])
```

Python types will automatically be converted

```python
import datetime

ws['A2'] = datetime.datetime.now()
```

Save the file

```python
wb.save("sample.xlsx")
```
