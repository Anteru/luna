from setuptools import setup, find_packages

setup(
    name = "Luna",
    version = "0.1.0",
    packages = find_packages (exclude='test'),
	test_suite = 'test',

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = ['cairocffi>=0.5', 'svgwrite>=1.0'],

    # metadata for upload to PyPI
    author = "Matthäus G. Chajdas",
    author_email = "dev@anteru.net",
    description = "2D drawing library",
    license = "BSD",
    keywords = [],
    url = "http://shelter13.net/projects/Luna",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)
