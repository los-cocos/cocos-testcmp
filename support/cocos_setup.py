# -*- coding: utf-8 -*-
"""cocos setup.py minus the pyglet dep 
"""

# cocos-testcmp-mark <- let it alone

__version__ = "777"
try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages

import os

f = open('README.rst','rU')
long_description = f.read()
f.close()

install_requires=['six>=1.4', ]
dependency_links = []

setup(
    name = "cocos2d",
    version = __version__,
    author = "cocos2d Team",
    license="BSD",
    description = "a 2D framework for games and multimedia",
    long_description=long_description,
    url = "http://python.cocos2d.org",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        ("Topic :: Software Development :: Libraries :: Python Modules"),
        ("Topic :: Games/Entertainment"),
        ],
 
    packages = ['cocos', 'cocos/actions', 'cocos/audio', 'cocos/layer', 'cocos/scenes'],
    package_data={'cocos': ['resources/*.*']},

    install_requires=install_requires,
    dependency_links=dependency_links,

    include_package_data = True,
    zip_safe = False,
    )
