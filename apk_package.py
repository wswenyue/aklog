#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by zhangwanxin on 2019/6/9.
import time

import comm_tools
from comm_tools import cmd_run_iter, is_not_empty


class ApkProcess(object):
    _name = None  # "bangjob"
    _pn = None  # "com.wuba.bangjob"
    _pid = None
    _tag = None
    _children = {}

    def __init__(self, name=None):
        self._name = name

    def __add_child(self, c_pn, c_pid):
        child = ApkProcess(c_pn)
        child._pid = c_pid
        child._pn = c_pn
        child._tag = "[" + self.__get_last_name() + str(c_pn).replace(self.get_name(), "") + "]"
        self._children[c_pid] = child

    def get_pid(self):
        return self._pid

    def get_tag(self):
        return self._tag

    def get_name(self):
        if is_not_empty(self._pn):
            return self._pn
        return self._name

    def __get_last_name(self):
        if "." in self._pn:
            return self._pn[self._pn.rfind(".") + 1:]
        else:
            return self._pn

    def is_apk(self, pid):
        if self._pid == pid:
            return True
        if pid in self._children.keys():
            return True
        return False

    def get_cur_tag(self, pid):
        if self._pid == pid:
            return self._tag
        c = self._children[pid]
        if c:
            return c.get_tag()
        return None

    def update(self):
        cur_pid = ApkProcess.__git_name_pid(self._name)
        if not cur_pid or len(cur_pid) <= 0:
            return None
        _pn = list(cur_pid.keys())[0]
        self._pn = str(_pn).strip().split(":")[0]
        self._pid = cur_pid.pop(self._pn)
        self._tag = "[" + self.__get_last_name() + "@]"
        for c_pn, c_id in cur_pid.items():
            self.__add_child(c_pn, c_id)

    @staticmethod
    def get_cur_apk():
        name = ApkProcess.__cur_package_name()
        if name:
            apk = ApkProcess(name)
            apk.update()
            return apk
        return None

    @staticmethod
    def __git_name_pid(package_name):
        '''
        匹配指定包对应的pid信息
        :param package_name:
        :return: {'com.wuba.bangjob': '20628', 'com.wuba.bangjob:pushservice': '20546'}
        '''
        pid_map = {}
        for line in cmd_run_iter("adb shell ps"):
            line = line.strip()
            if package_name in line:
                ls = line.split()
                pid_map[ls[-1]] = ls[1]
        return pid_map

    @staticmethod
    def __cur_package_name():
        try:
            for line in cmd_run_iter("adb shell dumpsys window windows | grep -E 'mFocusedApp'"):
                line = line.strip()
                if line.startswith("mFocusedApp="):
                    pn = line.split()[4].split("/")[0]
                    return pn
        except Exception:
            print("__cur_package_name fetch Error")
        return None


try:
    from synchronize import make_synchronized
except ImportError:
    def make_synchronized(func):
        import threading
        func.__lock__ = threading.Lock()

        def synced_func(*args, **kws):
            with func.__lock__:
                return func(*args, **kws)

        return synced_func


class ProcessData(object):
    instance = None
    is_cur = False
    target_pn = None
    target_apk = None

    @make_synchronized
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls, *args, **kwargs)
        return cls.instance

    def get_apk_info(self):
        return self.target_apk

    def __fetch(self):
        print("apk info fetch...")
        if self.is_cur:
            apk = ApkProcess.get_cur_apk()
            if not apk:
                return
            if not self.target_apk or self.target_apk.get_pid() != apk.get_pid():
                print("--->current apk===>pid:{0};pn:{1};".format(apk.get_pid(), apk.get_name()))
            self.target_apk = apk

        if self.target_pn:
            apk = ApkProcess(self.target_pn)
            apk.update()
            if not self.target_apk or self.target_apk.get_pid() != apk.get_pid():
                print("--->target apk===>pid:{0};pn:{1};".format(apk.get_pid(), apk.get_name()))
            self.target_apk = apk

    def start(self, cur=False, pn=None):
        self.is_cur = cur
        self.target_pn = pn
        comm_tools.new_thread(ProcessData.__run, ("Thread-FetchAPKInfo", 5))

    @staticmethod
    def __run(t_name, delay):
        while True:
            ProcessData().__fetch()
            time.sleep(delay)
