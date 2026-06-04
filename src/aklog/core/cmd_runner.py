#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import subprocess

from aklog.core import comm_tools


def _popen_kwargs(extra=None):
    kwargs = {}
    if extra:
        kwargs.update(extra)
    if comm_tools.is_py3():
        if "universal_newlines" in kwargs and "text" not in kwargs:
            kwargs["text"] = kwargs.pop("universal_newlines")
    else:
        if "text" in kwargs:
            kwargs["universal_newlines"] = kwargs.pop("text")
    return kwargs


def run(argv, check=True, **kwargs):
    popen_kw = _popen_kwargs(kwargs)
    if comm_tools.is_py3():
        return subprocess.run(argv, check=check, **popen_kw)
    proc = subprocess.Popen(
        argv, stdout=popen_kw.get("stdout"), stderr=popen_kw.get("stderr"), stdin=popen_kw.get("stdin")
    )
    out, _err = proc.communicate()
    if check and proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, argv, output=out)
    return proc


def run_shell(script, check=True, **kwargs):
    popen_kw = _popen_kwargs(kwargs)
    if comm_tools.is_py3():
        return subprocess.run(script, shell=True, check=check, **popen_kw)
    proc = subprocess.Popen(script, shell=True, stdout=popen_kw.get("stdout"), stderr=popen_kw.get("stderr"))
    out, _err = proc.communicate()
    if check and proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, script, output=out)
    return proc


def popen(argv, **kwargs):
    popen_kw = _popen_kwargs(kwargs)
    return subprocess.Popen(argv, **popen_kw)


def iter_lines(argv):
    proc = popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    try:
        for line in iter(proc.stdout.readline, ""):
            yield comm_tools.get_str(line)
    finally:
        if proc.stdout:
            proc.stdout.close()
    rc = proc.wait()
    if rc:
        raise subprocess.CalledProcessError(rc, argv)


def check_output(argv):
    if comm_tools.is_py3():
        out = subprocess.check_output(argv, stderr=subprocess.PIPE)
    else:
        proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = proc.communicate()
        if proc.returncode:
            raise subprocess.CalledProcessError(proc.returncode, argv, output=out)
    return comm_tools.get_str(out)
