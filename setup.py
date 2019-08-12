#!/usr/bin/env python3

import os, sys

try:
    if not "--freeze" in sys.argv: # hack!
        fail()
    sys.argv.remove("--freeze")
    from cx_Freeze import setup, Executable
except:
    print("Warning: cx_Freeze not found. Using distutils")
    from distutils.core import setup
    # lol hack
    class Executable:
        def __init__(self, *args, **kwargs):
            pass

# imageformats and platforms directores must be fetched from qt install dir
data_files_cxfreeze = [
    'asc/data/', 'README.md', 'imageformats', 'platforms', 'asc/data/stdlib']
build_exe_options = {"packages": ["os", "PyQt5.QtSvg", "PyQt5.QtPrintSupport",
                                  "pkg_resources"],
                     "excludes": ["tkinter"],
                     "include_files": data_files_cxfreeze,
                     "includes": "PyQt5.QtCore"}

version = "2.0.0"

base = None
basecli = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name='red-alien',
      version=version,
      description="The Pokemon Advanced Script Compiler for GBA",
      author="Jaume (cosarara97) Delclòs",
      author_email="me@cosarara.me",
      url="https://www.cosarara.me/redalien/",
      packages=['asc'],
      package_data={'asc': ['data/*.txt', 'data/*.tbl', 'data/*.png',
          'data/*.pks', 'data/*.svg', 'data/stdlib/*']},
      scripts=['asc-qt', 'asc-cli'],
      requires=['sip', 'PyQt5', 'Qsci'],
      options={"build_exe": build_exe_options},
      executables=[
          Executable("asc-qt", base=base, icon="utils/asc.ico"),
          Executable("asc-cli", base=basecli, icon="utils/asc.ico"),
          ],
      )


