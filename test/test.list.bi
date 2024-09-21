:i count 8
:b shell 59
# Run SBF on a known content directory and target directory
:i returncode 0
:b stdout 0

:b stderr 0

:b shell 218
python cmd_interface.py gen_hash_random --output_sql ./examples/out/known_content_hashes.sqlite --target_directory ./examples/target_folder --known_content_directory ./examples/known_dataset --block_size 4 | head -n -2
:i returncode 0
:b stdout 457

INFO: Hashing all files in examples/known_dataset
INFO: Successfully processed examples/known_dataset
INFO: Stored hashes at examples/out/known_content_hashes.sqlite

INFO: Hashing random blocks from examples/target_folder
INFO: examples/target_folder has a total of 2 blocks

Results:
	Match: Yes
	Target Probability: 0.95
	Block Size: 4
	Matched Target File: examples/target_folder/sample.txt
	Match Known Dataset File: examples/known_dataset/sample.txt

:b stderr 0

:b shell 0

:i returncode 0
:b stdout 0

:b stderr 0

:b shell 82
# Generate a SQLite DB contains hashes of all the blocks within a source directory
:i returncode 0
:b stdout 0

:b stderr 0

:b shell 154
python cmd_interface.py gen_hash --output_sql ./examples/out/known_content_hashes.sqlite --known_content_directory ./examples/known_dataset --block_size 4
:i returncode 0
:b stdout 168

INFO: Hashing all files in examples/known_dataset
INFO: Successfully processed examples/known_dataset
INFO: Stored hashes at examples/out/known_content_hashes.sqlite


:b stderr 0

:b shell 0

:i returncode 0
:b stdout 0

:b stderr 0

:b shell 83
# Run SBF on a pre-generated known content directory SQLite DB and target directory
:i returncode 0
:b stdout 0

:b stderr 0

:b shell 162
python cmd_interface.py hash_random --input_sql ./examples/out/known_content_hashes.sqlite --target_directory ./examples/target_folder --block_size 4 | head -n -2
:i returncode 0
:b stdout 290

INFO: Hashing random blocks from examples/target_folder
INFO: examples/target_folder has a total of 2 blocks

Results:
	Match: Yes
	Target Probability: 0.95
	Block Size: 4
	Matched Target File: examples/target_folder/sample.txt
	Match Known Dataset File: examples/known_dataset/sample.txt

:b stderr 0

