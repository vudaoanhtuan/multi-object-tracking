VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: venv install run lint clean

venv:
	python3.11 -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m mot_va

lint:
	$(VENV)/bin/ruff check mot_va/

clean:
	rm -rf $(VENV)
	find . -name '__pycache__' -exec rm -rf {} +
