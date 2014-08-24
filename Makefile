TEST_SETTINGS_FILE=$(abspath settings_test.py)

# Silent: Don't output commands for those targets
.SILENT: clean tests
# Phony Build targets even in file or folder exist in the filesystem
.PHONY: clean tests

all: test

clean:
	find . -name '*.pyc' -delete
	rm -rf *.egg-info

tests:
	APP_SETTINGS=${TEST_SETTINGS_FILE} python setup.py test
