#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by wswenyue on 2019/6/29.
import sys
import traceback

from aklog.core.console import print_error, print_green

TAG = "AKLog::"


def log(msg):
    print_green(TAG + str(msg))


def log_err(msg):
    print_error(">>>>>>>>>>>>>>>>>>>>Error Begin>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print_error(TAG + str(msg))
    traceback.print_stack(file=sys.stdout)
    print_error("<<<<<<<<<<<<<<<<<<<<Error End<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
