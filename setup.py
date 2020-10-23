# -*- coding: utf-8 -*-
"""
   example operation for generating release without handling the docs:
       git clone https://github.com/los-cocos/cocos.git cocos_trunk
       cd cocos_trunk
       py -3.7 setup.py sdist >../sdist.log
       [ the generated package will be in cocos_trunk/dist ]

       Look at tools/building_release_notes.txt for more info about building
       release.
"""

__author__ = "cocos2d team"
__author_email__ = "lucio.torre@gmail.com"
__version__ = "0.6.8"
__date__ = "2020 02 02"

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

install_requires=["six", "numpy", "pillow"]
dependency_links = []

setup(
    name = "cocos-testcmp",
    version = __version__,
    author = "cocos2d Team",
    license="BSD",
    description = "support for cocos2d testing",
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
 
    packages = ['support',],
    #package_data={'cocos': ['resources/*.*']},
    package_data={},

    install_requires=install_requires,
    dependency_links=dependency_links,

    include_package_data = False, #True
    zip_safe = False,
    )
