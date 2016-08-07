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
        def __init__(self, a, base):
            pass

data_files_cxfreeze = [
    'asc/data/', 'README.md', 'imageformats', 'asc/data/stdlib']
build_exe_options = {"packages": ["os", "PyQt5.QtSvg", "PyQt5.QtPrintSupport",
                                  "pkg_resources"],
                     "include_files": data_files_cxfreeze,
                     "includes": "PyQt5.QtCore",
                     "icon": "utils/asc.ico"}

try:
    with os.popen("git describe --always | sed 's|-|.|g'") as psfile:
        version = psfile.read().strip("\n")
except:
    version = "git"

base = None
basecli = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name='Blue Spider',
      version=version,
      description="The Pokemon Advanced Script Compiler for GBA",
      author="Jaume (cosarara97) Delclòs",
      author_email="cosarara97@gmail.com",
      url="https://github.com/cosarara97/red-alien",
      packages=['asc'],
      package_data={'asc': ['data/*.txt', 'data/*.tbl', 'data/*.png',
          'data/*.pks', 'data/*.svg', 'data/stdlib/*']},
      scripts=['asc-qt', 'asc-cli'],
      requires=['sip', 'PyQt5', 'Qsci'],
      options={"build_exe": build_exe_options},
      executables=[
          Executable("asc-qt", base=base),
          Executable("asc-cli", base=basecli),
          ],
      )


