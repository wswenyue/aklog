#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by zhangwanxin on 2018/11/4.


def is_empty(obj):
    if obj is None:
        return True
    if not obj:
        return True
    if type(obj) is str:
        if obj == "":
            return True
        elif obj.strip() == "":
            return True
    else:
        return False


def is_not_empty(obj):
    return not is_empty(obj)


def get_str(obj):
    if type(obj) is str:
        return obj
    elif type(obj) is bytes:
        return obj.decode("utf-8")
    else:
        return str(obj)
