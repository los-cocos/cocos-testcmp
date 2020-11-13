=============
cocos-testcmp
=============

Workflow
--------

Initialization
______________

- make a venv and activate it; now python would be invoked by 'python' command
- clone cocos-testcmp
- cd cocos-testcmp
- python -m pip install -e .
- edit cocos-testcmp/conf.py
- run python 00_init.py

Loop
____

- edit conf.py to set the comparison targets
- run 'python do_test.py', this will report about tracebacks and snapshots differences for the pair specified in conf.py
- optional: use commands switches (only one per invocation) to perform certain tasks::
  
  --del-last-cmp
  --del-all-cmp
  --dump-cache
	  
Extra tests
___________

When doing a cocos release, once the comparison part is satisfactory scripts outside test/ should be tested, meaning a manual run and eyeballing they look good

- all in samples samples/
- in particular samples/tetrico should be tested with and without sound support
- tools/editor.py
- tools/gentileset.py
- tools/skeleton/anim_player.py
- tools/skeleton/animator.py
- tools/skeleton/skeleton_editor.py
