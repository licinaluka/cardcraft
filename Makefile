#!make

.PHONY: default pre-commit

default:
	echo 0

pre-commit:
	cp pre-commit .git/hooks/pre-commit
