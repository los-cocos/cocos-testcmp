# -*- coding: utf-8 -*-
"""
This script suposed to run in a venv
"""
from __future__ import division, print_function, unicode_literals
import os, shutil, subprocess, sys

import support.fs as fs

import conf as te

def clone_lib(libname, URL, dst):
    cmd_parts = ["git", "clone", URL, dst]
    if subprocess.call(cmd_parts):
        print("\nError, could not clone lib '%s'. Cmd tried:" % libname)
        print("   ", " ".join(cmd_parts))  
        sys.exit(1)
    
def install_remembercases(python_venv_cmdline, path_remembercases, checkout_str):
    print("\nCheckout the desired remembercases version")
    cmd_parts = ["git", "checkout", checkout_str]
    print("cmdline:", " ".join(cmd_parts))
    if subprocess.call(cmd_parts, cwd=path_remembercases):
        print("\nError, could not checkout remembercases at desired version. Cmd tried:")
        print("   ", " ".join(cmd_parts))  
        sys.exit(1)
    print("\nInstall remembercases in the main_venv_python")
    cmd_parts = list(python_venv_cmdline) + ["-m", "pip", "install", "-e", path_remembercases]
    print("cmdline:", " ".join(cmd_parts))
    if subprocess.call(cmd_parts, cwd=path_remembercases):
        print("\nError, could not install remembercases. Cmd tried:")
        print("   ", " ".join(cmd_parts))  
        sys.exit(1)
    


base_dir = os.path.dirname(os.path.abspath(__file__))
path_services = fs.PathServices(base_dir)

if os.path.exists(path_services.work):
    print("\n Error, there exista a 'work' directory. Delete it to start clean")
    sys.exit(1)

print("\nCreating work/ and setting reference snapshots")
shutil.copytree(path_services.ref, path_services.work)
#os.mkdir(path_services.snp) # no, just created the line above
os.mkdir(path_services.pys)
os.mkdir(path_services.cmp)

print("\nCloning pyglet")
clone_lib("pyglet", te.pyglet_URL, path_services.pyglet)

print("\nCloning oocos")
clone_lib("cocos", te.cocos_URL, path_services.cocos)

print("\nCheckout the cocos version where we want the tests come from")
cmd_parts = ["git", "checkout", te.test_checkout_str]
if subprocess.call(cmd_parts, cwd=path_services.cocos):
    print("\nError, could not checkout cocos at desired version. Cmd tried:")
    print("   ", " ".join(cmd_parts))  
    sys.exit(1)

print("\nCopy tests to run")
shutil.copytree(path_services.cocos_test, path_services.test)

print("\nCloning remembercases")
clone_lib("remembercases", te.remembercases_URL, path_services.remembercases)

install_remembercases(te.main_venv_python, path_services.remembercases, te.remembercases_checkout_str)


print("*** initialization done ***")
