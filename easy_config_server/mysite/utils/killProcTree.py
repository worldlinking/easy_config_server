# written by cy on 2022-11-17 11:17
# -*- coding: utf-8 -*-
import subprocess
import os
import signal
import psutil
import time

def killProcTree(pid):
    baseProc = psutil.Process(pid)
    childrenProcList = baseProc.children(recursive=True)
    for proc in childrenProcList:
        if (len(proc.children(recursive=True)) == 0):
            os.kill(proc.pid,signal.SIGILL)
        else:
            killProcTree(proc.pid)
    os.kill(pid, signal.SIGILL)

