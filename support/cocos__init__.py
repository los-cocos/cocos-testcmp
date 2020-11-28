# -*- coding: utf-8 -*-
"""cocos/__init__.py with pyglet checks striped"""
# flake8: noqa
from __future__ import division, print_function, unicode_literals

# cocos-testcmp-mark <- let it alone

version = "777"

import sys

# add the cocos resources path
import os
import pyglet
pyglet.resource.path.append(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")
    )
pyglet.resource.reindex()



try:
    unittesting = hasattr(pyglet, 'mock_level')
except KeyError:
    unittesting = False
del os, pyglet

# in windows we use the pygame package to get the SDL dlls
# we must get the path here because the inner pygame module will hide the real
if sys.platform == 'win32':
    # module imp is deprecated in 3.5, the 3.x functionality
    # needed appears in 3.4
    major, minor = sys.version_info[0:2]
    if major == 2 or major == 3 and minor < 4:
        import imp
        try:
            dummy, sdl_lib_path, dummy = imp.find_module('pygame')
            del dummy
        except ImportError:
            sdl_lib_path = None
    else:
        import importlib
        try:
            spec = importlib.util.find_spec("pygame")
            sdl_lib_path = spec.submodule_search_locations[0]
        except Exception:
            sdl_lib_path = None


if not unittesting:

    # using 'from cocos import zzz' to make zzz appear in pycharm's autocomplete for cocos.
    from cocos import cocosnode
    from cocos import actions
    from cocos import director
    from cocos import layer
    from cocos import menu
    from cocos import sprite
    from cocos import path
    from cocos import scene
    from cocos import grid
    from cocos import text
    from cocos import camera
    from cocos import draw
    from cocos import skeleton
    from cocos import rect
    from cocos import tiles
