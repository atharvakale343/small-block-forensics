## Small Block Forensics

In [small block forensics](https://gist.github.com/atharvakale343/614a721b9ae429d1dce8ee14dd3bed52), the goal is to determine the existence of any content from  a small dataset of known content in a large target drive.

This project is an approximation of the SBF technique that takes two directories as input (target directory, known content directory), and uses the small block randomized technique to find the existence of some file from the known content directory within the target directory. For a visual intro to small block forensics, see this [PDF deck](./docs/intro-to-small-block-forensics.pdf).

View a video explanation of the project here: [demo.mp4](./docs/small-block-forensics-demo.mp4)

## Supported Tasks

This application supports the three tasks:

### Generate SQLite DB of Hashes

This task generates a SQLite DB of hashes of all the blocks within a source directory.

#### Inputs
1. **Known Content Directory:** A directory containing the files/folders of known content.
2. **Output SQL Path:** The path to save the SQLite table for known_content.

#### Parameters
1. **Block Size:** The block size in bytes to be used for hashing. Defaults to 4096.

### Hash Random Blocks of a Target Directory

This task hashes the blocks of a target directory and compares them with the hashes contained in an SQLite database.

#### Inputs
1. **Target Directory:** The directory containing files/folders of the content to analyze.
2. **Input SQL:** The path to the existing SQLite DB containing hashes of known content.

#### Parameters
1. **Block Size:** The block size in bytes to be used for hashing. Defaults to 4096.
2. **Target Probability:** The target probability to achieve. Higher means more of the target drive will be scanned. Defaults to 0.95.

### Hash Blocks of Known Content and Find Existence in Target Directory

This task hashes the blocks of known content and compares them with the hashes generated from the target directory.

#### Inputs
1. **Target Directory:** The directory containing files/folders of the content to analyze.
2. **Known Content Directory:** The directory containing the files/folders of known content.
3. **Output SQL Path:** The path to save the SQLite hashesh for known content.

#### Parameters
1. **Block Size:** The block size in bytes to be used for hashing. Defaults to 4096.
2. **Target Probability:** The target probability to achieve. Higher means more of the target drive will be scanned. Defaults to 0.95.

## Constraints
- **Runtime:** Because of the experimental nature of this project, the runtime is not guaranteed. Please make a backup of your data before running this application.

# Running the application

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
