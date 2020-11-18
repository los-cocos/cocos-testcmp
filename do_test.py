# -*- coding: utf-8 -*-
"""
If no subcommand provided it completes a comparison between two cocos versions,
adds the data collected to reports and db.

Subcommands allows to discard or dump some of the generated info.

Usage
  python do_test.py [subcommand]

Subcommands:
  <no subcommand>: takes snapshots over test/, runs pytest over utest/,
      makes a comparison report, adds info to cache and db
      
  --del-last-cmp: deletes last cmp data, but not SnapshotSession(s) generated
  
  --del-all-cmp: deletes all comparison data, but not the related snapshot info

  --dump-cache: dumps cache

  -h or --help: shows this text
"""

from __future__ import division, print_function, unicode_literals
import six

import os, sys
import pickle
from collections import namedtuple
import copy
import shutil
import traceback as tb

#import support
import support.fs as fs
import support.helpers as hl
import support.templates as templates
import support.pytest_helper as pt

import conf as tc


##import remembercases as rm
import remembercases.gits as gits
import remembercases.cmds as cm
import remembercases.doers as doers
import remembercases.image_comparison as ri

cache = None
cache_path = None

def save_cache():
    global cache, cache_path
    # protocol 2 is compatible with both py2.x and 3.x , protocol 3 is py3 only
    with open(cache_path, "wb") as f:
        pickler = pickle.Pickler(f, protocol=2)
        pickler.dump(cache)
    

def save_pickle(fname, obj):
    # protocol 2 is compatible with both py2.x and 3.x , protocol 3 is py3 only
    with open(fname, "wb") as f:
        pickler = pickle.Pickler(f, protocol=2)
        pickler.dump(obj)

def load_pickle(fname):
    with open(fname, "rb") as f:
        unpickler = pickle.Unpickler(f)
        obj = unpickler.load()
    return obj

def get_python_cmdline(asked_py):
    diagnostic = ""
    if sys.platform == "win32":
        cmd_python = ["py", "-%s" % asked_py]
        print("cmd_python:", cmd_python)
    else:
        try:
            cmd_python = [tc.pyversions_available[asked_py]]
        except KeyError:
            cmd_python = None
            msg = "Missing version in test_conf.pyversions_available, not found:"
            diagnostic = msg % asked_py
    return diagnostic, cmd_python

#!! py 2.7 reporta --version en stderr, no en stdout
# example output expected: 'Python 2.7.18', 'Python 3.7.7'
def query_python_version(python_cmdline):
    cmdline = list(python_cmdline)
    cmdline.extend(["-c", "import sys;sys.stdout.write(sys.version)"])
    vs = None
    try:
        out = cm.cmd_run_ok(cmdline)
        diagnostic = ""
    except Exception:
        msg = ("Error while running: '%s'\n" +
               "Probably that python version is not available or wasn't correctly\n" +
               "configured in test_conf.py")
        diagnostic =  msg % " ".join(cmdline)
    if diagnostic == "":
        try:
            vs = out.split(" ")[0]
        except Exception:
            diagnostic = "Unexpected output of command '%s'\n" % " ".join(cmdline)
    return diagnostic, vs

def make_venv(path_venv, python_cmdline, asked_py):
    cmdline = list(python_cmdline)
    if asked_py.startswith("2"):
        cmdline.extend(["-m", "virtualenv", path_venv])
    else:
        cmdline.extend(["-m", "venv", path_venv])
    try:
        out = cm.cmd_run_ok(cmdline)
        diagnostic = ""
        #?
        py_cmd_venv = get_py_cmd_venv(path_venv)
    except cm.CmdExecutionError:
        msg = ("Error, venv creation failed for py_asked version: %s\n" +
               "cmdline was: %s\n")
        diagnostic = msg % (asked_py, cmdline)
        py_cmd_venv = None
    return diagnostic, py_cmd_venv

def get_py_cmd_venv(path_venv):
    return  [os.path.join(path_venv, "Scripts", "python"),]

