PYZ     := dist/habits
STAGING := build/staging
PREFIX  ?= $(HOME)/.local
SOURCES := $(shell find src/habits -name '*.py')

build: $(PYZ)

$(PYZ): $(SOURCES)
	rm -rf $(STAGING)
	mkdir -p $(STAGING) dist
	cp -r src/habits $(STAGING)/
	pip install --target $(STAGING) --no-compile tomlkit
	python -m zipapp $(STAGING) -o $(PYZ) -m "habits.__main__:main" -p '/usr/bin/env python3'

tags:
	ctags -R --languages=Python --fields=+l --extras=+q --python-kinds=-i src/

install: build
	install -Dm755 $(PYZ) $(PREFIX)/bin/habits

lint:
	mkdir -p build
	pylint --output build/lint.log src/habits

test: dist/habits
	./test/smoke.sh

clean:
	rm -rf dist build __pycache__ src/habits/__pycache__ tags

.PHONY: build install clean lint
