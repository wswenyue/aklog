#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by wswenyue on 2018/11/4.
import errno
import fnmatch
import os
import platform
import shutil
import subprocess
import sys

import threading
from typing import Tuple, Iterable, List, Optional


def is_empty(obj):
    if obj is None:
        return True
    if not obj:
        return True
    if type(obj) is str:
        if obj == "":
            return True
        elif obj == "None":
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


def get_str(obj) -> str:
    if type(obj) is str:
        return obj
    elif type(obj) is bytes:
        return bytes.decode(obj, encoding="utf-8", errors="ignore")
        # return obj.decode("utf-8")
    else:
        return str(obj)


def to_str(obj) -> str:
    return get_str(obj)


def to_int(obj) -> int:
    if type(obj) is int:
        return obj
    else:
        return int(obj)


def get_iterable(obj) -> Iterable:
    return iter(obj)


def cmd_run_iter(cmd):
    _cmd = str(cmd).split()
    popen = subprocess.Popen(_cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield get_str(stdout_line)
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, _cmd)


def cmd_run(cmd):
    _cmd = str(cmd).split()
    output = subprocess.check_output(_cmd)
    return get_str(output)


def new_thread(f, name: str = None, args: Tuple = ()):
    t = threading.Thread(target=f, args=args)
    t.setDaemon(True)
    if name:
        t.name = name
    t.start()


def is_py3():
    return sys.version_info[0] == 3


def is_windows_os() -> bool:
    # The output of platform.system() is as follows:
    # Linux: Linux
    # Mac: Darwin
    # Windows: Windows
    return platform.system() == "Windows"


def is_mac_os() -> bool:
    # The output of platform.system() is as follows:
    # Linux: Linux
    # Mac: Darwin
    # Windows: Windows
    return platform.system() == "Darwin"


def get_user_home_dir() -> str:
    if is_windows_os():
        return os.path.join(os.environ['USERPROFILE'])
    else:
        return os.path.join(os.path.expanduser('~'))


def get_user_desktop_dir(file_name: str = None) -> str:
    if file_name:
        return os.path.join(os.path.join(get_user_home_dir(), 'Desktop'), file_name)
    else:
        return os.path.join(get_user_home_dir(), 'Desktop')


def create_dir_not_exists(path):
    if os.path.exists(path) and os.path.isdir(path):
        # print(f"{path} already exists!!!")
        return
    try:
        # print(f"create_dir_not_exists-path->{path}")
        dir_path = os.path.dirname(path)
        # print(f"create_dir_not_exists-dir_path->{dir_path}")
        os.makedirs(dir_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise exception


def is_exe(fpath: str) -> bool:
    """
    check file path is executable file
    :param fpath:
    :return:
    """
    if not fpath:
        return False
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def match_str(a: str, b: str, is_exact: bool = True, is_ignore_case: bool = False) -> bool:
    """
    a str match b str
    :param a:
    :param b:
    :param is_exact: 精准匹配
    :param is_ignore_case: 忽略大小写
    :return: true:matched
    """
    if is_empty(a) or is_empty(b):
        return False
    if is_exact:
        if is_ignore_case:
            return a.lower() == b.lower()
        else:
            return a == b
    else:
        if is_ignore_case:
            return a.lower() in b.lower()
        else:
            return a in b


def read_file_line_iter(file_path):
    with open(file_path) as fp:
        if not fp:
            return None
        for line in fp:
            yield line


def read_file_lines(file_path):
    with open(file_path) as fp:
        if fp:
            return fp.readlines()
        return None


def write_to_file_no_error(str_data, file_path):
    create_dir_not_exists(file_path)
    write_to_file(str_data, file_path)


def write_to_file_iterable(obj, file_path):
    if is_file_exists(file_path):
        print("the file %s exists!!!" % file_path)
        return
    create_dir_not_exists(file_path)
    if not isinstance(obj, Iterable):
        return
    with open(file_path, "w") as f:
        if f:
            for line in obj:
                f.write(line + "\n")


def __write_to_file(name, msg, mode=None):
    with open(name, mode) as f:
        f.write(msg)


def write_to_file(str_data, file_path):
    """
    写文件
    :param str_data:
    :param file_path:
    :return:
    """
    __write_to_file(file_path, str_data, 'w')


def write_to_file_add(str_data, file_path):
    """
    写文件，以追加的形式
    :param str_data:
    :param file_path:
    :return:
    """
    __write_to_file(file_path, str_data, 'a')


def create_file_not_exists(path):
    """
    Create a file regardless of  the father dir not exists
    :param path:
    :return:
    """
    if os.path.exists(path):
        return
    dir_path = os.path.dirname(path)
    create_dir_not_exists(dir_path)
    open(path, "w").close()


def is_file_exists(path):
    """
    the file path exists and the file is a file not dir
    :param path:
    :return:
    """
    return os.path.isfile(path)


def is_dir_exists(path):
    """
    check dir exists
    :param path:
    :return:
    """
    return os.path.isdir(path)


def remove_file(path):
    """
    remove this file
    :param path: file path
    :return:
    """
    if not os.path.exists(path):
        return
    if os.path.isfile(path):
        os.remove(path)  # remove the file
    elif os.path.isdir(path):
        shutil.rmtree(path)  # remove dir and all contains


def get_cur_path(file_name):
    return os.getcwd() + os.sep + file_name


def get_path_dir(path):
    _dir = os.path.dirname(path)
    if _dir[len(_dir) - 1] != os.sep:
        _dir += os.sep
    return _dir


def get_path_file_name(path):
    return os.path.basename(path)


def get_file_extension(file_path):
    """
    获取文件的扩展名
    :param file_path: 文件名或者文件路径
    :return:扩展名 eg:tar.gz;zip;9.png;png ...
    """
    base_name = os.path.basename(file_path)
    print(base_name)
    return base_name[base_name.index(".") + 1:]


def find_files(target_path_pattern, path) -> List[str]:
    """
    给定搜索 target_path_pattern 正则，在指定的path路径下搜索匹配文件
    find("/sdk/*/openharmony/toolchains/hdc*", environ["HARMONY_HOME"])
    """
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(os.path.join(root, name).replace(path, ""), target_path_pattern):
                result.append(to_str(os.path.join(root, name)))
    return result


def find_file(target_path_pattern, path) -> Optional[str]:
    ret = find_files(target_path_pattern, path)
    if len(ret) == 0:
        return None
    return ret[0]