def query_venv_python_version(py_cmd_venv):
    cmdline = py_cmd_venv + ["-c", "import sys;sys.stdout.write(sys.version)"]
    vs = None
    try:
        out = cm.cmd_run_ok(cmdline)
        diagnostic = ""
    except cm.CmdExecutionError:
        msg = ("Error while probing activated venv\n" +
               "cmdline:\n")
        diagnostic =  msg % " ".join(cmdline)
    if diagnostic == "":
        try:
            vs = out.split(" ")[0]
        except Exception:
            diagnostic = "Unexpected output of command '%s'\n" % " ".join(cmdline)
    return diagnostic, vs

def package_in_venv(py_cmd_venv, import_name):
    cmdline = py_cmd_venv + ["-c", "import %s" % import_name]
#    cmdline = ["python", "-c", "import %s" % import_name]
    try:
        cm.cmd_run_ok(cmdline)
        found = True
    except cm.CmdExecutionError:
        found = False
    return found

def pip_install_in_venv(py_cmd_venv, pip_name, logfname):
    cmdline = py_cmd_venv + ["-m", "pip", "install", pip_name]
#    cmdline = ["python", "-m", "pip", "install", pip_name]
    killed, returncode, err, out = cm.cmd_run(cmdline, timeout=120)
    if killed or returncode:
        log_header = "Error while pip_install_in_venv for package %s" % pip_name
        diagnostic = log_header + "\nSee logfile:%s" % logfname
    else:
        log_header = "Success while pip_install_in_venv for package %s" % pip_name
        diagnostic = ""
    parts = [log_header, "**stderr**", err, "**stdout**\n", out]
    text = "\n".join(parts)
    as_bytes = text.encode("utf-8")
    with open(logfname, "ab") as f:
        f.write(as_bytes)
    return diagnostic

def pip_uninstall_in_venv(py_cmd_venv, pip_name):
    cmdline = py_cmd_venv + ["-m", "pip", "uninstall", "-y", pip_name]
#    ["python", "-m", "pip", "uninstall", pip_name]
    try:
        out = cm.cmd_run_ok(cmdline)
    except cm.CmdExecutionError:
        out = ("Error in pip_uninstall_in_venv, got cm.CmdExecutionError.\n" +
               "Cmdline was: %s" % " ".join(cmdline))
    logg.out("pip_uninstall_in_venv out: " + out)
    diagnostic = ""
    return diagnostic

def pip_dev_install_in_venv(py_cmd_venv, path):
    cmdline = py_cmd_venv + ["-m", "pip", "install", "-e", path]
#    cmdline = ["python", "-m", "pip", "install", "-e", path]
    try:
        cm.cmd_run_ok(cmdline)
        diagnostic = ""
    except cm.CmdExecutionError:
        msg =  "Error while trying an install with cmdline:\n%s"
        diagnostic = msg % " ".join(cmdline)
    return diagnostic

def package_dir_in_venv(py_cmd_venv, import_name):
    prog = ("import os, sys, %s;" +
            "pkgdir = os.path.dirname(os.path.abspath(%s.__file__));" +
            "sys.stdout(pkgdir") % (import_name, import_name) 
    cmdline = py_cmd_venv + ["-c", prog]
    out = None
    try:
        out = cm.cmd_run_ok(cmdline)
        diagnostic = ""
    except cm.CmdExecutionError:
        msg = ("Error while getting a pkgdir in the venv\n" +
               "cmdline:%s\n")
        diagnostic =  msg % " ".join(cmdline)
    return diagnostic, out

def pytest_from_venv(py_cmd_venv, cwd, timeout=60):
    cmd_pytest = os.path.join(os.path.dirname(py_cmd_venv[0]), "pytest")
    cmdline = [cmd_pytest, "--cache-clear"]
    killed, returncode, err, out = cm.cmd_run(cmdline, cwd=cwd, timeout=timeout)
    cmdstr = " ".join(cmdline)
    #parts = ["Error while running cmd\n", "    " + cmdstr, "details:"]
    parts = []
    parts.append("cwd: %s" % cwd)
    parts.append("timeout: %s" % killed)
    parts.append("retcode: %s" % returncode)
    parts.append("stderr: %s" % err)
    parts.append("stdout: %s" % out)
    parts.append("------------------\n")
    text = "\n".join(parts)
    return text

