#!/bin/sh

install-dev:
	pip3 install bump2version

bump-minor:
	bump2version minor

bump-major:
	bump2version major

bump-patch:
	bump2version patch