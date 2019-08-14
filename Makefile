all:build install_user

.PHONY:build
build:
	python3.7 setup.py bdist_wheel

install_user:
	pip3.7 install --user --upgrade dist/*.whl
