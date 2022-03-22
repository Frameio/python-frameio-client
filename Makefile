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
	cd tests && poetry run python test_integration.py

package:
	poetry build

publish:
	poetry publish

build-docker:
	docker build . -t benchmark

run-benchmark:
	docker run -it -e $1 benchmark

format:
	black frameioclient

view-docs:
	cd docs && poetry run make dev

publish-docs:
	cd docs && poetry run make jekyll
