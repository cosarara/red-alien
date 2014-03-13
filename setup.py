#!/usr/bin/env python3

from distutils.core import setup
import os

try:
    with os.popen("git describe --always | sed 's|-|.|g'") as psfile:
        version = psfile.read().strip("\n")
except:
    version = "git"

setup(name='Blue Spider',
      version=version,
      description="The Pokemon Advanced Script Compiler for GBA",
      author="Jaume (cosarara97) Delclòs",
      author_email="cosarara97@gmail.com",
      url="https://github.com/cosarara97/red-alien",
      packages=['asc'],
      package_data={'asc': ['data/*']},
      scripts=['asc-qt', 'asc-cli'],
      requires=['sip', 'PyQt4', 'Qsci'],
      )


