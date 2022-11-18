#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:   wswenyue
@date:     2022/11/10 
"""
from typing import List

import comm_tools
from app_info import AppInfoHelper
from log_info import LogInfo, LogLevelHelper


class LogFilter(object):

    def __init__(self,
                 _package: str = None,
                 _package_exclude: List[str] = None,
                 _is_package_all: bool = False,
                 _tag: str = None,
                 _is_tag_exact: bool = False,
                 _is_tag_ignore_case: bool = True,
                 _msg: str = None,
                 _priority: str = None):
        """
         过滤
        :param _package: 包名
        :param _package_exclude:  包名排除
        :param _tag: tag
        :param _is_tag_exact: tag 精准匹配
        :param _is_tag_ignore_case: tag 忽略大小写
        :param _msg: msg匹配（包含匹配）
        :param _priority: 日志过滤级别
        """
        if _is_package_all:
            self._is_package_all = True
            self._is_package_current = False
        else:
            self._is_package_all = False
            if comm_tools.is_empty(_package) and comm_tools.is_empty(_package_exclude):
                self._is_package_current = True
            else:
                self._is_package_current = False
                self._package = _package
                self._package_exclude = _package_exclude
        self._tag = _tag
        self._is_tag_exact = _is_tag_exact
        self._is_tag_ignore_case = _is_tag_ignore_case
        self._msg = _msg
        self._level = LogLevelHelper.level_code(_priority)

    def filter_package(self, package: str) -> bool:
        if self._is_package_all:
            # 全部应用日志
            return True
        if self._is_package_current:
            # 当前应用
            return AppInfoHelper.cur_app_package() in package
        if self._package_exclude and package in self._package_exclude:
            return False
        if self._package in package:
            return True
        return False

    def filter_tag(self, tag: str) -> bool:
        if comm_tools.is_empty(self._tag):
            # 不做过滤
            return True
        if comm_tools.is_empty(tag):
            # 不匹配
            return False
        if self._is_tag_exact:
            # 精准匹配
            if self._is_tag_ignore_case:
                # 忽略大小写
                return self._tag.lower() == tag.lower()
            else:
                return self._tag == tag
        else:
            # 模糊匹配
            if self._is_tag_ignore_case:
                # 忽略大小写
                return self._tag.lower() in tag.lower()
            else:
                return self._tag in tag

    def filter_level(self, level: int) -> bool:
        return self._level <= level

    def filter_msg(self, msg: str) -> bool:
        if comm_tools.is_empty(self._msg):
            # 不做过滤
            return True
        return self._msg in msg

    def is_filter(self, log: LogInfo) -> bool:
        if not log:
            return False
        """
        过滤日志
        :param log:
        :return: true：打印日志，false：不打印，丢弃
        """
        if self.filter_package(log.get_process_name()) \
                and self.filter_level(log.get_level()) \
                and self.filter_tag(log.tag) \
                and self.filter_msg(log.get_msg_content()):
            return True
        return False
