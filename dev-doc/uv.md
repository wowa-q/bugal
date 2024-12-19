# UV Python package manager

[UV](https://docs.astral.sh/uv/)

- uv can be used to install Python
- uv can create virtual environments
- uv can create Python packages
- uv replaces all other tools from Python eco system (PIP, pyenv etc.)
- uv compatible to PIP (`uv pip install`)
- uv resolve the dependencies of the installed packages

> Python doesn't support multiversion packages (no two versions of the same package)

## Lifecycle

1. Discover Python interpreter
2. Discover first-party (user) requirements
3. Resolve requirements into locked dependency graph
4. Generate an install plan
5. Install upgrade

### Workflow
1. `uv init --python 3.12 projectname` - creates a new project, with specified Python version. Python version specification is optional
    Set of file in a new folder will be created:
    - pyproject.toml: 
    - .gitignore:
    - .python-version
    - README.md
    - hello.py
2. `uv add packagename` - adds new packages to the project. If first time executed the new uv.lock file will be created and automatically virtual environment will be created. uv will execute the code automatically from this virtual environment. The pyproject.toml will be automatically updated.

3. `uv synch` - will update the project environment according to pyproject.toml **and will create .venv if it doesn't exists**

4. `uv add packagename --dev` - adds packages, which are needed only for development and won't be packed into delivery package
    `uv add --group lint ruff` - adds package to a dependency group

5. `uv remove packagename` - to remove package from dependency tree

6. `uv tree` - shows the dependency tree

### Commands

- `uv python list` to checkout the Python version
- `uv python install` installs Python
- `uv run xyz` runs the script
- `uv init --name NAME` creates a new project
- `uv add packagename` adds a package to the project dependency
- `uv remove packagename` removes the packages from the project
- `uv tool install toolname` tool can be installed to be used from command line