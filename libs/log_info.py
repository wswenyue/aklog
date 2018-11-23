#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by zhangwanxin on 2018/11/4.
import re

from libs import comm_tools, color_print


class LogInfo(object):
    date = None
    time = None
    pid = None
    tid = None
    priority = None
    tag = None
    msg = None

    def get_msg(self):
        _msg = ""
        if self.msg:
            for index, line in enumerate(self.msg):
                if index == 0:
                    _msg += line
                else:
                    _msg += ("\n\t\t" + line)
        return _msg


class LogMsgParser(object):
    # [ <datetime> <pid>:<tid> <priority>/<tag> ]
    # [ 08-28 22:39:39.974  1785: 1832 D/HeadsetStateMachine ]
    REGEX_LOG_HEAD = r"^\[\s*(\d{2}-\d{2})\s*(\d{2}:\d{2}:\d{2}.\d+)\s*(\d+):\s*(\d+)\s*([I|D|E|V|W])/(.*)\]$"
    PATTERN_HEAD = re.compile(REGEX_LOG_HEAD)
    PATTERN_FILTER = None
    log = None
    pids = {}  # {'com.wuba.bangjob': '20628', 'com.wuba.bangjob:pushservice': '20546'}

    def __init__(self, log_filter=None, filter_ignorecase=False,
                 filter_exact=False, pn=None, pids=None):
        print("cur packageName-->" + pn)
        print("pids==>" + str(pids))
        print("filter={0};ignore={1};exact={2}".format(
            log_filter, filter_ignorecase, filter_exact))
        self.init_filter(log_filter, filter_exact, filter_ignorecase)
        self.init_pids(pids, pn)

    def init_filter(self, log_filter, filter_exact, filter_ignorecase):
        if comm_tools.is_not_empty(log_filter):
            if filter_exact:
                re_filter = log_filter
            else:
                re_filter = ".*(" + log_filter + ").*"
            if filter_ignorecase:
                self.PATTERN_FILTER = re.compile(re_filter, re.IGNORECASE)
            else:
                self.PATTERN_FILTER = re.compile(re_filter)
        else:
            self.PATTERN_FILTER = None

    def init_pids(self, pids, pn):
        if pids:
            for package, pid in pids.items():
                if package == pn:
                    self.pids[pid] = "main"
                else:
                    self.pids[pid] = str(package).replace(pn, "")

    def parser(self, msg):
        if comm_tools.is_empty(msg):
            return
        group = self.parser_head(msg)
        if group:
            if self.log:
                self.print_logic()
            self.log = LogInfo()
            self.log.date = group[0]
            self.log.time = group[1]
            self.log.pid = group[2]
            self.log.tid = group[3]
            self.log.priority = group[4]
            self.log.tag = group[5]
        else:
            if self.log:
                if not self.log.msg:
                    self.log.msg = []
                self.log.msg.append(msg)
            else:
                print(">>>>" + str(msg))

    def print_logic(self):
        log = self.log
        if self.is_print_log(log):
            self._log_print(log)
        self.log = None

    def is_print_log(self, log_msg):
        if log_msg.pid not in self.pids.keys():
            return False

        if self.PATTERN_FILTER:
            if not self.PATTERN_FILTER.match(log_msg.tag):
                return False

        return True

    def _log_print(self, log_msg):
        pid = self.pids.get(log_msg.pid, log_msg.pid)
        msg = "{0}#{1}#{2}#{3}#{4}#{5}".format(log_msg.time, pid,
                                               log_msg.tid, log_msg.priority, log_msg.tag,
                                               log_msg.get_msg())
        if log_msg.priority == 'D':
            color_print.green(msg)
        elif log_msg.priority == 'E':
            color_print.red(msg)
        elif log_msg.priority == 'W':
            color_print.yellow(msg)
        elif log_msg.priority == 'I':
            color_print.light_blue(msg)
        else:
            print(msg)

    def parser_head(self, msg):
        match = self.PATTERN_HEAD.match(msg)
        if match:
            return match.groups()
        else:
            return None
