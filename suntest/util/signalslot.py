# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Filename: signalslot.py
# Author:   huangbin@pset.suntec.net
# Date:     2016.8.15
# Input:
#      None
# ------------------------------------------------------------------------------


class SignalSlot(object):
    _SSPool = dict()

    @staticmethod
    def connect(signal, slot):
        if(signal not in SignalSlot._SSPool):
            SignalSlot._SSPool[signal] = []
        if(slot not in SignalSlot._SSPool[signal]):
            SignalSlot._SSPool[signal] = [slot]

    @staticmethod
    def emit(signal, args):
        if(signal in SignalSlot._SSPool):
            slots = SignalSlot._SSPool[signal]
            for i in range(len(slots)):
                slots[i](*args)
