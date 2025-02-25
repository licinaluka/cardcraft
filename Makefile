#!make

.PHONY: default pre-commit sonar

default:
	echo 0

pre-commit:
	cp pre-commit .git/hooks/pre-commit

sonar:
	poetry run pysonar-scanner -Dsonar.login=${SONAR_TOKEN} -Dsonar.host.url=http://127.0.0.1:9009 -Dsonar.projectKey=cardcraft -Dsonar.sources=.
