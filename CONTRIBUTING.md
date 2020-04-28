# Contribution Guidelines

Thank you very much for you interest in contributing in this project!


## Set up the development environment

  * Clone the project (or even better: fork it on GitLab and clone your fork) to your local file system and `cd` into it
  * Set up a python virtual environment and install the package in editable mode:
    ```
    virtualenv -p python3.8 venv
    pip install -e .
    ```
   * For every time you start developing or you open a new shell, load the virtual python environment:
     ```bash
     . ./venv/bin/activate
     ```

That's it! Happy coding!

## Code Contributions

Before you submit your code, please make sure that the code will pass the tests:

  * Unittests (using the built-in `unittest` package):
    ```
    python -m unittest discover tests
    ```
  * flake8 code style checks (install with `pip install flake8`):
    ```
    python -m flake8
    ```
  * Type checks (using `mypy`, install with `pip install mypy`):
    ```
    python -m mypy -p bdtsim
    ```

## Documentation Contributions

Documentation is located in the `docs/` directory and will be converted to HTML pages using `mkdocs`
(execute `pip install mkdocs` for installing the `mkdocs` package).

To work on the documentation and to check the results locally, `mkdocs` provides an integrated webserver.
Use the following command in the project root (not in `docs/`) to start the documentation development webserver:
```
mkdocs serve
```
Now the documentation should be served on http://127.0.0.1:8000.
