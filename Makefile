SOURCE = src

VENV = .venv
BIN_DIR = $(VENV)/bin

venv:
	python3.10 -m venv $(VENV)
	$(BIN_DIR)/python -m pip install --upgrade pip
	$(BIN_DIR)/python -m pip install poetry~=1.7.1
	$(BIN_DIR)/python -m poetry install

format:
	@echo "Formatting isort" && $(BIN_DIR)/isort $(SOURCE)
	@echo "Formatting black" && $(BIN_DIR)/black . --config pyproject.toml $(SOURCE)
	@echo "Formatting autoflake" && $(BIN_DIR)/autoflake --recursive --in-place --remove-all-unused-imports --ignore-init-module-imports $(SOURCE)
	@echo "Formatting unify" && $(BIN_DIR)/unify --in-place --recursive --quote '"' $(SOURCE)

lint:
	@echo "Linting isort" && $(BIN_DIR)/isort --jobs 4 --check --diff $(SOURCE)
	@echo "Linting flake8" && $(BIN_DIR)/flake8 --jobs 4 --statistics --show-source --config setup.cfg $(SOURCE)
	@echo "Linting black" && $(BIN_DIR)/black --workers 4 --check --config pyproject.toml $(SOURCE)
	@echo "Linting mypy" && $(BIN_DIR)/mypy --cache-dir=/dev/null --config-file=setup.cfg $(SOURCE)

mypy:
	$(BIN_DIR)/mypy --cache-dir=/dev/null --config-file=setup.cfg $(SOURCE)
