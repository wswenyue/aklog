#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author:   wswenyue
@date:     2022/11/18 
"""
import re
from abc import ABCMeta, abstractmethod
from typing import List, Optional, Union

import comm_tools
from color_print import ColorStr


class IFormatContent(metaclass=ABCMeta):

    @abstractmethod
    def format_content(self, _input: str) -> Optional[Union[str, ColorStr]]:
        pass


class JsonValueFormat(IFormatContent):
    def __init__(self, _keys: List[str]):
        self._keys_reg = {}
        for _key in _keys:
            self._keys_reg[_key] = re.compile(r'\\?["\']?' + re.escape(_key) + r'\\?["\']?[:=]\\?["\'](.*?)\\?["\']',
                                              re.M)

    @staticmethod
    def _reg_match(reg, msg: str) -> str:
        ret = reg.findall(msg)
        if comm_tools.is_empty(ret):
            return ""
        if len(ret) == 1:
            return str(ret[0]).strip()
        return str(ret)

    def format_content(self, _input: str) -> Optional[Union[str, ColorStr]]:
        if comm_tools.is_empty(_input):
            return None
        has_key = False
        for _key in self._keys_reg.keys():
            if _key in _input:
                has_key = True
                break
        if not has_key:
            return None
        ret: str = ""
        for _key, reg in self._keys_reg.items():
            value = JsonValueFormat._reg_match(reg, _input)
            if comm_tools.is_not_empty(value):
                ret += f"'{_key}':'{value}'\t"
        if comm_tools.is_empty(ret):
            return None
        return "👉 " + ret
