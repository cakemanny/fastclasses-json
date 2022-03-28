PYTHON ?= python3

venv: requirements.txt requirements-test.txt
	$(PYTHON) -m venv venv
	touch -t 01010000 venv
	venv/bin/pip install --upgrade pip setuptools
	venv/bin/pip install --upgrade -r requirements-test.txt
	touch venv

test: venv
	venv/bin/pytest

lint: venv
	venv/bin/flake8 fastclasses_json

.PHONY: test.docker
test.docker:
	docker build . -f tests/Dockerfile.test -t fastclasses-json:tests
	docker run -it --rm fastclasses-json:tests

publish:
	venv/bin/pip install --upgrade twine build
	venv/bin/python -m build
	venv/bin/twine upload dist/*
	rm -Rf dist/ fastclasses_json.egg-info

.PHONY: clean
clean:
	rm -Rf dist/ fastclasses_json.egg-info
