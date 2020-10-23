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
	  
---------

prob transitorio: al contar black snapshots se recibio: 

...
PIL.UnidentifiedImageError: cannot identify image file 'D:\\dev\\cocos-testcmp\\
work\\snp\\py3.7.7_p1467968c_Cfe6beb3\\test_acceldeccel_01.000.png'

Todos los files son de tamaño cero; La toma fue hecha con las ventanas d test en background

-----------