ComboVersion = namedtuple("ComboVersion", "py pyglet cocos")

def ensureSnapshotSession(path_services, db, combo_version_asked):
    logg.out("info: ensureSnapshotSession starts - version asked:", combo_version_asked, flush=True)
    snp_session = SnapshotSession(combo_version_asked)
    diagnostic = snp_session.resolve(path_services)
    if diagnostic != "":
        return diagnostic, None
    logg.out("info: ensureSnapshotSession - resolve:", snp_session.resolved_py, snp_session.resolved_pyglet, snp_session.resolved_cocos, flush=True)
    c_key = snp_session.cache_key()
    if c_key in cache:
        logg.out("info: ensureSnapshotSession - session in cache", flush=True)
        session = copy.copy(cache[c_key])
        session.asked_py = snp_session.asked_py
        session.asked_pyglet = session.asked_pyglet
        session.asked_cocos = session.asked_cocos
        session.cached = True
        snp_session = session
        db.set_default_testbed(snp_session.id_string)
    else:
        logg.out("info: ensureSnapshotSession - session not in cache", flush=True)
        diagnostic = snp_session.ensure_venv(path_services)
        if diagnostic != "":
            logg.out(diagnostic)
            return diagnostic, None
        
        diagnostic = snp_session.ensure_non_dev_packages(path_services, tc.packages)
        if diagnostic != "":
            return diagnostic, None

        snp_session.install_pyglet_cocos(path_services)
        if diagnostic != "":
            return diagnostic, None

        hl.new_testbed(db, snp_session.id_string, path_services.test)
        snapshots_dir = path_services.snp_versioned(snp_session.id_string)        
        #(db, db_path, snapshots_dir, tests_dir, py_cmd=None)
        diagnostic = take_snapshots(db, path_services.db, snapshots_dir,
                                    path_services.test, py_cmd=snp_session.py_cmd_venv)

        rpt_fname = path_services.report_link(snp_session.id_string)
        text = hl.rpt_snapshot_detailed(db)
        as_bytes = text.encode("utf8")
        with open(rpt_fname, "wb") as f:
            f.write(as_bytes)
        
        black_snapshots = hl.get_full_black_pngs(snapshots_dir)

        cwd = path_services.cocos_utest
        #print("snp_session.py_cmd_venv:", snp_session.py_cmd_venv);sys.exit(1)
        pytest_link = path_services.pytest_link(snp_session.id_string)
        pytest_summary = run_unittests(snp_session.py_cmd_venv, cwd, pytest_link, timeout=60)

        snp_session.set_stats(db, len(black_snapshots), rpt_fname, pytest_summary, pytest_link)

        if diagnostic == "":
            cache[c_key] = snp_session
            save_cache()
        else:
            snp_session = None
    return diagnostic, snp_session

def fn_fname_test_py(filename):
    return filename.startswith('test_') and filename.endswith('.py')

def take_snapshots(db, db_path, snapshots_dir, tests_dir, py_cmd=None):
    """runs the test_*.py scripts in 'tests_dir', storing screenshots in
    'snapshots_dir' and error info in 'db' current testbed. The python
    provided by 'py_cmd_venv' wil be used to run each script.

    The file persisting the db is updated at each step, so more detail on
    bad conditions can be obtained by making the appropiate queries to the
    db without need to rerun slow operations
    
    db: instance of remembercases,db.TestbedEntityPropDB to store data

    db_path: full filename to store data colected

    snapshots_dir: dir where update_snapshots will store snapshots

    tests_dir: dir with the test scripts

    py_cmd: cmdline to run the desired python venv, by example
      ["venv_path/Scripts/python",]; if None the same python as the caller
    """
    logg.out("info: start taking snapshoots")
    # ensure start with no tests registered
    known, unknown = hl.get_scripts(db, 'all')
    print("known:", known)
    print("unknown:", unknown)
    
    assert len(known) == 0 and len(unknown) == 0
    
    diags = [""] 
    # add all scripts test_*.py as entities
    all_test_files = doers.files_from_dir(tests_dir, fn_fname_test_py)
    canonical_names = hl.canonical_names_from_filenames(db, all_test_files)
    hl.add_entities(db, db_path, canonical_names)
    candidates, unknowns = hl.get_scripts(db, 'all')
    if len(candidates) != len(canonical_names):
        msg = "Some scripts where unexpectly not selected to test: %s"
        diags.append(set(canonical_names) - candidates)

    # scan candidates to get info needed by update snapshots
    scripts, unknowns = hl.update_scanprops(db, db_path, candidates)

    # filter candidates to retain the ones that can be run
    candidates, unknowns = hl.get_scripts(db, 'testinfo_valid')
    assert len(unknowns)==0
    
    # do snapshots
    valid_scripts, rejected = hl.update_snapshots(db, db_path, candidates,
                                            snapshots_dir, py_cmd=py_cmd)
    diagnostics = "\n".join(diags)
    return diagnostics

