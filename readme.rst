Overview
--------

Testing in cocos is accomplished by

- running unittests in cocos2d/utest/

- taking automated snapshots along the execution of the cocos2d/test/ demo scripts and doing an human assisted comparison with a reference snapshot session 

This package helps with that by building a comparison report for the two targeted versions specified in the configuration, version meaning a tuple of (python version, pyglet version, cocos version), where the pyglet and cocos version are specific git commits. 

The report is a html page that tells 

- summary unittest results for each run; should be 0 errors and 0 fails
- link to pytest output for the unittests
- summary of snapshot taking session for each version, including tracebacks detected; should be 0
- link to snapshots details, which will have the tracebaks detected and other info 
- image comparison results, showing side by side the snapshots that differs between runs, plus two delta images
  - black and white, with black meaning pixel have equal value in both images
  - greyscale, with black for equals and progressively whiter as abs(delta) grows
  Is up to human judgment if the images are similar enough to consider them equal

If one of the version selected is the reference version, and

- the unittests for the other version has 0 errors and 0 fails
- no tracebacks for the other version
- All snapshots differences are considered non significative

then the other version is considered good.

To consider a cocos version good to release, individual runs with py lower, py last, pyglet lower, pyglet high must be all good. 
 
Setting the venv
----------------

- make a venv, I will call it py37_cmp::

    D:\dev>py -3.7 -m venv py37_cmp

- activate the pyenv, now the command 'python' would refer to the python in the venv, only applies to the activated console::

    D:\dev>py37_cmp\Scripts\activate
    
  From now, all commands are issued at the activated console

- upgrade pip to not see pip warning messages::

    python -m pip install pip --upgrade

Cloning cocos-testcmp
---------------------

Clone cocos-testcmp, the repo_url depends if you are getting it from the official repo or a forked repo, and the git protocol to use (https or git over SSH)::

    git clone repo_url
        
By example, from the official repo and with https::

    git clone https://github.com/los-cocos/cocos-testcmp.git

Now cocos-testcmp/ will hold the Working Copy (WD) of the repo,and it will be in the default branch, 'main' because that is the mew style, not 'master'
If you are developing cocos-testcmp, switch to the desired branch, else let it alone.

Initial configuration
--------------------- 

Don't skip this, else you will get a bunch of tracebacks later.

The file cocos-testcmp/conf.py is the one to edit.

- Set 'main_venv_python' to a list with only one item, the fully qualified python executable to drive the data collection. You get it by running in the activated console::

    python -c "import sys; print(sys.executable)"

  In my case, I would set::
  
    main_venv_python = [D:\dev\py37_cmp\Scripts\python.exe]

- Setting up the different pythons to use to exercise cocos

  On Windows no configuration needs to be done, it is assumed 'py -X.Y' will invoke a python version X.Y interpreter.

  On other OSes a table telling how to invoke python for each version X.Y to exercise must be filled.
   
  That's the 'pyversions_available' dict in conf.py, which maps each X.Y desired with the fully qualified python executable to invoke.
   
  if you invoke a python version X.Y interpreter with 'foo' run::
  
      foo -c "import sys; print(sys.executable)"

  in another console, not the activated console, to get the fully qualified python executable to use.
  Common values for 'foo' are 'python', 'python2', python3'
   
  The tests will be run in venvs created from those pythons
   
  More pythons can be added anytime later, it is best to provide and configure in advance to have less things to worry when running the tests.
   
- Adjust repo URLs if using forks or other git protocol, casual users can left as it comes.
  Repos to configure are for packages 'remembercases', 'cocos2d', 'pyglet'
  Example for remembercases::

	remembercases_URL = https://gitlab.com/ccanepa/remembercases.git
  
  When developing cocos-testcmp it may be of interest to select a branch / tag to checkout remembercases, that can be done by setting the 'remembercases_checkout_str' to the desired value. Caveat: it only would be read at the 00_init stage
  
- If needed, adjust which packages, with optional versions restrictions, should be installed in each venv to test.
  One line per package, in the 'packages' dict.
  By example, on Win10 + python 3.9+ you want "PIL": "pillow==8",
  
- Now in the activated console do::

    cd cocos-testcmp
    python 00_init.py

  This creates the work/ subtree, makes there clones of 'remembercases', 'cocos2d', 'pyglet', sets the tests to be exercised.
     
- Install cocos-testcmp in the venv so some imports work
  Still in cocos-testcmp directory::
  
     python -m pip install -e .
     
That ends the preparation phase.

Test loop
---------

- Edit conf.py and set v_ref and v_other to tell which combination of (python, pyglet, cocos) will be used

- Run comparison with::
     python do_test.py

  Note that at least in Windows the activated console should have focus when do_test begins to take snapshots, else will produce snapshots of 0 filesize and the comparison will crash with a traceback.

- Repeat as necessary

- Optional: use commands switches (only one per invocation) to perform certain tasks::
  
  --del-last-cmp
  --del-all-cmp
  --dump-cache

Extra tests
-----------

When doing a cocos release, once the comparison part is satisfactory scripts outside test/ should be tested, meaning a manual run and eyeballing they look good

- all in samples samples/
- in particular samples/tetrico should be tested with and without sound support
- tools/editor.py
- tools/gentileset.py
- tools/skeleton/anim_player.py
- tools/skeleton/animator.py
- tools/skeleton/skeleton_editor.py

Tips
----

- Each do_test run will start by checking out the specified pyglet and cocos commits, so if you edit and don't commit you will lose the changes. Safest is to do changes in a WD outside work/, push from there, pull from work/cocos (and remember to adjust cocos version in conf.py)
