import sys
import os
import re

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
LONG_DESCRIPTION = open(readme).read()

module_file = open("notario/__init__.py").read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))

from setuptools import setup

setup(
    name             = 'notario',
    description      = 'A dictionary validator',
    packages         = ['notario'],
    author           = 'Alfredo Deza',
    author_email     = 'alfredodeza [at] gmail.com',
    version          = metadata['version'],
    license          = "MIT",
    zip_safe         = False,
    keywords         = "schema, validator, dictionary, enforce",
    long_description = LONG_DESCRIPTION,
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
                        'Programming Language :: Python :: 2.5',
                        'Programming Language :: Python :: 2.6',
                        'Programming Language :: Python :: 2.7',
                        'Programming Language :: Python :: 3.0',
                        'Programming Language :: Python :: 3.1',
                        'Programming Language :: Python :: 3.2',
                        'Programming Language :: Python :: Implementation :: PyPy'
                      ],
    **extra
)
