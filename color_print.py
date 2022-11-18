#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by zhangwanxin on 2018/11/4.

"""
同时设置背景和前景
print("\033[95;46m {}\033[00m".format(msg))
"""


class Colors(object):
    reset = '\033[0m'
    bold = '\033[01m'
    disable = '\033[02m'
    underline = '\033[04m'
    reverse = '\033[07m'
    strike_through = '\033[09m'
    invisible = '\033[08m'

    class fg:
        black = '\033[30m'
        red = '\033[31m'
        green = '\033[32m'
        orange = '\033[33m'
        blue = '\033[34m'
        purple = '\033[35m'
        cyan = '\033[36m'
        light_grey = '\033[37m'
        dark_grey = '\033[90m'
        light_red = '\033[91m'
        light_green = '\033[92m'
        yellow = '\033[93m'
        light_blue = '\033[94m'
        pink = '\033[95m'
        light_cyan = '\033[96m'

    class bg:
        black = '\033[40m'
        red = '\033[41m'
        green = '\033[42m'
        orange = '\033[43m'
        blue = '\033[44m'
        purple = '\033[45m'
        cyan = '\033[46m'
        light_grey = '\033[47m'


def red(msg):
    print(Colors.fg.red + msg + Colors.reset)


def tag(msg):
    print("\033[1;31;42m {}\033[00m".format(msg))


# test
def log():
    msg = Colors.reset + "\033[1;31;42m TAG\033[00m " + Colors.fg.red + "hello world" + Colors.reset
    print(msg)


def green(msg):
    print(Colors.fg.green + msg + Colors.reset)


def yellow(msg):
    print(Colors.fg.yellow + msg + Colors.reset)


def light_blue(msg):
    print(Colors.fg.light_blue + msg + Colors.reset)


def purple(msg):
    print(Colors.fg.purple + msg + Colors.reset)


def cyan(msg):
    print(Colors.fg.cyan + msg + Colors.reset)


def light_gray(msg):
    print(Colors.fg.light_grey + msg + Colors.reset)


def black(msg):
    print(Colors.fg.black + msg + Colors.reset)


def print_format_table():
    """
    prints table of formatted text format options
    """
    for style in range(8):
        for fg in range(30, 38):
            s1 = ''
            for bg in range(40, 48):
                _format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (_format, _format)
            print(s1)
        print('\n')

# 打印色表
# print_format_table()
# log()
