#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by wswenyue on 2019/6/26.
import re
from queue import Queue

import color_print
import comm_tools
import debug


class Node(object):
    __id = None
    __parent = None
    __children = None
    __depth = 0
    __content = None

    def __init__(self, _id, content):
        self.__id = _id
        self.__content = content

    def insert(self, node, pid):
        if node is None or pid is None:
            return False
        parent = self.search(pid)
        if parent:
            parent.__add_child(node)
            return True
        return False

    def search(self, _id):
        if int(_id) < 0:
            return None
        if _id == self.__id:
            return self
        else:
            if self.has_child():
                for child in self.__children:
                    ret = child.search(_id)
                    if ret is not None:
                        return ret
            return None

    def search_parent(self, _id):
        node = self.search(_id)
        if node:
            return node.get_parent()
        return None

    def __add_child(self, child):
        if self.__children is None:
            self.__children = []
        child.__set_parent(self)
        child.__set_depth(self.__depth + 1)
        self.__children.append(child)

    def has_child(self):
        if self.__children is None:
            return False
        return len(self.__children) > 0

    def get_children(self):
        return self.__children

    def get_content(self):
        return self.__content

    def get_depth(self):
        return self.__depth

    def __set_depth(self, depth):
        self.__depth = depth

    def get_id(self):
        return self.__id

    def get_pid(self):
        if self.__parent:
            return self.__parent.get_id()
        return None

    def get_parent(self):
        return self.__parent

    def __set_parent(self, parent):
        self.__parent = parent

    def is_root(self):
        return self.__parent is None

    def is_leaf(self):
        return self.has_child() is not True

    def node_print(self):
        print("-" * self.__depth * 4 + str(self.get_content()))
        if self.has_child():
            for child in self.__children:
                child.node_print()

    @staticmethod
    def get_level_nodes(root, max_level=-1):
        if root is None:
            return None
        if not isinstance(root, Node):
            return None
        queue = Queue()
        queue.put(root)
        level_map = {}
        while True:
            count = queue.qsize()
            if count == 0:
                break
            cur_depth = -1
            while count > 0:
                node = queue.get()
                cur_depth = node.get_depth()
                if not (cur_depth in level_map):
                    level_map[cur_depth] = []
                level_map[cur_depth].append(node)
                if node.has_child():
                    for ch in node.get_children():
                        queue.put(ch)
                count -= 1
            if max_level == cur_depth:
                break
        return level_map

    @staticmethod
    def get_target_node(root, level, content):
        l_map = Node.get_level_nodes(root, level)
        if l_map is None:
            debug.log("result map is empty!")
            return
        nodes = l_map.get(level)
        if nodes is None:
            debug.log("result is empty!")
        else:
            for n in nodes:
                if content in n.get_content().get_text():
                    return n
        return None

    @staticmethod
    def print_target_level_nodes(root, target_level, print_format=debug.log):
        l_map = Node.get_level_nodes(root, target_level)
        if l_map is None:
            print_format("result map is empty!")
            return
        nodes = l_map.get(target_level)
        if nodes is None:
            print_format("result is empty!")
        else:
            for n in nodes:
                print_format(str(n.get_content()))

    @staticmethod
    def print_level_nodes(root, print_format=debug.log):
        l_map = Node.get_level_nodes(root)
        if l_map is None:
            print_format("result map is empty!")
            return
        for level, nodes in l_map.items():
            print_format("##################{}#####BEGIN################".format(level))
            if nodes is not None:
                for n in nodes:
                    print_format(str(n.get_content()))
            print_format("##################{}#####END##################".format(level))

    @staticmethod
    def print_diameter_node(node, print_format=debug.log):
        if node is None:
            print_format("node is None!!!")
            return
        if not isinstance(node, Node):
            print_format("Type Error!!!")
            return
        stack = []
        temp = node
        while True:
            if temp is None:
                break
            stack.append(temp)
            if temp.is_root():
                break
            temp = temp.get_parent()

        while True:
            if len(stack) <= 0:
                break
            n = stack.pop()
            print_format(str(n.get_content()))
            if len(stack) <= 0:
                if n.has_child():
                    for c in n.get_children():
                        print_format(str(c.get_content()))
                break


class Bean(object):
    __text = None
    __num = None

    def __init__(self, text, num):
        self.__text = text
        self.__num = num

    def get_text(self):
        return self.__text

    def get_num(self):
        return self.__num

    def __repr__(self):
        return "[" + str(self.__num) + "]" + self.__text

    def __str__(self):
        return "[" + str(self.__num) + "]" + self.__text

    def __eq__(self, other):
        if not isinstance(other, Bean):
            return NotImplemented
        return self.__text == other.__text

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__text)


class TreeDataParser(object):
    PATTERN_BLANK = re.compile(r"^(\s*)")

    def parser(self, path):
        if comm_tools.is_empty(path):
            return

        def insert_node(root, node, last_depth, depth, last_node):
            if last_depth == depth:
                root.insert(node, last_node.get_pid())
            elif last_depth < depth:
                root.insert(node, last_node.get_id())
            else:
                p = last_node.get_parent()
                if p:
                    num = p.get_content().get_num()
                    insert_node(root, node, num, depth, p)
                else:
                    debug.log_err(last_node.get_content())

        index = 1
        last_depth = 0
        root = Node(index - 1, Bean("Root:", last_depth))
        last_node = None
        with open(path, "r") as fp:
            for line in fp:
                if comm_tools.is_empty(line):
                    continue
                match = self.PATTERN_BLANK.match(line)
                if not match:
                    print("not match-->" + line)
                    continue
                group = str(match.groups()[0])
                depth = len(group)
                node = Node(index, Bean(line.strip(), depth))
                if last_node is None:
                    root.insert(node, root.get_id())
                else:
                    insert_node(root, node, last_depth, depth, last_node)
                last_node = node
                last_depth = depth
                index += 1

        # Node.print_target_level_nodes(root, 3, print_format=color_print.light_blue)
        node = Node.get_target_node(root, 3, "RecentsActivity")
        if node is None:
            debug.log("empty!!!")
        else:
            Node.print_diameter_node(node, print_format=color_print.light_blue)
        # Node.print_target_level_nodes(root, 1, print_format=color_print.light_blue)
        # root.node_print()

# TreeDataParser().parser("~/Desktop/top.txt")


# root = Node(1, "A")
# root.insert(Node(2, "B"), 1)
# root.insert(Node(3, "C"), 1)
# root.insert(Node(4, "D"), 1)
# root.insert(Node(5, "E"), 2)
# root.insert(Node(6, "F"), 2)
# root.insert(Node(7, "G"), 2)
# root.insert(Node(8, "H"), 3)
# root.insert(Node(9, "Q"), 4)
# root.insert(Node(10, "M"), 4)
# root.node_print()
# Node.print_target_level_nodes(root, 1)
