# -*- coding: utf-8 -*-
"""Path building for entities should be delegated to fs.PathServices

base :
  src : extra modules supporting test
  work : all files written will live here
    remembercases : remembercases clone
    pyglet : pyglet clone
    cocos : cocos clone
    pys : python venvs, each child a venv named "pyX.Y"
    snp : snapshoots, each child named '<canonical version>'
"""
import os

class PathServices(object):
    def __init__(self, base_path):
        self.base = base_path
        self.support = os.path.join(self.base, "support")
        self.ref = os.path.join(self.base, "ref")
        self.work = os.path.join(self.base, "work")
        self.log = os.path.join(self.work, "do_test.log")
        self.pys = os.path.join(self.work, "pys")
        self.snp = os.path.join(self.work, "snp")
        self.test = os.path.join(self.work, "test")
        self.remembercases = os.path.join(self.work, "remembercases")
        self.pyglet = os.path.join(self.work, "pyglet")
        self.cocos = os.path.join(self.work, "cocos")
        self.cocos_setup = os.path.join(self.cocos, "setup.py")
        self.cocos_init = os.path.join(self.cocos, "cocos", "__init__.py")
        self.cocos_director = os.path.join(self.cocos, "cocos", "director.py")
        self.cocos_custom_clocks = os.path.join(self.cocos, "cocos", "custom_clocks.py")
        self.cocos_test = os.path.join(self.cocos, "test")
        self.cocos_utest = os.path.join(self.cocos, "utest")
        self.pytest_nolegacy = os.path.join(self.cocos_utest, "pytest_nolegacy.txt")
        self.cache = os.path.join(self.work, "cache.pkl")
        self.db = os.path.join(self.work, "db.pkl")
        self.cmp = os.path.join(self.work, "cmp")

    def venv(self, py_version):
        return os.path.join(self.pys, py_version)

    def venv_logs(self, py_version):
        return os.path.join(self.venv(py_version), "logs")

    def pip_fixed_logs(self, py_version, libname):
        return os.path.join(self.venv_logs(py_version), libname + ".txt")

    def snp_versioned(self, version_string):
        return os.path.join(self.snp, version_string)

    def snp_versioned_relative(self, version_string):
        dir_snp = self.snp_versioned(version_string)
        relative = os.path.relpath(dir_snp, self.work)
        return relative

    def report_link(self, version_string):
        short = "_rpt_%s.txt" % version_string
        return os.path.join(self.snp_versioned(version_string), short)

    def pytest_link(self, version_string):
        short = "_rpt_pytest_%s.txt" % version_string
        return os.path.join(self.snp_versioned(version_string), short)

    def cmp_report(self, ordinal):
        return os.path.join(self.work, "%02d_cmp_report.htm" % ordinal)

    def cmp_deltas(self, ordinal):
        return os.path.join(self.cmp, "%02d" % ordinal)

    def cmp_diff_bw(self, snp, ordinal):
        i = snp.rfind(".")
        s = snp[:i] + ".diff_bw" + snp[i:]
        return os.path.join(self.cmp_deltas(ordinal), s)

    def cmp_diff_scale(self, snp, ordinal):
        i = snp.rfind(".")
        s = snp[:i] + ".diff_scale" + snp[i:]
        return os.path.join(self.cmp_deltas(ordinal), s)
