#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:   wswenyue
@date:     2022/11/10 
"""
from typing import List, Optional

import comm_tools
from app_info import AppInfoHelper
from format_content import IFormatContent
from log_info import LogInfo, LogLevelHelper


class LogFilter(object):

    def __init__(self,
                 _package: str = None,
                 _package_exclude: List[str] = None,
                 _is_package_all: bool = False,
                 _is_tag_exact: bool = False,
                 _is_tag_ignore_case: bool = True,
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
        self._is_tag_exact = _is_tag_exact
        self._is_tag_ignore_case = _is_tag_ignore_case

        self._level = LogLevelHelper.level_code(_priority)
        self._tags = []
        self._msgs = []
        self._msg_format: Optional[IFormatContent] = None

    @property
    def tags(self) -> List[str]:
        return self._tags

    @tags.setter
    def tags(self, _tags: List[str] = None):
        self._tags = _tags

    @property
    def msgs(self) -> List[str]:
        return self._msgs

    @msgs.setter
    def msgs(self, _msgs: List[str] = None):
        self._msgs = _msgs

    @property
    def msg_format(self) -> Optional[IFormatContent]:
        return self._msg_format

    @msg_format.setter
    def msg_format(self, _msg_format: Optional[IFormatContent] = None):
        self._msg_format = _msg_format

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
        if comm_tools.is_empty(self.tags):
            # 不做过滤
            return True
        if comm_tools.is_empty(tag):
            # 不匹配
            return False
        for _tag in self.tags:
            if comm_tools.match_str(_tag, tag,
                                    is_exact=self._is_tag_exact,
                                    is_ignore_case=self._is_tag_ignore_case):
                return True

        return False

    def filter_level(self, level: int) -> bool:
        return self._level <= level

    def filter_msg(self, msg: str) -> bool:
        if comm_tools.is_empty(self.msgs):
            # 不做过滤
            return True
        for _msg in self.msgs:
            if _msg in msg:
                return True

        return False

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
            log.msg_format = self._msg_format
            return True
        return False
