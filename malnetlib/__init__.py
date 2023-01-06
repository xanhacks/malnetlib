from sys import exit as sys_exit
from pythonnet import load
load("coreclr")

import clr
clr.AddReference("System.IO")
from System.IO import FileNotFoundException

try:
    clr.AddReference("dnlib")
except FileNotFoundException:
    print("Unable to find 'dnlib.dll'.")
    print("Please follow the installation instructions.")
    sys_exit(1)
