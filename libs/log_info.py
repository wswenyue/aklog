#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by zhangwanxin on 2018/11/4.
import re

import color_print
import comm_tools


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
    progress_id = None

    def __init__(self, log_filter=None, filter_ignorecase=False, filter_exact=False, progress_id=None):
        print("filter={0};ignore={1};exact={2};progress={3}".format(log_filter, filter_ignorecase, filter_exact,
                                                                    progress_id))
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
        self.progress_id = progress_id

    def parser(self, msg):
        if comm_tools.is_empty(msg):
            return
        group = self.parser_head(msg.strip())
        if group:
            if self.log:
                self.print_log()
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
                print ">>>>" + msg

    def print_log(self):
        log = self.log
        if log:
            open_log = True
            if self.PATTERN_FILTER:
                if self.PATTERN_FILTER.match(log.tag):
                    open_log = True
                else:
                    open_log = False

            if open_log:
                msg = "{0}#{1}#{2}#{3}#{4}#{5}".format(log.time, log.pid, log.tid, log.priority, log.tag,
                                                       log.get_msg())
                if log.priority == 'D':
                    color_print.green(msg)
                elif log.priority == 'E':
                    color_print.red(msg)
                elif log.priority == 'W':
                    color_print.yellow(msg)
                elif log.priority == 'I':
                    color_print.light_blue(msg)
                else:
                    print (msg)

        self.log = None

    def parser_head(self, msg):
        match = self.PATTERN_HEAD.match(msg)
        if match:
            return match.groups()
        else:
            return None
