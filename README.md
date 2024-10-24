## Small Block Forensics

In [small block forensics](https://gist.github.com/atharvakale343/614a721b9ae429d1dce8ee14dd3bed52), the goal is to determine the existence of any content from  a small dataset of known content in a large target drive.

This project is an approximation of the SBF technique that takes two directories as input (target directory, known content directory), and uses the small block randomized technique to find the existence of some file from the known content directory within the target directory. For a visual intro to small block forensics, see this [PDF deck](./docs/intro-to-small-block-forensics.pdf).

View a video explanation of the project here: [demo.mp4](./docs/small-block-forensics-demo.mp4)

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

Pre-requisite: start the server in the background.

```zsh
python client_example.py
```

### Command line tool

Run SBF on a known content directory and target directory

```zsh
python cmd_interface.py gen_hash_random \
    --output_sql ./examples/out/known_content_hashes.sqlite \
    --target_directory ./examples/target_directory \
    --known_content_directory ./examples/known_content_directory \
    --block_size 4
```

Generate a SQLite DB contains hashes of all the blocks within a source directory

```zsh
python cmd_interface.py gen_hash \
    --output_sql ./examples/out/known_content_hashes.sqlite \
    --known_content_directory ./examples/known_content_directory \
    --block_size 4
```


Run SBF on a pre-generated known content directory SQLite DB and target directory

```zsh
python cmd_interface.py hash_random \
    --input_sql ./examples/out/known_content_hashes.sqlite \
    --target_directory ./examples/target_directory \
    --block_size 4
```

### Developing SBF

Running black, isort, flake8 and mypy:

```zsh
pipenv install --dev
make format
```
