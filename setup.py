import cx_Freeze
import sys
import os

PYTHON_INSTALL_DIR = os.path.dirname(sys.executable)
os.environ["TCL_LIBRARY"] = os.path.join(PYTHON_INSTALL_DIR, "tcl", "tcl8.6")
os.environ["TK_LIBRARY"] = os.path.join(PYTHON_INSTALL_DIR, "tcl", "tk8.6")

base = None

#if sys.platform == "win32":
base = "Win32GUI"

executables = [cx_Freeze.Executable("app.py", base=base, icon="imgs/paperfeatherAllSizes.ico", targetName="MarText.exe")]
included_files = ["imgs", "data",
(os.path.join(PYTHON_INSTALL_DIR, "DLLs", "tk86t.dll"), os.path.join("lib", "tk86.dll")),
(os.path.join(PYTHON_INSTALL_DIR, "DLLs", "tcl86t.dll"), os.path.join("lib", "tcl86.dll")),
]

cx_Freeze.setup(
    name="MarText",
    options = {"build_exe":{"packages":["TkinterDnD2", "tkinter", "chardet", "configparser"], "include_files":included_files}},
    version = "1.00",
    description = "Text Editor",
    executables = executables
)