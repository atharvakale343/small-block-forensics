:i count 5
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

