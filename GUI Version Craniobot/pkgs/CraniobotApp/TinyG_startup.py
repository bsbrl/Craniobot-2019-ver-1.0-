#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from CNCController import CNCController as CNC
from generateCircularCraniotomy import GenerateCircularCraniotomy
from generate_milling_commands import MillPath
from brainwindow import BrainWindow
from umnlogo import UMNLogo

tinyG = CNC()
tinyG.assignPort("default")
tinyG.connect()
tinyG.checkConnection()

"""
#Use this code to generate probe commands for a circular craniotomy

craniotomy = GenerateCircularCraniotomy(0,0,3,10)
probe_commands = craniotomy.gCode
"""

"""
#Use this code to generate the probe commands for the UMN logo

tiny
probe_commands = craniotomyUMN.gCode
"""



