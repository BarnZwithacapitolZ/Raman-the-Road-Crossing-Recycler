from cx_Freeze import setup, Executable
import os

os.environ['TCL_LIBRARY'] = r'C:\Program Files\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Program Files\Python36\tcl\tk8.6'

includeFiles = ['settings.py',
                'sprites.py',
                'mapConfig.py',
                'data/',
                r"C:\Program Files\Python36\DLLs\tcl86t.dll",
                r"C:\Program Files\Python36\DLLs\tk86t.dll"]

shortcut_table = [("DesktopShortcut",
                   "DesktopFolder",
                   "Demo Build",
                   "TARGETDIR",
                   "[TARGETDIR]build_1.exe",
                   None,
                   None, 
                   None,
                   None,
                   None,
                   None,
                  'TARGETDIR')]

msi_data = {"Shortcut": shortcut_table}
bdist_msi_options = {'data': msi_data}

setup(name = "Raman the Road Crossing Recycler",
      version = "1.0",
      description="Game for college",
      options = {"build_exe": {"packages":["pygame", "pytmx"],
                               "include_files":includeFiles},
                               "bdist_msi": bdist_msi_options},
      executables = [Executable("recycle_game.py", base = "Win32GUI")])


