EXAMPLES_SRC=$(wildcard examples/*.py)
EXAMPLES_TXT=$(patsubst examples/%.py,output/%.txt,${EXAMPLES_SRC})

SCENARIOS_SRC=$(wildcard scenarios/*.py)
SCENARIOS_TMP=$(patsubst scenarios/%.py,tmp/%.html,${SCENARIOS_SRC})

.PRECIOUS: ${SCENARIOS_TMP}

.PHONY: docs
all: commands

## commands: show available commands (*)
commands:
	@grep -h -E '^##' ${MAKEFILE_LIST} \
	| sed -e 's/## //g' \
	| column -t -s ':'

## benchmark: run benchmark for N=10000
benchmark:
	python benchmark/benchmark.py 10000

## build: build package
build:
	python -m build

## check: check code issues
check:
	@ruff check .

## clean: clean up
clean:
	@rm -rf ./dist ./tmp
	@find . -path './.venv' -prune -o -type d -name '__pycache__' -exec rm -rf {} +
	@find . -path './.venv' -prune -o -type f -name '*~' -exec rm {} +

## coverage: run tests with coverage
coverage:
	@python -m coverage run -m pytest tests
	@python -m coverage report --show-missing

## docs: build documentation
docs: ${SCENARIOS_TMP}
	@mkdocs build
	@touch docs/.nojekyll
	@cp docs-requirements.txt docs/requirements.txt
	@cp -r tmp docs/notebooks

## fix: fix code issues
fix:
	ruff check --fix .

## format: format code
format:
	ruff format .

## lint: run all code checks
lint:
	@make check
	@make types

## examples: regenerate example output
examples: ${EXAMPLES_TXT}

output/%.txt: examples/%.py
	@mkdir -p output
	python $< > $@ 2>&1

## publish: publish using ~/.pypirc credentials
publish:
	twine upload --verbose dist/*

## scenarios: regenerate scenario output
scenarios: ${SCENARIOS_HTML}

tmp/%.html: scenarios/%.py
	@mkdir -p tmp
	uv run marimo export html-wasm --force --sandbox --mode edit $< -o $@

## serve: serve documentation
serve:
	python -m http.server -d docs

## test: run tests
test:
	pytest tests

## types: check types
types:
	ty check src tests
