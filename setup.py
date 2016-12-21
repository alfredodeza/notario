import re


module_file = open("notario/__init__.py").read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))
long_description = open('README.rst').read()

from setuptools import setup, find_packages

setup(
    name             = 'notario',
    description      = 'A dictionary validator',
    packages         = find_packages(),
    author           = 'Alfredo Deza',
    version          = metadata['version'],
    url              = 'http://github.com/alfredodeza/notario',
    license          = "MIT",
    zip_safe         = False,
    keywords         = "schema, validator, dictionary, enforce",
    long_description = long_description,
    classifiers      = [
                        'Development Status :: 4 - Beta',
                        'Intended Audience :: Developers',
                        'License :: OSI Approved :: MIT License',
                        'Topic :: Software Development :: Build Tools',
                        'Topic :: Software Development :: Libraries',
                        'Topic :: Software Development :: Testing',
                        'Topic :: Utilities',
                        'Operating System :: MacOS :: MacOS X',
                        'Operating System :: Microsoft :: Windows',
                        'Operating System :: POSIX',
                        'Programming Language :: Python :: 2.6',
                        'Programming Language :: Python :: 2.7',
                        'Programming Language :: Python :: 3.0',
                        'Programming Language :: Python :: 3.1',
                        'Programming Language :: Python :: 3.2',
                        'Programming Language :: Python :: Implementation :: PyPy'
                      ]
)
