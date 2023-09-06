#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:   wswenyue
@date:     2023/2/27 
"""
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Optional, List, Union

import comm_tools
from app_info import AppInfoHelper
from color_print import ColorStr
from content_format import JsonValueFormat
from log_info import LogLevelHelper


class IBaseFilterFormat(metaclass=ABCMeta):

    @abstractmethod
    def filter(self, _input: str) -> bool:
        """
        :param _input:
        :return: True: 表示接受数据 False: 表示丢弃数据
        """
        pass

    def format_content(self, _input: str) -> Optional[Union[str, ColorStr]]:
        if not self.filter(_input):
            # False 既过滤
            return None
        if not _input:
            return ""
        return _input


class PackageFilterType(Enum):
    # top app
    Top = 0,
    # all app
    All = 1,
    # 指定 app
    TARGET = 2,
    # 排除 app
    EXCLUDE = 3


class LogPackageFilterFormat(IBaseFilterFormat):
    """
    log package 过滤
    """

    def __init__(self, _type: PackageFilterType, _target: Optional[List[str]] = None):
        self.type = _type
        self.target_package = _target

    def filter(self, package: str) -> bool:
        if self.type == PackageFilterType.Top:
            return AppInfoHelper.cur_app_package() in package
        elif self.type == PackageFilterType.All:
            return True
        elif self.type == PackageFilterType.TARGET:
            if comm_tools.is_empty(self.target_package):
                return False
            for _target in self.target_package:
                if _target in package:
                    return True
            return False
        elif self.type == PackageFilterType.EXCLUDE:
            if comm_tools.is_empty(self.target_package):
                return True
            for _target in self.target_package:
                if _target in package:
                    return False
            return True
        else:
            # 没有类型，默认当做all处理
            return True


class LogTagFilterFormat(IBaseFilterFormat):

    def __init__(self, target: Optional[List[str]] = None,
                 tag_not: Optional[List[str]] = None,
                 is_exact: bool = False,
                 is_tag_not_fuzzy: bool = False):
        self.is_exact = is_exact
        self.target = target
        self.tag_not = tag_not
        self.is_tag_not_fuzzy = is_tag_not_fuzzy

    def filter(self, tag: str) -> bool:
        if self.tag_not:
            if self.is_tag_not_fuzzy:
                for tagN in self.tag_not:
                    if tagN in tag:
                        return False
            else:
                if tag.strip() in self.tag_not:
                    return False
        if (self.target is None) or (len(self.target) <= 0):
            # 没有设置tag，既不需要匹配tag，全接受
            return True
        if self.is_exact:
            return tag in self.target
        else:
            for _tag in self.target:
                if _tag in tag:
                    return True
            return False


class LogMsgFilterFormat(IBaseFilterFormat):
    def __init__(self, target: Optional[List[str]] = None,
                 msg_not: Optional[List[str]] = None,
                 json_format: Optional[JsonValueFormat] = None):
        self.target = target
        self.msg_not = msg_not
        self.json_format = json_format

    def filter(self, msg: str) -> bool:
        # 不处理
        return True

    def format_content(self, _input: str) -> Optional[Union[str, ColorStr]]:
        if self.msg_not:
            for msgN in self.msg_not:
                if msgN in _input:
                    return None
        if self.json_format:
            return self.json_format.format_content(_input)
        if comm_tools.is_not_empty(self.target):
            for _msg in self.target:
                if _msg in _input:
                    return _input
            return None
        return _input


class LogLevelFilterFormat(IBaseFilterFormat):
    def __init__(self, target: Optional[int] = None):
        self.target = target

    def filter(self, level: str) -> bool:
        if self.target:
            return self.target <= LogLevelHelper.level_code(level)
        return True