def run_unittests(py_cmd_venv, cwd, logfname, timeout=60):
    """
    Will run the pytest found in the Scripts/ of the same venv as py_cmd_venv
    Writes the pytest output to file logfname, echoes to console, returns a
    summary
    
    Some utest/ tests need the cwd to be utest/
    
    cocos older than 0.6.10 needs patching so that no env var needs to be set,
    the patching is done at method SnapshotSession.install_pyglet_cocos

    Modern cocos version that do not need that patching signal it by having a
    file utest/pytest_nolegacy.txt
    """
    text = pytest_from_venv(py_cmd_venv, cwd, timeout)
    # using 'tee' would be better, but not available on Windows cmd.exe console
    # still, with execution time < 2 sec is aceptable for cocos-testcmp
    print(text)
    as_bytes = text.encode("utf8")
    with open(logfname, "wb") as f:
        f.write(as_bytes)
    s = pt.get_summary_line(text)
    return s

class SnapshotSession(object):
    def __init__(self, combo_version_asked):
        self.asked_py = combo_version_asked[0]
        self.asked_pyglet = combo_version_asked[1]
        self.asked_cocos = combo_version_asked[2]
        self.cached = False

    def cache_key(self):
        return ("snprun", self.resolved_py, self.resolved_pyglet, self.resolved_cocos)

    def __str__(self):
        fmt = "asked: %s, %s, %s - resolved: %s %s %s"
        text = fmt % (self.asked_py, self.asked_pyglet, self.asked_cocos,
                      self.resolved_py, self.resolved_pyglet, self.resolved_cocos)
        return text
    
    def resolve(self, path_services):
        diagnostic, cmd_python = get_python_cmdline(self.asked_py)
        if diagnostic != "":
            return diagnostic
        self.cmd_python = cmd_python
        diagnostic, resolved_py = query_python_version(self.cmd_python)
        if diagnostic != "":
            return diagnostic
        self.resolved_py = resolved_py
        
        try:
            gits.checkout(path_services.pyglet, self.asked_pyglet)
            self.resolved_pyglet = gits.WD_short_hash(path_services.pyglet)
        except cm.CmdExecutionError:
            msg = ("Could not checkout pyglet at version: %s" +
                   "(path to pyglet WD was '%s')\n")
            diagnostic += msg % (self.asked_pyglet, path_services.pyglet)

        try:
            gits.checkout(path_services.cocos, self.asked_cocos)
            self.resolved_cocos = gits.WD_short_hash(path_services.cocos)
        except cm.CmdExecutionError:
            msg += ("Could not checkout cocos at version: %s" +
                    "(path to cocos WD was '%s')\n")
            diagnostic += msg % (self.asked_cocos, path_services.cocos)
        if diagnostic == "":
            fmt = "py%s_p%s_C%s"
            self.id_string = fmt % (self.resolved_py, self.resolved_pyglet,
                                    self.resolved_cocos)

        return diagnostic

    #? agregar stat num scripts sacaron todas las fotos esperadas
    def set_stats(self, db, num_blacks, report_link, pytest_summary, pytest_link):
        self.stats_total_tests = db.num_entities()
        no_testinfo, _ = hl.get_scripts(db, "testinfo_missing")
        self.stats_no_testinfo = len(no_testinfo)
        self.stats_repeteables = "-"
        failures, _ = hl.get_scripts(db, "snapshots_failure")
        self.stats_failures = len(failures)

        self.stats_blacks = num_blacks
        self.report_link = report_link

        self.pytest_summary = pytest_summary
        self.pytest_link = pytest_link
        
    def ensure_venv(self, path_services):
        # ensure env exists
        path = path_services.venv(self.resolved_py)
        if not os.path.exists(path):
            logg.out("info: SnapshotSession.ensure_venv - venv do not exist; building...", flush=True)
            diagnostic, py_cmd_venv = make_venv(path, self.cmd_python, self.asked_py)
            if diagnostic != "":
                return diagnostic
            logg.out("info: SnapshotSession.ensure_venv - py_cmd_venv:", py_cmd_venv, flush=True)
            print("SnapshotSession.ensure_venv - py_cmd_venv:", py_cmd_venv)
            print("path logs:", path_services.venv_logs(self.resolved_py))
            os.mkdir(path_services.venv_logs(self.resolved_py))

            # install remembercases in the venv
            diagnostic = pip_dev_install_in_venv(py_cmd_venv, path_services.remembercases)
            if diagnostic != "":
                return diagnostic
        else:
            logg.out("info: SnapshotSession.ensure_venv - venv exist, recycling", flush=True)
            py_cmd_venv = get_py_cmd_venv(path)
        self.py_cmd_venv = py_cmd_venv

        # smoketest: 'python' version must be resolved_py
        diag = "ERROR: SnapshotSession.ensure_venv, #smoke test failed: "
        try:
            diagnostic, venv_py = query_venv_python_version(self.py_cmd_venv)
        except Exception as ex:
            diagnostic = ''.join(tb.format_exception(None, ex, ex.__traceback__))
        if diagnostic != "":
            diagnostic = diag + diagnostic
            return diagnostic
        if venv_py != self.resolved_py:
            msg = diag + "unexpected py version in venv. Expected: %s, found: %s"
            diagnostic = msg % (self.resolved_py, venv_py)
        if diagnostic != "":
            return diagnostic

        # update pip for less noise in logs; log errors but dont force bailout,
        # maybe it is only no internet
        logg.out("info: updating pip in the venv")
        cmdline = self.py_cmd_venv + ["-m", "pip", "install", "pip", "--upgrade"]
        try:
            cm.cmd_run_ok(cmdline)
        except cm.CmdExecutionError:
            msg = "SnapshotSession.ensure_venv #pip update failed for venv: %s"
            logg.out("WARN:", msg % path_services.venv(self.resolved_py), flush=True)
        diagnostic = ""
        return diagnostic

    def ensure_non_dev_packages(self, path_services, packages):
        diags = []
        for import_name, pip_name in packages.items():
            if not package_in_venv(self.py_cmd_venv, import_name):
                logfname = path_services.pip_fixed_logs(self.resolved_py, import_name)
                msg = "pip instaling package: %s; pip log in '%s'" % (pip_name, logfname)
                print(msg)
                logg.out("info:", msg, flush=True)
                diags.append(pip_install_in_venv(self.py_cmd_venv, pip_name, logfname))
        diags = [s for s in diags if s != ""]

        if diags:
            diagnostic = "\n".join(diags)
        else:
            diagnostic = ""
        return diagnostic

    def install_pyglet_cocos(self, path_services):
        diags = []
        # uninstall both
        msg = "uninstalling cocos2d in the venv"
        print(msg)
        logg.out("info: %s" % msg)
        diags.append(pip_uninstall_in_venv(self.py_cmd_venv, "cocos2d"))
        msg = "uninstalling pyglet in the venv"
        print(msg)
        logg.out("info: %s" % msg)
        diags.append(pip_uninstall_in_venv(self.py_cmd_venv, "pyglet"))

        # move versions -> was handled in .resolve

        # install pyglet
        msg = "installing pyglet in the venv"
        print(msg)
        logg.out("info: %s" % msg)
        diags.append(pip_dev_install_in_venv(self.py_cmd_venv, path_services.pyglet))

        # patch cocos to ignore pyglet restrictions
        with open("support/cocos__init__.py", "rb") as f:
            as_bytes = f.read()
        with open(path_services.cocos_init, "wb") as f:
            f.write(as_bytes)
        with open("support/cocos_setup.py", "rb") as f:
            as_bytes = f.read()
        with open(path_services.cocos_setup, "wb") as f:
            f.write(as_bytes)
        # patch cocos with the desired custom_clock (probably the latest)
        if tc.custom_clocks_checkout_str is not None:
            path = path_services.cocos_custom_clocks
            gits.checkout_file(path_services.cocos, tc.custom_clocks_checkout_str, path)
        # patch cocos/utest for old cocos versions
        pt.patch_if_needed(path_services)
        
        # install cocos
        msg = "installing cocos2d in the venv"
        print(msg)
        logg.out("info: %s" % msg)
        diags.append(pip_dev_install_in_venv(self.py_cmd_venv, path_services.cocos))

        msg = "smoketest correct cocos amd pyglet available"
        print(msg)
        logg.out("info: %s" % msg)
        # smoketest: see pyglet and cocos can be imported, see they come
        # from the expected dir
        ## pyglet
        if not package_in_venv(self.py_cmd_venv, "pyglet"):
            diags.append("Error, pyglet can not be imported in the venv")
        else:
            d, pkgdir = package_dir_in_venv(self.py_cmd_venv, "pyglet")
            if d != "":
                diags.append(d)
            else:
                if pkgdir != path_services.pyglet:
                    fmt = ("Error, expecting pyglet in the venv point to '%s'," +
                           "found it points to '%s'")
                    msg = fmt % (path_services.pyglet, pkgdir)
                    diags.append(msg)
        ## cocos
        if not package_in_venv(self.py_cmd_venv, "cocos"):
            diags.append("Error, cocos can not be imported in the venv")
        else:
            d, pkgdir = package_dir_in_venv(self.py_cmd_venv, "cocos")
            if d != "":
                diags.append(d)
            else:
                if pkgdir != path_services.cocos:
                    fmt = ("Error, expecting cocos in the venv point to '%s'," +
                           "found it points to '%s'")
                    msg = fmt % (path_services.cocos, pkgdir)
                    diags.append(msg)
                else:
                    # also verify is patched
                    # patched cocos setup.py in place?
                    diag = ""
                    path = os.path.abspath(os.path.join(pkgdir, "../setup.py"))
                    try:
                        with open(path, "rb") as f:
                            as_bytes = f.read()
                    except Exception:
                        diag = "Error, could not read file: %s" % path
                        diags.append(diag)        
                    if  diag=="" and "cocos-testcmp-mark" not in as_bytes.decode("utf8"):
                        diags.append("Error, cocos setup.py not patched.")                              

                    # patched cocos __init__.py in place?
                    diag = ""
                    path = os.path.join(pkgdir, "__init__.py")
                    try:
                        with open(path, "rb") as f:
                            as_bytes = f.read()
                    except Exception:
                        diag = "Error, could not read file: %s" % path
                        diags.append(diag)        
                    if diag=="" and "cocos-testcmp-mark" not in as_bytes.decode("utf8"):
                        diags.append("Error, cocos __init__.py not patched.")

        diags = [s for s in diags if s!= "" ]
        if diags:
            diagnostic = "\n".join(diags)
        else:
            diagnostic = ""
        return diagnostic

