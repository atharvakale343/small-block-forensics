:i count 14
:b shell 59
# Run SBF on a known content directory and target directory
:i returncode 0
:b stdout 0

:b stderr 0

:b shell 227
python cmd_interface.py gen_hash_and_hash_random --output_sql ./examples/out/known_content_hashes.sqlite --target_directory ./examples/target_folder --known_content_directory ./examples/known_dataset --block_size 4 | head -n -2
:i returncode 0
:b stdout 297

INFO: Successfully processed examples/known_dataset
INFO: Stored hashes at examples/out/known_content_hashes.sqlite

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

:b shell 161
python cmd_interface.py generate_hashes --output_sql ./examples/out/known_content_hashes.sqlite --known_content_directory ./examples/known_dataset --block_size 4
:i returncode 0
:b stdout 118

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

:b shell 169
python cmd_interface.py hash_random_blocks --input_sql ./examples/out/known_content_hashes.sqlite --target_directory ./examples/target_folder --block_size 4 | head -n -2
:i returncode 0
:b stdout 181


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

:b shell 20
# Server-client test
:i returncode 0
:b stdout 0

:b stderr 0

:b shell 72
(NOCAPTURE) hap run --check python -m small_blk_forensics.backend.server
:i returncode 0
:b stdout 0

:b stderr 0

:b shell 35
sleep 3 && python client_example.py
:i returncode 0
:b stdout 591
INFO: Received a response
[{'result': {'found': True, 'target_file': '/Users/atharvakale/workspace/umass/596e-cs/individual-project/small-block-forensics/examples/target_folder/sample.txt', 'known_dataset_file': '/Users/atharvakale/workspace/umass/596e-cs/individual-project/small-block-forensics/examples/known_dataset/sample.txt', 'block_num_in_known_dataset': 0, 'block_num_in_target': 1}, 'text': 'RESULTS'}, {'result': '/Users/atharvakale/workspace/umass/596e-cs/individual-project/small-block-forensics/examples/out/known_content_hashes.sqlite', 'text': 'Successfully stored hashes'}]

:b stderr 0

:b shell 14
hap kill --all
:i returncode 0
:b stdout 26
💀 Killed 1 active haps

:b stderr 0

:b shell 12
hap cleanall
:i returncode 0
:b stdout 29
🧲 Deleted 1 finished haps

:b stderr 0

