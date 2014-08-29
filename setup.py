from setuptools import setup, find_packages
import sys
from setuptools.command.test import test as TestCommand

import luna

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)

setup(
    name = "Luna",
    version = luna.__version__,
    packages = find_packages (exclude=['*.test', 'test.*', '*.test.*']),

    test_suite = 'luna.test',
    tests_require=['tox'],
    cmdclass = {'test' : Tox},

    install_requires = ['cairocffi>=0.5.4', 'svgwrite>=1.1.6'],

    author = "Matthäus G. Chajdas",
    author_email = "dev@anteru.net",
    description = "2D drawing library",
    license = "BSD",
    keywords = [],
    url = "http://shelter13.net/projects/Luna",

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Topic :: Multimedia :: Graphics',

    ]
)