def delta_snapshots(path_services, cmp_ordinal, db, testbed_1, testbed_2):
    scripts_with_non_matching_snapshots = {}
    scripts1, unknown = hl.get_scripts(db, 'snapshots_success', None, testbed_1)
    snapshots_path1 = path_services.snp_versioned(testbed_1)
    scripts2, unknown = hl.get_scripts(db, 'snapshots_success', None, testbed_2)
    snapshots_path2 = path_services.snp_versioned(testbed_2)
    comparables = scripts1 & scripts2
    #print("delta_snapshots - comparables:", comparables)
    for script in comparables:
        expected_snapshots = db.get_prop_value(script, 'expected_snapshots')
        differents = []
##        if script == "test_accel_amplitude.py":
##            print("delta_snapshots - script 'test_accel_amplitude.py' found")
##        else:
##            continue
        for name in expected_snapshots:
            p1 = os.path.join(snapshots_path1, name)
            p2 = os.path.join(snapshots_path2, name)
            delta_1 = path_services.cmp_diff_bw(name, cmp_ordinal)
            delta_2 = path_services.cmp_diff_scale(name, cmp_ordinal)
#            print("p1 %s\n, p2%s\n, d1%s\n, d2:%s\n" % (p1, p2, delta_1, delta_2))
            equal, comparables = ri.cmp_and_diff_proportional(p1, p2, delta_1, delta_2)
