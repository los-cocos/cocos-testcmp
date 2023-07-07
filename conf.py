# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

### -> This section must be configured before the 00_init.py run (but more
###    python versions can be added at any time)

# python executable to drive the data collection, the one in the venv
main_venv_python = [r"D:\venvs\py38_cmp\Scripts\python.exe"]  # (windows)
# main_venv_python = ["/home/pi/dev2/py37_cmp/bin/python"]  # (raspbian buster)

# fully qualified python executable to invoke to run a python at version X.Y
pyversions_available = {
    # version: cmdline to invoke python, by example "/bin/python3.7"
    "3.7": "/usr/bin/python3.7",
    "2.7": "/usr/bin/python2.7",
    }

# package remembercases, project page at https://gitlab.com/ccanepa/remembercases
# remembercases_URL = https://gitlab.com/ccanepa/remembercases.git
remembercases_URL = "git@gitlab.com:ccanepa/remembercases.git"
remembercases_checkout_str = "master"  # "v0.4.1" # "branch_name" #"tag_name"

# package pyglet, project page at https://github.com/pyglet/pyglet
pyglet_URL = "https://github.com/pyglet/pyglet.git"

# package cocos2D, project page at https://github.com/los-cocos/cocos
# cocos_URL = https://github.com/los-cocos/cocos.git
cocos_URL = "git@github.com:los-cocos/cocos.git"

# git checkout string used before copying cocos\test
test_checkout_str = "master"

# git checkout string for the commit where cocos\custom_clocks.py be taken,
# None for 'use original custom_clocks'
custom_clocks_checkout_str = None  # "master"

# packages to install with pip from pypi in each venv to test
packages = {
    # import_name: pip_name
    # examples
    # "numpy": "numpy",
    # "numpy": "numpy==1.18.4",
    "six": "six",
    "numpy": "numpy",  # "numpy==1.16.2", # the 1.16.2 used in the raspi3
    "PIL": "pillow",  # '<8' needed for pyglet <1.5.9; py39's pillow wants 8+ in windows,
                        # py36 needs pillow<9, py37 needs pillow<10 
    "pytest": "pytest",
    }

### <- This section must be configured before the 00_init.py run


### -> Configure this for each comparison run desired

# The tuples specify (python version, pyglet version, cocos version)
# pyglet and cocos versions are specified as a string to do a
# 'git checkout string'; branch names, tag names and commit hashes are fine.
# Prepending an '@' to the py version will select the special reference session
# provided with cocos-testcmp, all other info will be ignored

# pyglet 1.5.9, cocos 0.6.9
v_ref = ("@3.7", "v1.5.9", "release-0.6.9")

# pyglet 1.5.27, cocos 0.6.9 transitioning to 0.6.10
v_other = ("3.8", "v1.5.27", "888fcc7")

### <- Configure this for each comparison run desired


### --> Only for reference, not used in cocos-testcmp
friendly_pyglet = {
    # abrev. hash: friendly name
    "b9c8c10e" : "v1.5.27 2022 09 21",
    "5de9e518": "v1.5.17 2021 05 21",
    "ba4e722e": "v1.5.16 2021 04 13",  # some text failures due to
                                       # https://github.com/pyglet/pyglet/issues/378
    "03eeadbb": "v1.5.15 2021 02 09",
    "e3c27ab2": "v1.5.13 2020 12 18",
    # no 1.5.12 on pypi
    "69a09bb8": "v1.5.11 2020 11 18",
    "3536341e": "v1.5.10 2020 11 15",
    "33175228": "1.5.9 2020 11 09",
    "a39ebc20": "1.5.8 2020 10 16",
    "b9c9ffae": "1.5.7 2020 06 21",
    "ce8b3073": "1.5.6 2020 06 12",
    "4f2e2d6c": "1.5.5 2020 05 02",
    "1ffd9402": "1.5.3 2020 04 06 breaks cocos-testcmp + cocos 0.6.8, custom_clocks problem",
    "edf43ad5": "1.5.2 2020 03 23",
    "0af100f4": "1.4.11 2020 04 18(last(?) 1.4.x, last py2.7 support)",
    "525b7aff": "1.4.3 2019 09 05 (first usable 1.4.x, needs cocos >= 0.6.7)",
    "0419b96c": "1.3.3 2019 11 24 (last released 1.3.x)",
    "1467968c": "1.3.0 2017 11 10",  # py _must_ be < 3.7
    "a9c6ffdb": "last 1.2-maintenance 2016 08 28",
    "2f2283d6": "1.2.4 2015 09 02 (last released 1.2.x)",
    "521c04e1": "1.2alpha1 (sliding) 2014 03 24, used by release cocos 0.6.0",
    "bfe1b597": "1.2dev (sliding) 2012 08 11, probably used by cocos release 0.5.5",
    "c4b868f0": "1.2dev (sliding) 2011 08 20, probably used by cocos release 0.5.0",
    "ec22d949": "1.1.4 2009 12 31 (for py < 2.5 needs ctypes)"
    }

friendly_cocos = {
    "888fcc7": "0.6.9 2023 07 06", # begin work for release 3.6.10
    "90b9350": "0.6.9 2020 11 08",
    'cab0b8a': "0.6.8 2020 02 02",
    '32af346': "0.6.7 2019 09 06 (1st cocos vs to support pyglet 1.4.x, needs 1.4.3+)",
    'd90978d': "0.6.6 2019 08 15",
    'fe6beb3': "0.6.5 2017 08 24 (1st cocos vs to support pyglet 1.3.x, also runs 1.2.x)",
    '6c894fa': "0.6.4 2016 06 12",
    'a44fba5': "0.6.3 2015 04 26 (needs pyglet<=1.2.4 due to #240)",
    'e543b18': "0.6.2 2015 04 08",
    'c737675': "0.6.0 2014 03 24 (1st cocos vs to support py3, needs 3.3+ or 2.6+)",
    'e084685': "0.5.5 2012 08 13",
    '312a7a6': "0.5.0 2011 10 26",
    '20e2bed': "0.4.0 2010 09 27 (needs pyglet 1.1.4+)",
    '10ffb10': "0.3.0 2008 09 05 (needs pyglet 1.1b2+)",
    }
