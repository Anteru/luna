from setuptools import setup, find_packages
import sys
from setuptools.command.test import test as TestCommand

import luna

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['--strict', 'luna']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    name = "Luna",
    version = luna.__version__,
    packages = find_packages (),

    test_suite = 'luna.test',
    tests_require=['pytest'],
    cmdclass = {'test' : PyTest},

    install_requires = ['cairocffi>=0.5.4', 'svgwrite>=1.1.6'],

    author = "Matthäus G. Chajdas",
    author_email = "dev@anteru.net",
    description = "2D drawing library",
    license = "BSD",
    keywords = [],
    url = "http://shelter13.net/projects/Luna",
    extras_require={
	'testing' : ['pytest']
    }
)