#            print("equal, comparables:", equal, comparables)
            if not equal:
                if not comparables:
                    delta_1, delta_2 = None, None
                differents.append((name, delta_1, delta_2))
        if len(differents):
            scripts_with_non_matching_snapshots[script] = differents
#    print("delta_snapshots - len(scripts_with_non_matching_snapshots)", len(scripts_with_non_matching_snapshots))
    return scripts_with_non_matching_snapshots

class Cmp(object):
    def __init__(self, v_ref, v_other, ordinal):
        self.v_ref = v_ref
        self.v_other = v_other
        self.ordinal = ordinal
        self.cached = False

    #? agregar num tests que tomaron todos los snapshots en ambas versiones
    def compare(self, path_services, db):
        self.scripts_with_non_matchig_snapshots = None
        os.mkdir(path_services.cmp_deltas(self.ordinal))
        res = delta_snapshots(path_services, self.ordinal, db, self.v_ref.id_string, self.v_other.id_string)
        self.scripts_with_non_matchig_snapshots = res
        
def ensure_cmp(path_services, db, conf_v_ref, conf_v_other):
    cmp = None
    diagnostic, ref_session = ensureSnapshotSession(path_services, db, conf_v_ref)
#    print("ref_session - version, diagnostic:", conf_v_ref, diagnostic)
    if diagnostic != "":
        return diagnostic, cmp

    diagnostic, other_session = ensureSnapshotSession(path_services, db, conf_v_other)
