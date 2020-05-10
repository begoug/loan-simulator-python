default: all
all:build install_user

.PHONY:build
build:
	cd src && python setup.py bdist_wheel

install_user:
	cd src && pip install --user --upgrade dist/*.whl && cp dist/* versions && rm -f dist/*
