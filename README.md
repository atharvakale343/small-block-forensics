## Small Block Forensics

An approximation of the [small block forensics technique](https://gist.github.com/atharvakale343/614a721b9ae429d1dce8ee14dd3bed52) that takes two directories as input (target directory, known content directory), and uses the small block randomized technique to find the existence of some file from the known content directory within the target directory.

### Installing requirements

1. Install pipenv

```zsh
pip install pipenv
```

2. Activate the venv

```zsh
pipenv shell
```

3. Install dependencies

```zsh
pipenv install
```

### Starting the server

```zsh
python -m small_blk_forensics.backend.server
```

### Client example

```zsh
python client_example.py
```

### Command line tool

Run SBF on a known content directory and target directory

```zsh
python cmd_interface.py --output_directory ./examples/out --target_directory ./examples/target_folder --known_content_directory ./examples/known_dataset
```

Run SBF on a pre-generated known content directory SQLite DB and target directory

```zsh
python cmd_interface.py --output_directory ./examples/out --target_directory ./examples/target_folder --existing_known_content_db ./examples/known_dataset.sqlite3
```

### Developing SBF

Running black, isort, flake8 and mypy:

```zsh
make format
```
