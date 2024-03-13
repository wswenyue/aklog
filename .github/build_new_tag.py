#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by wswenyue on 2024-03-13 14:29:20.
# Description: a python script
import os
import subprocess
import sys


def get_str(obj) -> str:
    if type(obj) is str:
        return obj
    elif type(obj) is bytes:
        return bytes.decode(obj, encoding="utf-8", errors="ignore")
        # return obj.decode("utf-8")
    else:
        return str(obj)


def add_env(key: str, value):
    env_file = os.getenv('GITHUB_ENV')
    # write to the file
    with open(env_file, "a") as env_file:
        env_file.write(f"{key}={value}")


def cmd_run(cmd: str) -> str:
    _cmd = str(cmd).split()
    output = subprocess.check_output(_cmd)
    return get_str(output)


def cmd_run_iter(cmd: str):
    _cmd = str(cmd).split()
    popen = subprocess.Popen(_cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield get_str(stdout_line)
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, _cmd)


def is_empty(obj):
    if obj is None:
        return True
    if not obj:
        return True
    if type(obj) is str:
        if obj == "":
            return True
        elif obj.strip() == "":
            return True
        else:
            return False
    if type(obj) is list:
        if len(obj) <= 0:
            return True
        else:
            return False
    if type(obj) is dict:
        return bool(obj)
    else:
        return False


def is_not_empty(obj):
    return not is_empty(obj)


def next_revision_num(version_pre: str) -> int:
    _max = -1
    for line in cmd_run_iter("git ls-remote --tags -q"):
        if is_empty(line):
            continue
        if version_pre not in line:
            continue
        code = int(line.rsplit('.', 1)[-1])
        print(f"code:{code}")
        if _max < code:
            _max = code
    return _max + 1


v_prefix = os.getenv('VERSION_PREFIX')
v_major_minor = os.getenv('VERSION_MAJOR_MINOR')
print(f"v_prefix:{v_prefix}")
print(f"v_major_minor:{v_major_minor}")
v_revision = next_revision_num(f"{v_prefix}{v_major_minor}.")
new_tag = f"{v_prefix}{v_major_minor}.{v_revision}"
print(f"newTag:{new_tag}")
add_env("NEW_TAG", new_tag)
sys.exit(0)
