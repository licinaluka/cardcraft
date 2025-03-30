#!make

.PHONY: default


default:
	.venv/bin/pyinstaller -F main.py --hidden-import=_cffi_backend --hidden-import=cardcraft.apparatus.apparatus.settings -n cardcraft-web-amd64
