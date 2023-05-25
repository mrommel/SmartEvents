# define the name of the virtual environment directory
VENV := venv

PY_FILES := $(shell find . -name \*.py -not -path "./venv/*" -print)

# default target, when make executed without arguments
all: venv

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	./$(VENV)/bin/pip3 install -r requirements.txt

# venv is a shortcut target
venv: $(VENV)/bin/activate

# pylint: venv
	# --disable=C0303,R0903,R0915,C0103,E1101,E0102,R0913,W0123,R0912,R0801 simulation map population
#	./$(VENV)/bin/pylint

pytests: venv
	mkdir -p coverage
	./$(VENV)/bin/pytest tests/

run: venv
	./$(VENV)/bin/python3 main.py

l18n_prepare: $(PY_FILES)
	which xgettext || (echo "You have to install gettext (brew install gettext)" ; exit 1)
	find . -iname "*.py" | xargs xgettext -L Python -o locales/base.pot

l18n_extract:
	mkdir -p 'locales/en/LC_MESSAGES'
	[ -e 'locales/en/LC_MESSAGES/base.po' ] || msginit --no-translator -l en -i 'locales/base.pot' -o 'locales/en/LC_MESSAGES/base.po'
	msgmerge -N -U 'locales/en/LC_MESSAGES/base.po' 'locales/base.pot'

l18n_compile:
	msgfmt 'locales/en/LC_MESSAGES/base.po' -o 'locales/en/LC_MESSAGES/base.mo'

.PHONY: l18n_prepare l18n_extract l18n_compile