# -*- coding: utf-8 -*-
"""
"""

__author__ = "cocos2d team"
__author_email__ = "lucio.torre@gmail.com"
__version__ = "0.6.9"
__date__ = "2020 11 18"

from setuptools import setup

f = open('README.rst', 'rU')
long_description = f.read()
f.close()

install_requires = ["six", "numpy", "pillow"]
dependency_links = []

setup(
    name="cocos-testcmp",
    version=__version__,
    author="cocos2d Team",
    license="BSD",
    description="support for cocos2d testing",
    long_description=long_description,
    url="http://python.cocos2d.org",
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

    packages=['support', ],
    #package_data={'cocos': ['resources/*.*']},
    package_data={},

    install_requires=install_requires,
    dependency_links=dependency_links,

    include_package_data=False,  # True
    zip_safe=False,
    )
