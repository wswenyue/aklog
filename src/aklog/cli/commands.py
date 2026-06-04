#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

from aklog.app.info import AppInfoHelper
from aklog.core import color_print
from aklog.core.comm_tools import get_str
from aklog.device.manager import resolve_device


def run_log(platform, log_printer, level_arg=None):
    platform.check_connect()
    AppInfoHelper.start(platform)
    level = None
    if level_arg:
        level = get_str(level_arg[0]) if isinstance(level_arg, list) else get_str(level_arg)
    pro = platform.start_log_stream(level=level)
    parser = platform.create_log_parser(log_printer)
    err_code = pro.poll()
    _line = None
    while err_code is None:
        try:
            _line = pro.stdout.readline()
            if _line:
                parser.parser(get_str(_line).strip())
        except Exception as e:
            color_print.red("===========parser error===============\n{0}".format(e))
            if _line:
                print("==>{0}<==".format(_line))
        err_code = pro.poll()
    if parser.log and log_printer:
        log_printer.print(parser.log)


def main(argv=None):
    from aklog.cli.args import AkLogCli

    cli = AkLogCli()
    args = cli.parse(argv)
    platform = resolve_device(args.get("device"))
    if cli.run_command(platform, args):
        return
    run_log(platform, cli.build_log_printer(args), args.get("level"))
