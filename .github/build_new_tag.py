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


v_prefix = os.getenv('VERSION_PREFIX')
v_major_minor = os.getenv('VERSION_MAJOR_MINOR')
print(f"v_prefix:{v_prefix}")
print(f"v_major_minor:{v_major_minor}")
# Get the path of the runner file
v_revision_old = cmd_run(
    f"git tag --list '{v_prefix}{v_major_minor}.*' --sort=-version:refname | head -n 1 | grep -oE '[0-9]+$'")
v_revision = 0
if is_empty(v_revision_old):
    print("v_revision_old empty!!!")
    v_revision = 0
else:
    v_revision = int(v_revision_old.strip()) + 1
new_tag = f"{v_prefix}{v_major_minor}.{v_revision}"
print(f"newTag:{new_tag}")
add_env("NEW_TAG", new_tag)
sys.exit(0)
