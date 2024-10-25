:i count 8
:b shell 59
# Run SBF on a known content directory and target directory
:i returncode 0
:b stdout 0

:b stderr 0

:b shell 231
python cmd_interface.py gen_hash_random --output_sql ./examples/out/known_content_hashes.sqlite --target_directory ./examples/target_directory --known_content_directory ./examples/known_content_directory --block_size 4 | head -n -2
:i returncode 0
:b stdout 822
INFO: Hashing all files in examples/known_content_directory
INFO: Successfully processed examples/known_content_directory
INFO: Stored hashes at examples/out/known_content_hashes.sqlite

INFO: Hashing random blocks from examples/target_directory
INFO: examples/target_directory has a total of 2 blocks
	Results:
	Small Block Forensics

	## Results
	
	- Found: True
	- Target File: examples/target_directory/sample.txt
	- Block Number in Target File: 1
	- Known Dataset File: examples/known_content_directory/sample.txt
	- Block Number in Known Dataset File: 1
	


	Results:
	Small Block Forensics

	## Results
	
	- Found: True
	- Target File: examples/target_directory/sample.txt
	- Block Number in Target File: 1
	- Known Dataset File: examples/known_content_directory/sample.txt
	- Block Number in Known Dataset File: 1

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

:b shell 164
python cmd_interface.py gen_hash --output_sql ./examples/out/known_content_hashes.sqlite --known_content_directory ./examples/known_content_directory --block_size 4
:i returncode 0
:b stdout 453
INFO: Hashing all files in examples/known_content_directory
INFO: Successfully processed examples/known_content_directory
INFO: Stored hashes at examples/out/known_content_hashes.sqlite
	Results:
	Small Block Forensics

	## Results
	
	- Successfully generated SQLite DB at ./examples/out/known_content_hashes.sqlite
	


	Results:
	Small Block Forensics

	## Results
	
	- Successfully generated SQLite DB at ./examples/out/known_content_hashes.sqlite
	


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

:b shell 165
python cmd_interface.py hash_random --input_sql ./examples/out/known_content_hashes.sqlite --target_directory ./examples/target_directory --block_size 4 | head -n -2
:i returncode 0
:b stdout 635
INFO: Hashing random blocks from examples/target_directory
INFO: examples/target_directory has a total of 2 blocks
	Results:
	Small Block Forensics

	## Results
	
	- Found: True
	- Target File: examples/target_directory/sample.txt
	- Block Number in Target File: 1
	- Known Dataset File: examples/known_content_directory/sample.txt
	- Block Number in Known Dataset File: 1
	


	Results:
	Small Block Forensics

	## Results
	
	- Found: True
	- Target File: examples/target_directory/sample.txt
	- Block Number in Target File: 1
	- Known Dataset File: examples/known_content_directory/sample.txt
	- Block Number in Known Dataset File: 1

:b stderr 0

