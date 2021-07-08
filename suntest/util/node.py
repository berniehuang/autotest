# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: node.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.22
# Input:
#      None
# ------------------------------------------------------------------------------


class Node(object):
    def __init__(self):
        self._head = None
        self._node = None
        self._next = None
        self._count = 0

    def __iter__(self):
        return self

    # python 3
    def __next__(self):
        return self.next()

    def __len__(self):
        return self._count

    def isEmpty(self):
        return self._head is None

    def append(self, node):
        if self._node is None:
            self._head = self._next = node
        else:
            self._node.next = node
        self._node = node
        self._count += 1

    def next(self):
        if self._next is None:
            self._next = self._head
            raise StopIteration
        else:
            case = self._next
            self._next = self._next.next
            return case