#    print("other_session - version, diagnostic:", conf_v_other, diagnostic)
    if diagnostic != "":
        return diagnostic, cmp
#    print("In cmp - testbeds:", db.db.keys())
    key_ref = ref_session.cache_key()
    key_other = other_session.cache_key()
    cmp_key = ("cmp", key_ref, key_other)
    if cmp_key in cache:
        logg.out("info: ensure_cmp - cmp in cache", flush=True)
        cmp = copy.copy(cache[cmp_key])
        cmp.cached = True
    else:
        logg.out("info: ensure_cmp - cmp not in cache, building...", flush=True)
        cmp = Cmp(ref_session, other_session, cache["cmp_ord"])
        cmp.compare(path_services, db)
        cache[cmp_key] = cmp
        cache["cmp_ord"] += 1
        symetric_key = ("cmp", key_other, key_ref)
        cache[symetric_key] = cmp
        save_cache()
    return diagnostic, cmp

def rpt_cmp(path_services, cmp):
    # prepare delta snapshpts section
    reldir_snp_ref = path_services.snp_versioned_relative(cmp.v_ref.id_string)
    reldir_snp_other = path_services.snp_versioned_relative(cmp.v_other.id_string)
    snp_by_scripts = cmp.scripts_with_non_matchig_snapshots
    section_cmp_snp_diff = templates.render_delta(snp_by_scripts, reldir_snp_ref, reldir_snp_other)

    # calc symbols values
    glo = {"cmp": cmp, "section_cmp_snp_diff": section_cmp_snp_diff}
    symbols = {s: six.text_type(eval(s, glo)) for s in templates.known_symbols}
    print("***repr symbols:")
    for s in symbols:
        if s != "section_cmp_snp_diff":
            print(s, repr(symbols[s]))
            k = str(s)
    # render template
    in_ = os.path.join(path_services.support, "template_cmp_report.htm")
    out = path_services.cmp_report(cmp.ordinal)
    templates.render_template_to_file(in_, out, symbols)
    
