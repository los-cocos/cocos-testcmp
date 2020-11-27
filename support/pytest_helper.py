from __future__ import division, print_function, unicode_literals
import six

import os, sys

import support.fs as fs

# matching "os.environ['cocos_utest']" in utest/, except runner1.py
text_matchs_cu = """
test_RectMapCollider__no_stuck.py
test_acceldeccel.py
test_actions.py
test_director_scene_changes.py
test_instant_actions.py
test_p_ba_Loop_Actions.py
test_p_ba_Loop_IntervalAction.py
test_p_ba_Repeat_Action.py
test_p_ba_Sequence_Action.py
test_p_ba_Sequence_IntervalAction.py
test_p_ba_Spawn_Action.py
test_p_ba_Spawn_IntervalAction.py
test_p_ba_cocosnode_actions.py
test_p_ba_operands_different_classes.py
test_p_ba_operators_result_type.py
test_rect.py
test_tiles.py
test_tmx.py
test_RectMapCollider__no_stuck - copia.py
"""

prefix = ( "# DONT set cocos_utest, disregard cocos_utest comments and docstrings,\n" +
           "# this file hotpatched by cocos-testcmp ignores cocos_utest\n" )

def patch_assert_cu(path_services):
    print("in patch_assert_cu")
    global text_matchs_cu, prefix
    matchs_cu = sorted(text_matchs_cu.split('\n')[1:-1])
    print(matchs_cu)
    print("len:", len(matchs_cu))

    # transform "assert os.environ['cocos_utest']" -> "assert True"
    for name in matchs_cu:
        fname = os.path.join(path_services.cocos_utest, name)
        try:
            with open(fname, "rb") as f:
                as_bytes = f.read()
            opened = True
        except Exception:
            opened = False
        if opened:
            in_ = as_bytes.decode("utf8")
            out = prefix + in_.replace("os.environ['cocos_utest']", "True")
            as_bytes = out.encode("utf8")
            with open(fname, "wb") as f:
                as_bytes = f.write(as_bytes)


new_runner1_tail ="""
def proceed(fname):
    tests = get_list(fname)
    cmd = 'py.test -v ' + ' '.join(tests)
    print(cmd)
    os.system(cmd)

if len(sys.argv)!=2:
    usage()
else:
    proceed(sys.argv[1])
"""

def patch_runner1(path_services):
    global new_runner1_tail, prefix
    fname = os.path.join(path_services.cocos_utest, "runner1.py")
    with open(fname, "rb") as f:
        as_bytes = f.read()
    in_ = as_bytes.decode("utf8")
    start = in_.find("def proceed")
    out = prefix + in_[:start] + new_runner1_tail
    as_bytes = out.encode("utf8")
    with open(fname, "wb") as f:
        as_bytes = f.write(as_bytes)

# patch director "os.environ.get('cocos_utest', False)" -> "hasattr(pyglet, 'mock_level')"
def patch_director(path_services):
    fname = path_services.cocos_director
    with open(fname, "rb") as f:
        as_bytes = f.read()
    in_ = as_bytes.decode("utf8")
    out = in_.replace("os.environ.get('cocos_utest', False)", "hasattr(pyglet, 'mock_level')")
    as_bytes = out.encode("utf8")
    with open(fname, "wb") as f:
        as_bytes = f.write(as_bytes)

def patch_all(path_services):
    patch_assert_cu(path_services)
    patch_runner1(path_services)
    patch_director(path_services)

def needs_legacy_patch(path_services):
    fname = path_services.pytest_nolegacy
    return not os.path.exists(fname)

def patch_if_needed(path_services):
    if needs_legacy_patch(path_services):
        patch_all(path_services)

# What its seen currently at end of capture is
"""
====================== 542 passed, 20 warnings in 0.91s =======================

------------------
"""
#where the '------------------\n' comes from the runner in do_test
def get_summary_line(text):
    """
    text assumed the output captured in do_test func pytest_from_venv
    this is britle, if pytest changes the format it will not work
    """
    try:
        i = text.rfind('\n')
        j = text.rfind('\n', 0, i-1)
        #print("i, j:", i, j)
        #print("j repr:", repr(text[j+1:i]))
        k = text.rfind('\n', 0, j-1)
        #print("k repr:", repr(text[k+1:j]))
        s = text[k+1:j].replace('=', "")
        s = s.strip()
        #print("s repr:", repr(s))
    except Exception:
        s = "???"
    return s


if __name__ == "__main__":
    this_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(this_dir)
    #print("base_dir:", base_dir)
    path_services = fs.PathServices(base_dir)
    patch_if_needed(path_services)
