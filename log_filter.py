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

    def __init__(self):
        self._tags = []
        self._msgs = []
        self._msg_format: Optional[IFormatContent] = None
        self._level = LogLevelHelper.UNKNOWN
        self._is_package_all: bool = False
        self._is_tag_exact: bool = False
        self._is_tag_ignore_case: bool = True
        self._is_package_current = None
        self._package = None
        self._package_exclude = None

    @property
    def package(self):
        return self._package

    @package.setter
    def package(self, _package: str = None):
        """
        包名
        :param _package:
        :return:
        """
        self._package = _package

    @property
    def package_exclude(self):
        return self._package_exclude

    @package_exclude.setter
    def package_exclude(self, _package_exclude: List[str] = None):
        """
        包名排除
        :param _package_exclude:
        :return:
        """
        self._package_exclude = _package_exclude

    @property
    def is_package_all(self):
        return self._is_package_all

    @is_package_all.setter
    def is_package_all(self, _flag: bool):
        self._is_package_all = _flag

    @property
    def is_package_current(self):
        if self._is_package_current is None:
            if self.is_package_all:
                self._is_package_current = False
            else:
                if comm_tools.is_empty(self.package) and comm_tools.is_empty(self.package_exclude):
                    self._is_package_current = True
                else:
                    self._is_package_current = False
        return self._is_package_current

    @property
    def is_tag_exact(self):
        return self._is_tag_exact

    @is_tag_exact.setter
    def is_tag_exact(self, _flag: bool):
        """
        tag 精准匹配
        :param _flag:
        :return:
        """
        self._is_tag_exact = _flag

    @property
    def is_tag_ignore_case(self):
        return self._is_tag_ignore_case

    @is_tag_ignore_case.setter
    def is_tag_ignore_case(self, _flag: bool):
        """
        tag 忽略大小写
        :param _flag:
        :return:
        """
        self._is_tag_ignore_case = _flag

    def priority(self, _priority: str):
        """
        日志过滤级别
        :param _priority:
        :return:
        """
        self._level = LogLevelHelper.level_code(_priority)

    @property
    def tags(self) -> List[str]:
        """
        tag 匹配
        :return:
        """
        return self._tags

    @tags.setter
    def tags(self, _tags: List[str] = None):
        """
        tag 匹配
        :param _tags:
        :return:
        """
        self._tags = _tags

    @property
    def msgs(self) -> List[str]:
        """
        msg匹配（包含匹配）
        :return:
        """
        return self._msgs

    @msgs.setter
    def msgs(self, _msgs: List[str] = None):
        """
        msg匹配（包含匹配）
        :param _msgs:
        :return:
        """
        self._msgs = _msgs

    @property
    def msg_format(self) -> Optional[IFormatContent]:
        return self._msg_format

    @msg_format.setter
    def msg_format(self, _msg_format: Optional[IFormatContent] = None):
        self._msg_format = _msg_format

    def filter_package(self, package: str) -> bool:
        if self.is_package_all:
            # 全部应用日志
            return True
        if self.is_package_current:
            # 当前应用
            return AppInfoHelper.cur_app_package() in package
        if self.package_exclude and package in self.package_exclude:
            return False
        if self.package in package:
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
                                    is_exact=self.is_tag_exact,
                                    is_ignore_case=self.is_tag_ignore_case):
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
            log.msg_format = self.msg_format
            return True
        return False
