SRC = $(wildcard *.py) $(shell find small_blk_forensics/ -type f -name '*.py')

format:
	black --line-length 110 $(SRC)
	isort --profile black $(SRC)
	flake8 --max-line-length=110 --ignore=E203,W503 --select=F,N $(SRC)
	mypy $(SRC)

test-record:
	python test/rere.py record test/test.list

test-replay:
	python test/rere.py replay test/test.list
