#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by wswenyue on 2019/6/29.
import sys
import traceback

import color_print

TAG = "AKLog::"


def log(msg):
    color_print.green(TAG + str(msg))


def log_err(msg):
    color_print.red(">>>>>>>>>>>>>>>>>>>>Error Begin>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    color_print.red(TAG + str(msg))
    traceback.print_stack(file=sys.stdout)
    color_print.red("<<<<<<<<<<<<<<<<<<<<Error End<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
