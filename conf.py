# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

### -> This section must be configured before the 00_init.py run

remembercases_URL = "git@gitlab.com:ccanepa/remembercases.git"
remembercases_checkout_str = "gits" #"master" #"v0.4.0"
pyglet_URL = "https://github.com/pyglet/pyglet.git"
cocos_URL  = "git@github.com:los-cocos/cocos.git"

# git checkout string used before copying cocos\test
test_checkout_str = "master"

# git checkout string for the commit where cocos\custom_clocks.py be taken,
# None for 'use original custom_clocks 
custom_clocks_checkout_str = None #"master"

main_venv_python = ["D:/dev/py37_cmp/Scripts/python.exe",]
#main_venv_python = ["D:/cla/dev2/py39_cmp/Scripts/python.exe",]

### <- This section must be configured before the 00_init.py run

# packages installed by pip from pypi
packages = {
    # import_name: pip_name
    # examples
    # "numpy": "numpy",
    # "numpy": "numpy==1.18.4",
    "six": "six",
    "numpy": "numpy",
    "PIL": "pillow<8", # '<8' needed for pyglet <1.5.9; py39's pillow wants 8+ in windows
    }

# pythons needed to create venv s for testing
# used in unix-like OS, must be adjudsted to the testing machine.
# here a setting to work in the raspi3 with raspbian buster
# in windows the mapping "X.Y" -> "py -X.Y" is assumed 
pyversions_available = {
    #version: cmdline to invoke python, by example "/bin/python3.7"
    "3.7": "/usr/bin/python3.7",
    "2.7": "/usr/bin/python2.7",
    }

#pyglet 1.5.9, cocos 0.6.9
v_ref = ("3.7", "33175228", "release-0.6.9")

#pyglet 1.4.11 release, cocos 0.6.7 release 
v_other = ("3.7", "0af100f4", "release-0.6.7")

# informative


### notable pyglet _git_ commits
friendly_pyglet = {
    # abrev. sha: friendly name
    "33175228": "1.5.9 2020 11 09 (ATM last 1.5.x released)",
    "a39ebc20": "1.5.8 2020 10 16",
    "b9c9ffae": "1.5.7 2020 06 21",
    "ce8b3073": "1.5.6 2020 06 12",
    "4f2e2d6c": "1.5.5 2020 05 02",
    "1ffd9402": "1.5.3 2020 04 06 breaks cocos-testcmp + cocos 0.6.8, custom_clocls problem",
    "edf43ad5": "1.5.2 2020 03 23",
    "0af100f4": "1.4.11 2020 04 18(last(?) 1.4.x, last py2.7 support)",
    "525b7aff": "1.4.3 2019 09 05 (first usable 1.4.x, needs cocos >= 0.6.7)",
    "0419b96c": "1.3.3 2019 11 24 (last released 1.3.x)",
    "1467968c": "1.3.0 2017 11 10", # py _must_ be < 3.7
    "a9c6ffdb": "last 1.2-maintenance 2016 08 28",
    "2f2283d6": "1.2.4 2015 09 02 (last released 1.2.x)",
    "521c04e1": "1.2alpha1 (sliding) 2014 03 24, used by release cocos 0.6.0",
    "bfe1b597": "1.2dev (sliding) 2012 08 11, probably used by cocos release 0.5.5",
    "c4b868f0": "1.2dev (sliding) 2011 08 20, probably used by cocos release 0.5.0",
    "ec22d949": "1.1.4 2009 12 31 (for py < 2.5 needs ctypes)"
    }

friendly_cocos = {
    "90b9350": "0.6.9 2020 11 08",
    'cab0b8a': "0.6.8 2020 02 02",
    '32af346': "0.6.7 2019 09 06 (1st cocos version to support pyglet 1.4.x, needs 1.4.3+)",
    'd90978d': "0.6.6 2019 08 15",
    'fe6beb3': "0.6.5 2017 08 24 (1st cocos version to support pyglet 1.3.x, also runs 1.2.x)",
    '6c894fa': "0.6.4 2016 06 12",
    'a44fba5': "0.6.3 2015 04 26 (needs pyglet<=1.2.4 due to #240)",
    'e543b18': "0.6.2 2015 04 08",
    'c737675': "0.6.0 2014 03 24 (1st cocos version to support py3, needs 3.3+ or 2.6+)",
    'e084685': "0.5.5 2012 08 13",
    '312a7a6': "0.5.0 2011 10 26",
    '20e2bed': "0.4.0 2010 09 27 (needs pyglet 1.1.4+)",
    '10ffb10': "0.3.0 2008 09 05 (needs pyglet 1.1b2+)",
    }

# In raspi3 with raspbian buster

# To know the python version
    # $ python2 --version
    # Python 2.7.16

    # $ python3 --version
    # Python 3.7.3

# To know from where they come
  # py2
    # pi@raspberrypi:~/dev2 $ ls -l /usr/bin/python
    # lrwxrwxrwx 1 root root 7 Mar  4  2019 /usr/bin/python -> python2
    # pi@raspberrypi:~/dev2 $ ls -l /usr/bin/python2
    # lrwxrwxrwx 1 root root 9 Mar  4  2019 /usr/bin/python2 -> python2.7
    # pi@raspberrypi:~/dev2 $ ls -l /usr/bin/python2.7
    # -rwxr-xr-x 1 root root 2984816 Oct 10  2019 /usr/bin/python2.7

  # py3
    # pi@raspberrypi:~/dev2 $ ls -l /usr/bin/python3
    # lrwxrwxrwx 1 root root 9 Mar 26  2019 /usr/bin/python3 -> python3.7
    # pi@raspberrypi:~/dev2 $ ls -l /usr/bin/python3.7
    # -rwxr-xr-x 2 root root 4275580 Jul 25 10:03 /usr/bin/python3.7

# references about softlinks and hardlinks
# http://www.penguintutor.com/raspberrypi/links-reference-guide
# https://www.unixtutorial.org/how-to-find-what-symlink-points-to/
