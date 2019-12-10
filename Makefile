testenv:
	pip install -e .

create-sdist:
	python setup.py sdist bdist_wheel

release: create-sdist
	twine upload dist/*

# Test it via `pip install -i https://test.pypi.org/simple/ <project_name>`
test-release: create-sdist
	twine upload -r test dist/*

clean:
	find . -name "*.pyc" -exec rm {} \;
	rm -rf *.egg-info
	rm -rf build/ dist/ __pycache__/

.PHONY: clean release test-release create-sdist
