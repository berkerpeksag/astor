testenv:
	pip install -e .

release:
	python setup.py sdist upload -r pypi

register:
	python setup.py sdist register -r pypi

# Test it via `pip install -i https://testpypi.python.org/pypi <project_name>`
test-release:
	python setup.py sdist upload -r test

test-register:
	python setup.py sdist register -r test

clean:
	find . -name "*.pyc" -exec rm {} \;
	rm -rf *.egg-info
	rm -rf build/ dist/
	rm MANIFEST

.PHONY: clean register release