class Logg(object):
    def __init__(self, fname):
        self.fname = fname
        self.f = open(fname, "wb")

    def close(self):
        self.f.close()

    def out(self, *args, flush=False):
        text = " ".join([six.text_type(e) for e in args])
        text = text + "\n"
        as_bytes = text.encode("utf8")
        self.f.write(as_bytes)
        if flush:
            self.f.flush()

def compare(path_services):
    global logg, cache, cache_path
    db = hl.ensure_db(path_services.db)
    logg.out("info: db initial load - testbeds:", "%s" % db.db.keys())
    diagnostic, cmp = ensure_cmp(path_services, db, tc.v_ref, tc.v_other)
    msg = diagnostic if diagnostic != "" else "info: cmp completed"
    logg.out(msg)    
    print(msg)
    if diagnostic == "":
        rpt_cmp(path_services, cmp)

def main(task, extra):
    global logg, cache, cache_path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path_services = fs.PathServices(base_dir)
    logg = Logg(path_services.log)
    ## cache stores
    ##  - with key "cmp_ord": ordinal next comparison
    ##  - with key ("cmp", v_ref_resolved, v_other_resolved): Cmp instamce
    ##  - with key ("snprun", combo_version_resolved) -> instance SnapshotSession
    logg.out("Session starts -----------------------------------------------------")
    cache = {"cmp_ord": 0}
    cache_path = path_services.cache
    if os.path.exists(cache_path):
        cache = load_pickle(cache_path)
    logg.out("info:", cache_str())

    if task == "del_all_cmp":
        # del all 'cmp'
        to_del = [key for key in cache if isinstance(key, tuple) and key[0]=="cmp"]
        for key in to_del:
            path = path_services.cmp_deltas(cache[key].ordinal)
            if os.path.isdir(path):
                shutil.rmtree(path)
            del cache[key]
            #? faltaria borrar el xx.html

        cache["cmp_ord"] = 0
        save_cache()
        print("ok, deleted all cmp")

    elif task == "del_last_cmp":
        # del last cmp
        ordinal = cache["cmp_ord"]
        if ordinal > 0:
            ordinal -= 1
            cache["cmp_ord"] = ordinal
            path = path_services.cmp_deltas(ordinal)
            if os.path.isdir(path):
                shutil.rmtree(path)
            to_del = None
            for key in cache:
                if (isinstance(key, tuple) and key[0]=="cmp"
                    and cache[key].ordinal == ordinal):
                    to_del = key
                    break
            if to_del is not None:
                key = to_del
                del cache[key]
                symetric_key = ("cmp", key[2], key[1])
                del cache[symetric_key]
                save_cache()
                #? faltaria borrar el xx.html

        print("ok, deleted last cmp")

    elif task == "compare":
        compare(path_services)

    elif task == "dump_cache":
        print(cache_str())

    elif task == "del_snp":
        pass

    elif task == "usage":
        usage()

def cache_str():
    global logg, cache, cache_path
    lines = ["Cache contents"]
    lines.append("cmp_ord: %d" % cache["cmp_ord"])
    keys_cmp = sorted([k for k in cache if isinstance(k, tuple) and k[0] == "cmp"])
    for k in keys_cmp:
        fmt = "%d %s %s" 
        lines.append(fmt % (cache[k].ordinal, k, cache[k]))
    keys_snprun = sorted([k for k in cache if isinstance(k, tuple) and k[0] == "snprun"])
    for k in keys_snprun:
        lines.append("%s %s" % (k, cache[k]))
    text = "\n".join(lines)
    return text

def usage():
    text = __doc__.replace("do_test.py", os.path.basename(__file__))
    print(text)
    
if __name__ == "__main__":
    task = "usage"
    extra = None
    if len(sys.argv) == 1:
        task = "compare"
    elif len(sys.argv) == 2:
        if sys.argv[1] == "--del-last-cmp":
            task = "del_last_cmp"
        elif sys.argv[1] == "--del-all-cmp":
            task = "del_all_cmp"
        elif sys.argv[1] == "--dump-cache":
            task = "dump_cache"
    elif len(sys.argv) == 3:
        if sys.argv[1] == "--del-snp":
            task = "del_snp"
            extra = sys.argv[2]
    main(task, extra)
