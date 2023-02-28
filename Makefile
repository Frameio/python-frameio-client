#!/bin/sh

install-dev:
	pip3 install -e .[dev]
	curl -fLSs https://raw.githubusercontent.com/CircleCI-Public/circleci-cli/master/install.sh | bash

bump-minor:
	bump2version minor

bump-major:
	bump2version major

bump-patch:
	bump2version patch

clean:
	find . -name "*.pyc" -exec rm -f {} \;

test:
	cd tests && pipenv run python integration.py

package:
	pipenv run python3 setup.py sdist bdist_wheel

build-docker:
	docker build . -t benchmark

run-benchmark:
	docker run -it -e $1 benchmark

format:
	black frameioclient

view-docs:
	cd docs && pip install -r requirements.txt && make dev

publish-docs:
	cd docs && pip install -r requirements.txt && make jekyll && make publish
