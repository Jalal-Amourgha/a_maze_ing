NAME		= a_maze_ing.py
CONFIG_FILE 	= config.txt
PY 		= python3
FLAGS 		= -m flake8
PIP		= pip


run:
	${PY} ${NAME} ${CONFIG_FILE}

install:
	${PIP} install build wheel flake8 mypy pillow

debug:
	${PY} -m pdb ${NAME}


clean:
	@rm -rf  __pycache__
	@rm -rf .mypy_cache
	@rm -rf *.png
	rm -rf */__pycache__


lint:
	python3 -m flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

