#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by zhangwanxin on 2018/11/4.
import re

import color_print
import comm_tools
from apk_package import ProcessData


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

    def __init__(self, log_filter=None, filter_ignorecase=False,
                 filter_exact=False, pn=None, log_all=False):
        print("cur packageName-->" + str(pn))
        print("all log ==>" + str(log_all))
        print("filter={0};ignore={1};exact={2}".format(
            log_filter, filter_ignorecase, filter_exact))

        self.init_filter(log_filter, filter_exact, filter_ignorecase)

        is_print_cur = False
        target_pn = None

        if not log_all:
            if comm_tools.is_not_empty(pn):
                target_pn = pn
            else:
                is_print_cur = True

        ProcessData().start(cur=is_print_cur, pn=target_pn)

    def get_apk_info(self):
        return ProcessData().get_apk_info()

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
        apk = self.get_apk_info()
        if apk:
            # print("--->apk===>pid:{0};pn:{1};".format(apk.get_pid(), apk.get_name()))
            if not apk.is_apk(log_msg.pid):
                return False

        if self.PATTERN_FILTER:
            if not self.PATTERN_FILTER.match(log_msg.tag):
                return False

        return True

    def _log_print(self, log_msg):
        apk = self.get_apk_info()
        pid = None
        if apk:
            pid = apk.get_cur_tag(log_msg.pid)
        if comm_tools.is_empty(pid):
            pid = log_msg.pid

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
