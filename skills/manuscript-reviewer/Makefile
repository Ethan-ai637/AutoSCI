.PHONY: validate dist

validate:
	python scripts/validate_release.py

dist: validate
	python scripts/build_release.py
