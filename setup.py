import sys
import os 
from cx_Freeze import setup, Executable

logs_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),'logs')
icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'logo.ico')

includefiles =[logs_path,icon_path]

excludes= ["asyncio","atomicwrites","attr","backcall","certifi","cffi","chardet","colorama","concurrent","cryptography","ctypes",
            "curses","debugpy","defusedxml","distutils","email","greenlet","html","http","idna","importlib_metadata","iniconfig",
            "ipykernel","IPython","ipython_genutils","jedi","jinja2","jsonschema","jupyterlab_pygments","jupyter_client","jupyter_core",
            "lib2to3","markupsafe","matplotlib_inline","msilib","nbclient","nbconvert","nbformat","notebook","packaging","parso","PIL",
            "pluggy","prompt_toolkit","py","pyarrow","pycparser","pydoc_data","pygments","PyQt5","PyQt6","pyrsistent","PySide6","pytest",
            "pyzmq.libs","requests","setuptools","shiboken6","sqlalchemy","sqlite3","test","testpath","toml","tornado","traitlets","unittest",
            "urllib3","wcwidth","win32com","xml","xmlrpc","zmq","_distutils_hack","_pytest"]
                    

setup( name = "Data Converter Tool", 
       version = "1.0",
       description = " Data Converter Tool is custmized for client requiremnt",
       options = {"build_exe":{'excludes':excludes,'include_files':includefiles}},
       executables = [
                    Executable(script="Dc_tool.py",
                                icon="logo.ico",
                                base = "Win32GUI",
                                shortcut_dir="DesktopFolder",
                                shortcut_name=" DC_tool"
                                 )
                                 ])