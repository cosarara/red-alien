#!/usr/bin/env python3

import os, sys

freeze_options = {}

freeze = "--freeze" in sys.argv

if freeze:
    sys.argv.remove("--freeze")
    from cx_Freeze import setup, Executable
    #try:
    #    sys.argv.remove("--freeze")
    #    from cx_Freeze import setup, Executable
    #except ImportError:
    #    print("Warning: cx_Freeze not found. Using distutils")
    #    from distutils.core import setup
    #    freeze = False

#if freeze:
    base = None
    basecli = None
    if sys.platform == "win32":
        base = "Win32GUI"


    # imageformats and platforms directores must be fetched from qt install dir
    data_files_cxfreeze = [
        'asc/data/', 'README.md', 'imageformats', 'platforms', 'asc/data/stdlib']
    build_exe_options = {"packages": ["os", "PyQt5.QtSvg", "PyQt5.QtPrintSupport",
                                      "pkg_resources"],
                         "excludes": ["tkinter"],
                         "include_files": data_files_cxfreeze,
                         "includes": "PyQt5.QtCore"}

    freeze_options = {
        "executables": [
            Executable("asc-qt", base=base, icon="utils/asc.ico"),
            Executable("asc-cli", base=basecli, icon="utils/asc.ico"),
        ],
        "options": {"build_exe": build_exe_options},
    }
else:
    from distutils.core import setup

version = "2.0.1"

setup(name='red-alien',
      version=version,
      description="The Pokemon Advanced Script Compiler for GBA",
      author="Jaume (cosarara97) Delclòs",
      author_email="me@cosarara.me",
      url="https://www.cosarara.me/redalien/",
      packages=['asc'],
      package_data={'asc': ['data/*.txt', 'data/*.tbl', 'data/*.png',
          'data/*.pks', 'data/*.svg', 'data/stdlib/*']},
      #data_files=[('share/applications', ['red-alien.desktop'])],
      scripts=['asc-qt', 'asc-cli'],
      requires=['sip', 'PyQt5', 'Qsci'],
      **freeze_options
      )
