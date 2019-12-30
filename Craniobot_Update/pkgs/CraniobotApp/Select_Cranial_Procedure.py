"""
Craniobot: select cranial procedures and run probing routine
University of Minnesota - Twin Cities
Biosensing and Biorobotics Lab
author: Daniel Sousa Schulman
email: sousa013@umn.edu // dschul@umich.edu
PI: Suhasa Kodandaramaiah (suhasabk@umn.edu)
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from CraniobotApp.CNCController import CNCController as CNC
from string import *
from CraniobotApp.generateCircularCraniotomy import GenerateCircularCraniotomy
from CraniobotApp.generateSkullThinning import GenerateSkullThinning
from CraniobotApp.generateHoleDrill import GenerateHoleDrill
from CraniobotApp.generateGCode import *
import time
from CraniobotApp.instructions_Milling import *
import numpy as np
import json
import plotly as py
import plotly.graph_objs as go
from CraniobotApp.generate_milling_commands import MillPath


# %%
class cranialProcedure():
    #creates an object to store the gcode routines for each cranial procedure and keep track of variables 
    def __init__(self, procedureType, parameter, gCode_out, millingPath=None, millingDepth=None,probed=None):
       self.procedureType=procedureType
       self.parameter=parameter
       self.gCode_out=gCode_out
       if millingPath is not None:
           self.millingPath=millingPath
       if millingDepth is not None:
           self.millingDepth=millingDepth
       self.probed=0 #used to determine if srface profilin was already executed on that cranial pocedure          
           
    

# %%
class Ui_Select_Cranial_Procedure(object):
    def __init__(self, tinyG=None, probeCommands=None):
        if tinyG is None: #starts CNC seral communication
            self.tinyG = CNC()
            self.tinyG.assignPort("default")
            self.tinyG.connect()
            self.tinyG.checkConnection()
        else:
            self.tinyG = tinyG
        if probeCommands is None:
            #initialize array to store all cranial procedures
            self.probeCommands=[]
        else:
            self.probeCommands=probeCommands
    
    def firstProbe(self,tinyG):
        #runs single probe and stops upon contact
        tinyG.setOrigin()
        tinyG.runSingleProbe()
        tinyG.setOrigin()
        
        #reads status from tinyG and waits untill completd
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        while(stat.find("stat")<0):
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            time.sleep(1)

        self.updatePosition(tinyG)
        
    def  runProbe(self, tinyG, probeCommands):
        #run surface profiling routine
        millingPaths=[]
        for i in probeCommands:
            tinyG.runProbe(i.gCode_out)
            millingPaths.append(tinyG.probe_output)
        time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3):
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
        self.updatePosition(tinyG)   
    
    def  openSetXYZ_Origin(self, tinyG, probeCommands):
        #Opens surface profiling window
        self.window = QtWidgets.QDialog()
        self.uiSetXYZ_Origin = Ui_SetXYZ_Origin()
        self.uiSetXYZ_Origin.setupUi(self.window, tinyG, probeCommands)
        self.window.show()
    
    def  openDesired_Craniotomy(self, tinyG, probeCommands):
        #Prompts user to select csv file for custom craniotomy
        filename = QtWidgets.QFileDialog.getOpenFileName(None,'Open File')
        if filename[0]:
            pattern=generateGCode(filename[0])
            parameter=str(filename[0])
            procedure=cranialProcedure("Custom Craniotomy", parameter, pattern.gCode)
            probeCommands.append(procedure)
    
    def  openInstructions(self):
        #instructions for selecting the cranial procedures
        self.window = QtWidgets.QDialog()
        self.uiI_Select = Ui_I_Select()
        self.uiI_Select.setupUi(self.window)
        self.window.show()
    
    def openInstructions_2(self):
        #instructions for the right side of the window
        self.window = QtWidgets.QDialog()
        self.uiI_Jog = Ui_I_Jog()
        self.uiI_Jog.setupUi(self.window)
        self.window.show()
        
    def  openHole_Drilling_1(self, tinyG, probeCommands):
        #opens hole drilling window
        self.window = QtWidgets.QDialog()
        self.uiHole_Drilling_1 = Ui_Hole_Drilling_1()
        self.uiHole_Drilling_1.setupUi(self.window, tinyG, probeCommands)
        self.window.show()
        
    def  openSkull_Thinning(self, tinyG, probeCommands):
        #opens skull thinning window
        self.window = QtWidgets.QDialog()
        self.uiSkullThinning = Ui_Skull_Thinning()
        self.uiSkullThinning.setupUi(self.window, tinyG, probeCommands)
        self.window.show()
        
    def  openCircular_Craniotomy(self, tinyG, probeCommands):
        #opens circular craniotomy window
        self.window = QtWidgets.QDialog()
        self.uiCircular_Craniotomy = Ui_Circular_Craniotomy()
        self.uiCircular_Craniotomy.setupUi(self.window, tinyG, probeCommands)
        self.window.show()
        
    def updatePosition(self, tinyG):
        #communicates with tiny g to find current position    
        tinyG.ser.write(b'{"pos":n}\n')
        pos=str(tinyG.ser.readlines())
        
        #string manipulation to extract x,y,z positions from json line
        initIndex=pos.find("pos")+6
        finalIndex=pos.find("\"a\"")-1
        newPos=pos[initIndex:finalIndex]

        xaxis=int(newPos[newPos.find("x")+3:newPos.find(",")-4])
        newPos=newPos[newPos.find(",")+1:]
        yaxis=int(newPos[newPos.find("y")+3:newPos.find(",")-4])
        newPos=newPos[newPos.find(",")+1:]
        zaxis=int(newPos[newPos.find("z")+3:len(newPos)-4])
        
        #display values on the screen
        self.XValue.display(xaxis)
        self.YValue.display(yaxis)
        self.ZValue.display(zaxis)
        
    def callJog(self, tinyG):
        #used to jog on all 3 directions
        XMove=0
        YMove=0
        ZMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100 #final unitare mm/min
        if(self.ZJog.text()):
            ZMove=float(self.ZJog.text())
            self.tinyG.jog("z", ZMove, int(speed))  
        if(self.XJog.text()):
            XMove=float(self.XJog.text())
            self.tinyG.jog("x", XMove, int(speed))
        if(self.YJog.text()):
            YMove=float(self.YJog.text())
            self.tinyG.jog("y", YMove, int(speed))
        
        time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
    
    #sequence of 3 individual jog commands for each axis
    def callJogX(self,tinyG):
        XMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        if(self.XJog.text()):
            XMove=float(self.XJog.text())
            self.tinyG.jog("x", XMove, int(speed))
            time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
        
    def callJogY(self,tinyG):
        YMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        if(self.YJog.text()):
            YMove=float(self.YJog.text())
            self.tinyG.jog("y", YMove, int(speed))
            time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
        
    def callJogZ(self,tinyG):
        ZMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        if(self.ZJog.text()):
            ZMove=float(self.ZJog.text())
            self.tinyG.jog("z", ZMove, int(speed))
            time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
    
    def serialCommand(self,tinyG):
        #sends a serial command text to the tinyG. Should be in gCode format
        if(self.gcodeManual.text()):
            com=str(self.gcodeManual.text())
            command = '{{"gc":"{}"}}\n'.format(com)
            tinyG.ser.write(command.encode('utf-8'))
        time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG) 
        
    def setupUi(self, Dialog):  
        #creates all the graphics, pushbutton events and keyboard shortcuts
        Dialog.setObjectName("Dialog")
        Dialog.resize(718, 351)
        #stylesheet creates a custom layout
        Dialog.setStyleSheet("#mainView, #calibration_tab, #mask_tab, #integration_tab {\n"
"    background: #3C3C3C;\n"
"    border: 5px solid #3C3C3C;\n"
"}\n"
"\n"
"QTabWidget::tab-bar{\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabWidget::pane {\n"
"    border:  1px solid #2F2F2F;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QWidget{\n"
"    color: #F1F1F1;\n"
"}\n"
"\n"
"\n"
"QTabBar::tab:left, QTabBar::tab:right {\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"    font: normal 14px;\n"
"    color: #F1F1F1;\n"
"    border-radius:2px;\n"
"\n"
"    padding: 0px;\n"
"    width: 20px;\n"
"    min-height:140px;\n"
"}\n"
"\n"
"\n"
"QTabBar::tab::top, QTabBar::tab::bottom {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"    border-right: 0px solid white;\n"
"    color: #F1F1F1;\n"
"    font: normal 11px;\n"
"    border-radius:2px;\n"
"    min-width: 65px;\n"
"    height: 19px;\n"
"    padding: 0px;\n"
"    margin-top: 1px;\n"
"    margin-right: 1px;\n"
" }\n"
"QTabBar::tab::left:last, QTabBar::tab::right:last{\n"
"    border-bottom-left-radius: 10px;\n"
"    border-bottom-right-radius: 10px;\n"
"}\n"
"QTabBar::tab:left:first, QTabBar::tab:right:first{\n"
"    border-top-left-radius: 10px;\n"
"    border-top-right-radius: 10px;\n"
"}\n"
"\n"
"QTabWidget, QTabWidget::tab-bar,  QTabWidget::panel, QWidget{\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"QTabWidget::tab-bar {\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabBar::tab:hover {\n"
"    border: 1px solid #ADADAD;\n"
"}\n"
"\n"
"QTabBar:tab:selected{\n"
"    background: qlineargradient(\n"
"            x1: 0, y1: 1,\n"
"            x2: 0, y2: 0,\n"
"            stop: 0 #727272,\n"
"            stop: 1 #444444\n"
"        );\n"
"    border:1px solid  rgb(255, 120,00);/*#ADADAD; */\n"
"}\n"
"\n"
"QTabBar::tab:bottom:last, QTabBar::tab:top:last{\n"
"    border-top-right-radius: 10px;\n"
"    border-bottom-right-radius: 10px;\n"
"}\n"
"QTabBar::tab:bottom:first, QTabBar::tab:top:first{\n"
"    border-top-left-radius: 10px;\n"
"    border-bottom-left-radius: 10px;\n"
"}\n"
"QTabBar::tab:top:!selected {\n"
"    margin-top: 1px;\n"
"    padding-top:1px;\n"
"}\n"
"QTabBar::tab:bottom:!selected{\n"
"    margin-bottom: 1px;\n"
"    padding-bottom:1px;\n"
"}\n"
"\n"
"QGraphicsView {\n"
"    border-style: none;\n"
"}\n"
"\n"
"QLabel , QCheckBox, QGroupBox, QRadioButton, QListWidget::item, QPushButton, QToolBox::tab, QSpinBox, QDoubleSpinBox , QComboBox{\n"
"    color: #F1F1F1;\n"
"    font-size: 12px;\n"
"}\n"
"QCheckBox{\n"
"    border-radius: 5px;\n"
"}\n"
"QRadioButton, QCheckBox {\n"
"    font-weight: normal;\n"
"    height: 15px;\n"
"}\n"
"\n"
"QLineEdit  {\n"
"    border-radius: 2px;\n"
"    background: #F1F1F1;\n"
"    color: black;\n"
"    height: 18 px;\n"
"}\n"
"\n"
"QLineEdit::focus{\n"
"    border-style: none;\n"
"    border-radius: 2px;\n"
"    background: #F1F1F1;\n"
"    color: black;\n"
"}\n"
"\n"
"QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled{\n"
"    color:rgb(148, 148, 148)\n"
"}\n"
"QSpinBox, QDoubleSpinBox {\n"
"    background-color:  #F1F1F1;\n"
"    color: black;\n"
"    /*margin-left: -15px;\n"
"    margin-right: -2px;*/\n"
"}\n"
"\n"
"QComboBox QAbstractItemView{\n"
"    background: #2D2D30;\n"
"    color: #F1F1F1;\n"
"    selection-background-color: rgba(221, 124, 40, 120);\n"
"    border-radius: 5px;\n"
"    min-height: 40px;\n"
"\n"
"}\n"
"\n"
"QComboBox QAbstractItemView:QScrollbar::vertical {\n"
"    width:100px;\n"
"}\n"
"\n"
"QComboBox:!editable {\n"
"    margin-left: 1px;\n"
"    padding: 0px 10px 0px 10px;\n"
"    height: 23px;\n"
"    background-color: #3C3C3C;\n"
"}\n"
"\n"
"QComboBox::item{\n"
"    background-color: #3C3C3C;\n"
"}\n"
"\n"
"QComboBox::item::selected {\n"
"    background-color: #505050;\n"
"}\n"
"QToolBox::tab:QToolButton{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"\n"
"    border-radius:2px;\n"
"    padding-right: 10px;\n"
"\n"
"    color: #F1F1F1;\n"
"    font-size: 12px;\n"
"    padding: 3px;\n"
"}\n"
"QToolBox::tab:QToolButton{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"     border: 1px solid  #5B5B5B;\n"
"\n"
"     border-radius:2px;\n"
"     padding-right: 10px;\n"
"\n"
"      color: #F1F1F1;\n"
"    font-size: 12px;\n"
"    padding: 3px;\n"
"}\n"
"\n"
"QPushButton{\n"
"    color: #F1F1F1;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop:1 #505050);\n"
"    border: 1px solid #5B5B5B;\n"
"    border-radius: 5px;\n"
"    padding-left: 8px;\n"
"    height: 18px;\n"
"    padding-right: 8px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    margin-top: 2px;\n"
"    margin-left: 2px;\n"
"}\n"
"\n"
"QPushButton::disabled{\n"
"}\n"
"\n"
"QPushButton::hover {\n"
"    border:1px solid #ADADAD;\n"
"}\n"
"\n"
"QPushButton::checked {\n"
"    background: qlineargradient(\n"
"        x1: 0, y1: 1,\n"
"        x2: 0, y2: 0,\n"
"        stop: 0 #727272,\n"
"        stop: 1 #444444\n"
"    );\n"
"     border:1px solid  rgb(255, 120,00);\n"
"}\n"
"\n"
"QPushButton::focus {\n"
"    outline: None;\n"
"}\n"
"QGroupBox {\n"
"    border: 1px solid #ADADAD;\n"
"    border-radius: 4px;\n"
"    margin-top: 7px;\n"
"    padding: 0px\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 20px\n"
"}\n"
"\n"
"QSplitter::handle:hover {\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"\n"
"QGraphicsView{\n"
"    border-style: none;\n"
"}\n"
"\n"
"QScrollBar:vertical {\n"
"    border: 2px solid #3C3C3C;\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    width: 12px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #969696, stop:1 #CACACA);\n"
"    border-radius: 3px;\n"
"    min-height: 20px;\n"
"    padding: 15px;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:vertical {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"    background: none;\n"
"}\n"
"\n"
"QScrollBar:horizontal {\n"
"    border: 2px solid #3C3C3C;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    height: 12 px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #969696, stop:1 #CACACA);\n"
"    border-radius: 3px;\n"
"    min-width: 20px;\n"
"    padding: 15px;\n"
"}\n"
"QScrollBar::add-line:horizontal {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:horizontal {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n"
"    background: none;\n"
"}\n"
"\n"
"QSplitterHandle:hover {}\n"
"\n"
"QSplitter::handle:vertical{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #505050, stop: 0.7 #3C3C3C);\n"
"    height: 15px;\n"
"}\n"
"\n"
"QSplitter::handle:vertical:pressed, QSplitter::handle:vertical:hover{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #5C5C5C, stop: 0.7 #3C3C3C);\n"
"}\n"
"\n"
"QSplitter::handle:horizontal{\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #505050, stop: 0.7 #3C3C3C);\n"
"    width: 15px;\n"
"}\n"
"\n"
"QSplitter::handle:horizontal:pressed, QSplitter::handle:horizontal:hover{\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #5C5C5C, stop: 0.7 #3C3C3C);\n"
"}\n"
"\n"
"QSplitter::handle:hover {\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    spacing: 10px;\n"
"    color: #F1F1F1;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    border: None;\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    font-size: 12px;\n"
"    text-align: center;\n"
"}\n"
"\n"
"QTableWidget QPushButton {\n"
"    margin: 5px;\n"
"}\n"
"\n"
"\n"
"QTableWidget QPushButton::pressed{\n"
"    margin-top: 7px;\n"
"    margin-left: 7px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(177,80,0,255), stop:1 rgba(255,120,0,255));\n"
"    selection-color: #F1F1F1;\n"
"}\n"
"\n"
"#phase_table_widget QCheckBox, #overlay_table_widget QCheckBox {\n"
"    margin-left: 5px;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox, #phase_table_widget QDoubleSpinBox {\n"
"    min-width: 50;\n"
"    max-width: 70;\n"
"    background: transparent;\n"
"    background-color: transparent;\n"
"    color:#D1D1D1;\n"
"    border: 1px solid transparent;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox:disabled, #phase_table_widget QDoubleSpinBox:disabled {\n"
"    color:#888;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button, #overlay_table_widget QDoubleSpinBox::down-button,\n"
"#phase_table_widget QDoubleSpinBox::up-button, #phase_table_widget QDoubleSpinBox::down-button {\n"
"    width: 11px;\n"
"    height: 9px;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop:1 #505050);\n"
"    border: 0.5px solid #5B5B5B;\n"
"    border-radius: 2px;\n"
"}\n"
"#overlay_table_widget QDoubleSpinBox::up-button:hover, #overlay_table_widget QDoubleSpinBox::down-button:hover,\n"
"#phase_table_widget QDoubleSpinBox::up-button:hover, #phase_table_widget QDoubleSpinBox::down-button:hover\n"
"{\n"
"    border:0.5px solid #ADADAD;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button:pressed,  #phase_table_widget QDoubleSpinBox::up-button:pressed{\n"
"    width: 10px;\n"
"    height: 8px;\n"
"}\n"
"#overlay_table_widget QDoubleSpinBox::down-button:pressed, #phase_table_widget QDoubleSpinBox::down-button:pressed {\n"
"    width: 10px;\n"
"    height: 8px;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button, #phase_table_widget QDoubleSpinBox::up-button {\n"
"    image: url(dioptas/resources/icons/arrow_up.ico) 1;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::down-button, #phase_table_widget QDoubleSpinBox::down-button {\n"
"    image: url(dioptas/resources/icons/arrow_down.ico) 1;\n"
"}\n"
"\n"
"QFrame#main_frame {\n"
"    color: #F1F1F1;\n"
"    border: 1px solid #5B5B5B;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"#calibration_mode_btn, #mask_mode_btn, #integration_mode_btn {\n"
"    font: normal 12px;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"#calibration_mode_btn {\n"
"   border-top-right-radius:8px;\n"
"   border-bottom-right-radius: 8px;\n"
"}\n"
"\n"
"#integration_mode_btn {\n"
"   border-top-left-radius:8px;\n"
"   border-bottom-left-radius: 8px;\n"
"}")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(410, -20, 21, 381))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.line.setFont(font)
        self.line.setAutoFillBackground(False)
        self.line.setStyleSheet("color: rgb(0, 0, 0);")
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(1)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setObjectName("line")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 320, 241, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.Circular = QtWidgets.QPushButton(Dialog)
        self.Circular.setGeometry(QtCore.QRect(30, 70, 171, 41))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Circular.setFont(font)
        self.Circular.setObjectName("Circular")
        self.AnchorHoleDrilling = QtWidgets.QPushButton(Dialog)
        self.AnchorHoleDrilling.setGeometry(QtCore.QRect(220, 130, 171, 41))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.AnchorHoleDrilling.setFont(font)
        self.AnchorHoleDrilling.setObjectName("AnchorHoleDrilling")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(140, 20, 191, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.SkullThinning = QtWidgets.QPushButton(Dialog)
        self.SkullThinning.setGeometry(QtCore.QRect(220, 70, 171, 41))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.SkullThinning.setFont(font)
        self.SkullThinning.setObjectName("SkullThinning")
        self.OtherPattern = QtWidgets.QPushButton(Dialog)
        self.OtherPattern.setGeometry(QtCore.QRect(30, 130, 171, 41))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.OtherPattern.setFont(font)
        self.OtherPattern.setObjectName("OtherPattern")
        self.startProbe = QtWidgets.QPushButton(Dialog)
        self.startProbe.setGeometry(QtCore.QRect(110, 220, 211, 41))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.startProbe.setFont(font)
        self.startProbe.setObjectName("startProbe")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setGeometry(QtCore.QRect(20, 60, 381, 121))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setObjectName("frame")
        self.Instructions = QtWidgets.QPushButton(Dialog)
        self.Instructions.setGeometry(QtCore.QRect(380, 20, 31, 21))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.Instructions.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Instructions.setFont(font)
        self.Instructions.setStyleSheet("QPushButton{\n"
"background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"border-radius: 10px;\n"
"}")
        self.Instructions.setObjectName("Instructions")
        self.GoButton = QtWidgets.QPushButton(Dialog)
        self.GoButton.setGeometry(QtCore.QRect(580, 210, 61, 51))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.GoButton.setFont(font)
        self.GoButton.setObjectName("GoButton")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(520, 20, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.ZValue = QtWidgets.QLCDNumber(Dialog)
        self.ZValue.setGeometry(QtCore.QRect(510, 160, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.ZValue.setFont(font)
        self.ZValue.setAutoFillBackground(False)
        self.ZValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.ZValue.setDigitCount(4)
        self.ZValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.ZValue.setObjectName("ZValue")
        self.XJog = QtWidgets.QLineEdit(Dialog)
        self.XJog.setGeometry(QtCore.QRect(580, 80, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.XJog.setFont(font)
        self.XJog.setAlignment(QtCore.Qt.AlignCenter)
        self.XJog.setObjectName("XJog")
        self.LabelJog = QtWidgets.QLabel(Dialog)
        self.LabelJog.setGeometry(QtCore.QRect(570, 50, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelJog.setFont(font)
        self.LabelJog.setAutoFillBackground(False)
        self.LabelJog.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelJog.setLineWidth(1)
        self.LabelJog.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelJog.setObjectName("LabelJog")
        self.LabelPosition = QtWidgets.QLabel(Dialog)
        self.LabelPosition.setGeometry(QtCore.QRect(470, 50, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelPosition.setFont(font)
        self.LabelPosition.setAutoFillBackground(False)
        self.LabelPosition.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelPosition.setLineWidth(1)
        self.LabelPosition.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelPosition.setObjectName("LabelPosition")
        self.YValue = QtWidgets.QLCDNumber(Dialog)
        self.YValue.setGeometry(QtCore.QRect(510, 120, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.YValue.setFont(font)
        self.YValue.setAutoFillBackground(False)
        self.YValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.YValue.setDigitCount(4)
        self.YValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.YValue.setObjectName("YValue")
        self.YJog = QtWidgets.QLineEdit(Dialog)
        self.YJog.setGeometry(QtCore.QRect(580, 120, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.YJog.setFont(font)
        self.YJog.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.YJog.setAlignment(QtCore.Qt.AlignCenter)
        self.YJog.setObjectName("YJog")
        self.LabelZ = QtWidgets.QLabel(Dialog)
        self.LabelZ.setGeometry(QtCore.QRect(480, 160, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelZ.setFont(font)
        self.LabelZ.setTextFormat(QtCore.Qt.PlainText)
        self.LabelZ.setScaledContents(False)
        self.LabelZ.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelZ.setWordWrap(False)
        self.LabelZ.setObjectName("LabelZ")
        self.LabelSpeed = QtWidgets.QLabel(Dialog)
        self.LabelSpeed.setGeometry(QtCore.QRect(470, 210, 111, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelSpeed.setFont(font)
        self.LabelSpeed.setAutoFillBackground(False)
        self.LabelSpeed.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelSpeed.setLineWidth(1)
        self.LabelSpeed.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelSpeed.setObjectName("LabelSpeed")
        self.XValue = QtWidgets.QLCDNumber(Dialog)
        self.XValue.setGeometry(QtCore.QRect(510, 80, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.XValue.setFont(font)
        self.XValue.setAutoFillBackground(False)
        self.XValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.XValue.setDigitCount(4)
        self.XValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.XValue.setObjectName("XValue")
        self.LabelY = QtWidgets.QLabel(Dialog)
        self.LabelY.setGeometry(QtCore.QRect(480, 120, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelY.setFont(font)
        self.LabelY.setTextFormat(QtCore.Qt.PlainText)
        self.LabelY.setScaledContents(False)
        self.LabelY.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelY.setWordWrap(False)
        self.LabelY.setObjectName("LabelY")
        self.LabelX = QtWidgets.QLabel(Dialog)
        self.LabelX.setGeometry(QtCore.QRect(480, 80, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelX.setFont(font)
        self.LabelX.setTextFormat(QtCore.Qt.PlainText)
        self.LabelX.setScaledContents(False)
        self.LabelX.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelX.setWordWrap(False)
        self.LabelX.setObjectName("LabelX")
        self.ZJog = QtWidgets.QLineEdit(Dialog)
        self.ZJog.setGeometry(QtCore.QRect(580, 160, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.ZJog.setFont(font)
        self.ZJog.setAlignment(QtCore.Qt.AlignCenter)
        self.ZJog.setObjectName("ZJog")
        self.speed = QtWidgets.QComboBox(Dialog)
        self.speed.setGeometry(QtCore.QRect(510, 240, 50, 22))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.speed.setFont(font)
        self.speed.setStyleSheet("")
        self.speed.setEditable(False)
        self.speed.setCurrentText("")
        self.speed.setObjectName("speed")
        self.gcodeManual = QtWidgets.QLineEdit(Dialog)
        self.gcodeManual.setGeometry(QtCore.QRect(450, 300, 161, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.gcodeManual.setFont(font)
        self.gcodeManual.setText("")
        self.gcodeManual.setAlignment(QtCore.Qt.AlignCenter)
        self.gcodeManual.setObjectName("gcodeManual")
        self.LabelGcode = QtWidgets.QLabel(Dialog)
        self.LabelGcode.setGeometry(QtCore.QRect(470, 280, 111, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelGcode.setFont(font)
        self.LabelGcode.setAutoFillBackground(False)
        self.LabelGcode.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelGcode.setLineWidth(1)
        self.LabelGcode.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelGcode.setObjectName("LabelGcode")
        self.SendButton = QtWidgets.QPushButton(Dialog)
        self.SendButton.setGeometry(QtCore.QRect(620, 300, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.SendButton.setFont(font)
        self.SendButton.setObjectName("SendButton")
        self.Instructions_2 = QtWidgets.QPushButton(Dialog)
        self.Instructions_2.setGeometry(QtCore.QRect(670, 20, 31, 21))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.Instructions_2.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Instructions_2.setFont(font)
        self.Instructions_2.setStyleSheet("QPushButton{\n"
"background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"border-radius: 10px;\n"
"}")
        self.Instructions_2.setObjectName("Instructions_2")
        self.goX = QtWidgets.QPushButton(Dialog)
        self.goX.setGeometry(QtCore.QRect(650, 80, 51, 21))
        self.goX.setStyleSheet("")
        self.goX.setObjectName("goX")
        self.goZ = QtWidgets.QPushButton(Dialog)
        self.goZ.setGeometry(QtCore.QRect(650, 160, 51, 21))
        self.goZ.setStyleSheet("")
        self.goZ.setObjectName("goZ")
        self.goY = QtWidgets.QPushButton(Dialog)
        self.goY.setGeometry(QtCore.QRect(650, 120, 51, 21))
        self.goY.setStyleSheet("")
        self.goY.setObjectName("goY")
        self.frame.raise_()
        self.line.raise_()
        self.label_2.raise_()
        self.Circular.raise_()
        self.AnchorHoleDrilling.raise_()
        self.label.raise_()
        self.SkullThinning.raise_()
        self.OtherPattern.raise_()
        self.startProbe.raise_()
        self.Instructions.raise_()
        self.GoButton.raise_()
        self.label_3.raise_()
        self.ZValue.raise_()
        self.XJog.raise_()
        self.LabelJog.raise_()
        self.LabelPosition.raise_()
        self.YValue.raise_()
        self.YJog.raise_()
        self.LabelZ.raise_()
        self.LabelSpeed.raise_()
        self.XValue.raise_()
        self.LabelY.raise_()
        self.LabelX.raise_()
        self.ZJog.raise_()
        self.speed.raise_()
        self.gcodeManual.raise_()
        self.LabelGcode.raise_()
        self.SendButton.raise_()
        self.Instructions_2.raise_()
        self.goX.raise_()
        self.goZ.raise_()
        self.goY.raise_()
        
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        #add items to drop down menu
        self.speed.addItem("1")
        self.speed.addItem("2")
        self.speed.addItem("3")
        self.speed.addItem("4")
        self.speed.addItem("5")
        self.speed.setCurrentIndex(2)
        
        #use arrow keys + pgup/pgdn to jog axis by small amount
        self.right_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("right"), Dialog)
        self.right_shortcut.activated.connect(lambda: self.tinyG.jog("X",0.5,200))
        self.right_shortcut.activated.connect(lambda: self.updatePosition(self.tinyG))
        self.left_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("left"), Dialog)
        self.left_shortcut.activated.connect(lambda: self.tinyG.jog("X",-0.5,200))
        self.left_shortcut.activated.connect(lambda: self.updatePosition(self.tinyG))
        self.up_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("up"), Dialog)
        self.up_shortcut.activated.connect(lambda: self.tinyG.jog("Y",0.5,200))
        self.up_shortcut.activated.connect(lambda: self.updatePosition(self.tinyG))
        self.down_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("down"), Dialog)
        self.down_shortcut.activated.connect(lambda: self.tinyG.jog("Y",-0.5,200))
        self.down_shortcut.activated.connect(lambda: self.updatePosition(self.tinyG))
        self.zero_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("PgDown"), Dialog)
        self.zero_shortcut.activated.connect(lambda: self.tinyG.jog("Z",-0.5,200))
        self.zero_shortcut.activated.connect(lambda: self.updatePosition(self.tinyG))
        self.one_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("PgUp"), Dialog)
        self.one_shortcut.activated.connect(lambda: self.tinyG.jog("Z",0.5,200))
        self.one_shortcut.activated.connect(lambda: self.updatePosition(self.tinyG))
        
        #pushbuttons events
        self.Instructions.clicked.connect(lambda: self.openInstructions()) 
        self.Instructions_2.clicked.connect(lambda: self.openInstructions_2())
        self.Circular.clicked.connect(Dialog.close)        
        self.Circular.clicked.connect(lambda: self.openCircular_Craniotomy(self.tinyG, self.probeCommands))        
        self.OtherPattern.clicked.connect(lambda: self.openDesired_Craniotomy(self.tinyG, self.probeCommands))        
        self.SkullThinning.clicked.connect(lambda: self.openSkull_Thinning(self.tinyG, self.probeCommands))
        self.AnchorHoleDrilling.clicked.connect(Dialog.close)       
        self.SkullThinning.clicked.connect(Dialog.close) 
        self.AnchorHoleDrilling.clicked.connect(lambda: self.openHole_Drilling_1(self.tinyG, self.probeCommands))
        self.SendButton.clicked.connect(lambda: self.serialCommand(self.tinyG))
        self.startProbe.clicked.connect(lambda: self.openSetXYZ_Origin(self.tinyG, self.probeCommands))
        self.startProbe.clicked.connect(Dialog.close)
        self.updatePosition(self.tinyG)
        self.GoButton.clicked.connect(lambda: self.callJog(self.tinyG))
        self.goX.clicked.connect(lambda: self.callJogX(self.tinyG))
        self.goY.clicked.connect(lambda: self.callJogY(self.tinyG))
        self.goZ.clicked.connect(lambda: self.callJogZ(self.tinyG))
        self.GoButton.setDefault(True)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Select Procedures"))
        self.label_2.setText(_translate("Dialog", "Craniobot v1.0 Created at U. of Minnesota"))
        self.Circular.setText(_translate("Dialog", "Circular Craniotomy"))
        self.AnchorHoleDrilling.setText(_translate("Dialog", "Anchor Hole Drilling"))
        self.label.setText(_translate("Dialog", "Select Procedures"))
        self.SkullThinning.setText(_translate("Dialog", "Skull Thinning"))
        self.OtherPattern.setText(_translate("Dialog", "Other Craniotomy Patterns"))
        self.startProbe.setText(_translate("Dialog", "Surface Profiling Configuration"))
        self.Instructions.setText(_translate("Dialog", "?"))
        self.Instructions_2.setText(_translate("Dialog", "?"))
        self.GoButton.setText(_translate("Dialog", "Go!"))
        self.label_3.setText(_translate("Dialog", "Set Position"))
        self.XJog.setText(_translate("Dialog", "0"))
        self.LabelJog.setText(_translate("Dialog", "Jog (mm)"))
        self.LabelPosition.setText(_translate("Dialog", "Position (mm)"))
        self.YJog.setText(_translate("Dialog", "0"))
        self.LabelZ.setText(_translate("Dialog", "Z"))
        self.LabelSpeed.setText(_translate("Dialog", "Speed (1-5)"))
        self.LabelY.setText(_translate("Dialog", "Y"))
        self.LabelX.setText(_translate("Dialog", "X"))
        self.ZJog.setText(_translate("Dialog", "0"))
        self.LabelGcode.setText(_translate("Dialog", "G-code command"))
        self.SendButton.setText(_translate("Dialog", "Send"))
        self.goX.setText(_translate("Dialog", "Go X"))
        self.goZ.setText(_translate("Dialog", "Go Z"))
        self.goY.setText(_translate("Dialog", "Go Y"))


# %%
class Ui_Hole_Drilling_1(object):
    def callHoleDrill(self,tinyG, probeCommands):
        if(self.X_Hole.text()):
            Xoff=float(self.X_Hole.text())
        if(self.Y_Hole.text()):
            Yoff=float(self.Y_Hole.text())
            craniotomy_probe = GenerateHoleDrill(Xoff,Yoff) #generates single point gcode
            parameter="X offset = "+str(Xoff)+"mm, Y offset = "+str(Yoff)+"mm"
            procedure=cranialProcedure("Hole Drilling", parameter, craniotomy_probe.gCode) #creates cranial procedure object
            probeCommands.append(procedure) #add it to the tracking array
        
    def  openSelect_Cranial_Procedure(self, tinyG, probeCommands):
        #go back to select cranial procedures
        self.window = QtWidgets.QDialog()
        self.uiSelect_Cranial_Procedure = Ui_Select_Cranial_Procedure(tinyG, probeCommands)
        self.uiSelect_Cranial_Procedure.setupUi(self.window)
        self.window.show()
        
    def updatePosition(self, tinyG):
        tinyG.ser.write(b'{"pos":n}\n')
        pos=str(tinyG.ser.readlines())
        
        initIndex=pos.find("pos")+6
        finalIndex=pos.find("\"a\"")-1
        newPos=pos[initIndex:finalIndex]

        xaxis=int(newPos[newPos.find("x")+3:newPos.find(",")-4])
        newPos=newPos[newPos.find(",")+1:]
        yaxis=int(newPos[newPos.find("y")+3:newPos.find(",")-4])
        newPos=newPos[newPos.find(",")+1:]
        zaxis=int(newPos[newPos.find("z")+3:len(newPos)-4])
        
        self.XValue.display(xaxis)
        self.YValue.display(yaxis)
        self.ZValue.display(zaxis)
        
    def callJog(self, tinyG):
        XMove=0
        YMove=0
        ZMove=0
        speed=300
        if(self.ZJog.text()):
            ZMove=float(self.ZJog.text())
        if(self.XJog.text()):
            XMove=float(self.XJog.text())
        if(self.YJog.text()):
            YMove=float(self.YJog.text())
        
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        tinyG.jog("x", XMove, int(speed))
        self.updatePosition(tinyG)
        tinyG.jog("y", YMove, int(speed))
        self.updatePosition(tinyG)
        tinyG.jog("z", ZMove, int(speed))
        self.updatePosition(tinyG)
        
    def setupUi(self, Dialog, tinyG, probeCommands):
        Dialog.setObjectName("Dialog")
        Dialog.resize(503, 284)
        Dialog.setStyleSheet("#mainView, #calibration_tab, #mask_tab, #integration_tab {\n"
"    background: #3C3C3C;\n"
"    border: 5px solid #3C3C3C;\n"
"}\n"
"\n"
"QTabWidget::tab-bar{\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabWidget::pane {\n"
"    border:  1px solid #2F2F2F;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QWidget{\n"
"    color: #F1F1F1;\n"
"}\n"
"\n"
"\n"
"QTabBar::tab:left, QTabBar::tab:right {\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"    font: normal 14px;\n"
"    color: #F1F1F1;\n"
"    border-radius:2px;\n"
"\n"
"    padding: 0px;\n"
"    width: 20px;\n"
"    min-height:140px;\n"
"}\n"
"\n"
"\n"
"QTabBar::tab::top, QTabBar::tab::bottom {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"    border-right: 0px solid white;\n"
"    color: #F1F1F1;\n"
"    font: normal 11px;\n"
"    border-radius:2px;\n"
"    min-width: 65px;\n"
"    height: 19px;\n"
"    padding: 0px;\n"
"    margin-top: 1px;\n"
"    margin-right: 1px;\n"
" }\n"
"QTabBar::tab::left:last, QTabBar::tab::right:last{\n"
"    border-bottom-left-radius: 10px;\n"
"    border-bottom-right-radius: 10px;\n"
"}\n"
"QTabBar::tab:left:first, QTabBar::tab:right:first{\n"
"    border-top-left-radius: 10px;\n"
"    border-top-right-radius: 10px;\n"
"}\n"
"\n"
"QTabWidget, QTabWidget::tab-bar,  QTabWidget::panel, QWidget{\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"QTabWidget::tab-bar {\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabBar::tab:hover {\n"
"    border: 1px solid #ADADAD;\n"
"}\n"
"\n"
"QTabBar:tab:selected{\n"
"    background: qlineargradient(\n"
"            x1: 0, y1: 1,\n"
"            x2: 0, y2: 0,\n"
"            stop: 0 #727272,\n"
"            stop: 1 #444444\n"
"        );\n"
"    border:1px solid  rgb(255, 120,00);/*#ADADAD; */\n"
"}\n"
"\n"
"QTabBar::tab:bottom:last, QTabBar::tab:top:last{\n"
"    border-top-right-radius: 10px;\n"
"    border-bottom-right-radius: 10px;\n"
"}\n"
"QTabBar::tab:bottom:first, QTabBar::tab:top:first{\n"
"    border-top-left-radius: 10px;\n"
"    border-bottom-left-radius: 10px;\n"
"}\n"
"QTabBar::tab:top:!selected {\n"
"    margin-top: 1px;\n"
"    padding-top:1px;\n"
"}\n"
"QTabBar::tab:bottom:!selected{\n"
"    margin-bottom: 1px;\n"
"    padding-bottom:1px;\n"
"}\n"
"\n"
"QGraphicsView {\n"
"    border-style: none;\n"
"}\n"
"\n"
"QLabel , QCheckBox, QGroupBox, QRadioButton, QListWidget::item, QPushButton, QToolBox::tab, QSpinBox, QDoubleSpinBox , QComboBox{\n"
"    color: #F1F1F1;\n"
"    font-size: 12px;\n"
"}\n"
"QCheckBox{\n"
"    border-radius: 5px;\n"
"}\n"
"QRadioButton, QCheckBox {\n"
"    font-weight: normal;\n"
"    height: 15px;\n"
"}\n"
"\n"
"QLineEdit  {\n"
"    border-radius: 2px;\n"
"    background: #F1F1F1;\n"
"    color: black;\n"
"    height: 18 px;\n"
"}\n"
"\n"
"QLineEdit::focus{\n"
"    border-style: none;\n"
"    border-radius: 2px;\n"
"    background: #F1F1F1;\n"
"    color: black;\n"
"}\n"
"\n"
"QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled{\n"
"    color:rgb(148, 148, 148)\n"
"}\n"
"QSpinBox, QDoubleSpinBox {\n"
"    background-color:  #F1F1F1;\n"
"    color: black;\n"
"    /*margin-left: -15px;\n"
"    margin-right: -2px;*/\n"
"}\n"
"\n"
"QComboBox QAbstractItemView{\n"
"    background: #2D2D30;\n"
"    color: #F1F1F1;\n"
"    selection-background-color: rgba(221, 124, 40, 120);\n"
"    border-radius: 5px;\n"
"    min-height: 40px;\n"
"\n"
"}\n"
"\n"
"QComboBox QAbstractItemView:QScrollbar::vertical {\n"
"    width:100px;\n"
"}\n"
"\n"
"QComboBox:!editable {\n"
"    margin-left: 1px;\n"
"    padding: 0px 10px 0px 10px;\n"
"    height: 23px;\n"
"    background-color: #3C3C3C;\n"
"}\n"
"\n"
"QComboBox::item{\n"
"    background-color: #3C3C3C;\n"
"}\n"
"\n"
"QComboBox::item::selected {\n"
"    background-color: #505050;\n"
"}\n"
"QToolBox::tab:QToolButton{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"\n"
"    border-radius:2px;\n"
"    padding-right: 10px;\n"
"\n"
"    color: #F1F1F1;\n"
"    font-size: 12px;\n"
"    padding: 3px;\n"
"}\n"
"QToolBox::tab:QToolButton{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"     border: 1px solid  #5B5B5B;\n"
"\n"
"     border-radius:2px;\n"
"     padding-right: 10px;\n"
"\n"
"      color: #F1F1F1;\n"
"    font-size: 12px;\n"
"    padding: 3px;\n"
"}\n"
"\n"
"QPushButton{\n"
"    color: #F1F1F1;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop:1 #505050);\n"
"    border: 1px solid #5B5B5B;\n"
"    border-radius: 5px;\n"
"    padding-left: 8px;\n"
"    height: 18px;\n"
"    padding-right: 8px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    margin-top: 2px;\n"
"    margin-left: 2px;\n"
"}\n"
"\n"
"QPushButton::disabled{\n"
"}\n"
"\n"
"QPushButton::hover {\n"
"    border:1px solid #ADADAD;\n"
"}\n"
"\n"
"QPushButton::checked {\n"
"    background: qlineargradient(\n"
"        x1: 0, y1: 1,\n"
"        x2: 0, y2: 0,\n"
"        stop: 0 #727272,\n"
"        stop: 1 #444444\n"
"    );\n"
"     border:1px solid  rgb(255, 120,00);\n"
"}\n"
"\n"
"QPushButton::focus {\n"
"    outline: None;\n"
"}\n"
"QGroupBox {\n"
"    border: 1px solid #ADADAD;\n"
"    border-radius: 4px;\n"
"    margin-top: 7px;\n"
"    padding: 0px\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 20px\n"
"}\n"
"\n"
"QSplitter::handle:hover {\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"\n"
"QGraphicsView{\n"
"    border-style: none;\n"
"}\n"
"\n"
"QScrollBar:vertical {\n"
"    border: 2px solid #3C3C3C;\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    width: 12px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #969696, stop:1 #CACACA);\n"
"    border-radius: 3px;\n"
"    min-height: 20px;\n"
"    padding: 15px;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:vertical {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"    background: none;\n"
"}\n"
"\n"
"QScrollBar:horizontal {\n"
"    border: 2px solid #3C3C3C;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    height: 12 px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #969696, stop:1 #CACACA);\n"
"    border-radius: 3px;\n"
"    min-width: 20px;\n"
"    padding: 15px;\n"
"}\n"
"QScrollBar::add-line:horizontal {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:horizontal {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n"
"    background: none;\n"
"}\n"
"\n"
"QSplitterHandle:hover {}\n"
"\n"
"QSplitter::handle:vertical{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #505050, stop: 0.7 #3C3C3C);\n"
"    height: 15px;\n"
"}\n"
"\n"
"QSplitter::handle:vertical:pressed, QSplitter::handle:vertical:hover{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #5C5C5C, stop: 0.7 #3C3C3C);\n"
"}\n"
"\n"
"QSplitter::handle:horizontal{\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #505050, stop: 0.7 #3C3C3C);\n"
"    width: 15px;\n"
"}\n"
"\n"
"QSplitter::handle:horizontal:pressed, QSplitter::handle:horizontal:hover{\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #5C5C5C, stop: 0.7 #3C3C3C);\n"
"}\n"
"\n"
"QSplitter::handle:hover {\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    spacing: 10px;\n"
"    color: #F1F1F1;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    border: None;\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    font-size: 12px;\n"
"    text-align: center;\n"
"}\n"
"\n"
"QTableWidget QPushButton {\n"
"    margin: 5px;\n"
"}\n"
"\n"
"\n"
"QTableWidget QPushButton::pressed{\n"
"    margin-top: 7px;\n"
"    margin-left: 7px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(177,80,0,255), stop:1 rgba(255,120,0,255));\n"
"    selection-color: #F1F1F1;\n"
"}\n"
"\n"
"#phase_table_widget QCheckBox, #overlay_table_widget QCheckBox {\n"
"    margin-left: 5px;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox, #phase_table_widget QDoubleSpinBox {\n"
"    min-width: 50;\n"
"    max-width: 70;\n"
"    background: transparent;\n"
"    background-color: transparent;\n"
"    color:#D1D1D1;\n"
"    border: 1px solid transparent;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox:disabled, #phase_table_widget QDoubleSpinBox:disabled {\n"
"    color:#888;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button, #overlay_table_widget QDoubleSpinBox::down-button,\n"
"#phase_table_widget QDoubleSpinBox::up-button, #phase_table_widget QDoubleSpinBox::down-button {\n"
"    width: 11px;\n"
"    height: 9px;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop:1 #505050);\n"
"    border: 0.5px solid #5B5B5B;\n"
"    border-radius: 2px;\n"
"}\n"
"#overlay_table_widget QDoubleSpinBox::up-button:hover, #overlay_table_widget QDoubleSpinBox::down-button:hover,\n"
"#phase_table_widget QDoubleSpinBox::up-button:hover, #phase_table_widget QDoubleSpinBox::down-button:hover\n"
"{\n"
"    border:0.5px solid #ADADAD;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button:pressed,  #phase_table_widget QDoubleSpinBox::up-button:pressed{\n"
"    width: 10px;\n"
"    height: 8px;\n"
"}\n"
"#overlay_table_widget QDoubleSpinBox::down-button:pressed, #phase_table_widget QDoubleSpinBox::down-button:pressed {\n"
"    width: 10px;\n"
"    height: 8px;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button, #phase_table_widget QDoubleSpinBox::up-button {\n"
"    image: url(dioptas/resources/icons/arrow_up.ico) 1;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::down-button, #phase_table_widget QDoubleSpinBox::down-button {\n"
"    image: url(dioptas/resources/icons/arrow_down.ico) 1;\n"
"}\n"
"\n"
"QFrame#main_frame {\n"
"    color: #F1F1F1;\n"
"    border: 1px solid #5B5B5B;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"#calibration_mode_btn, #mask_mode_btn, #integration_mode_btn {\n"
"    font: normal 12px;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"#calibration_mode_btn {\n"
"   border-top-right-radius:8px;\n"
"   border-bottom-right-radius: 8px;\n"
"}\n"
"\n"
"#integration_mode_btn {\n"
"   border-top-left-radius:8px;\n"
"   border-bottom-left-radius: 8px;\n"
"}")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(270, -20, 21, 341))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.line.setFont(font)
        self.line.setAutoFillBackground(False)
        self.line.setStyleSheet("color: rgb(0, 0, 0);")
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(3)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setObjectName("line")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 260, 201, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.Title = QtWidgets.QLabel(Dialog)
        self.Title.setGeometry(QtCore.QRect(40, 20, 181, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Title.setFont(font)
        self.Title.setObjectName("Title")
        self.Xoffset_Label_2 = QtWidgets.QLabel(Dialog)
        self.Xoffset_Label_2.setGeometry(QtCore.QRect(60, 80, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Xoffset_Label_2.setFont(font)
        self.Xoffset_Label_2.setObjectName("Xoffset_Label_2")
        self.X_Hole = QtWidgets.QLineEdit(Dialog)
        self.X_Hole.setGeometry(QtCore.QRect(120, 80, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.X_Hole.setFont(font)
        self.X_Hole.setAlignment(QtCore.Qt.AlignCenter)
        self.X_Hole.setObjectName("X_Hole")
        self.Y_Hole = QtWidgets.QLineEdit(Dialog)
        self.Y_Hole.setGeometry(QtCore.QRect(120, 120, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.Y_Hole.setFont(font)
        self.Y_Hole.setAlignment(QtCore.Qt.AlignCenter)
        self.Y_Hole.setObjectName("Y_Hole")
        self.Yoffset_label_2 = QtWidgets.QLabel(Dialog)
        self.Yoffset_label_2.setGeometry(QtCore.QRect(60, 120, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Yoffset_label_2.setFont(font)
        self.Yoffset_label_2.setObjectName("Yoffset_label_2")
        self.Next = QtWidgets.QPushButton(Dialog)
        self.Next.setGeometry(QtCore.QRect(120, 160, 61, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Next.setFont(font)
        self.Next.setObjectName("Next")
        self.GoButton = QtWidgets.QPushButton(Dialog)
        self.GoButton.setGeometry(QtCore.QRect(400, 210, 61, 51))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.GoButton.setFont(font)
        self.GoButton.setObjectName("GoButton")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(340, 20, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.ZValue = QtWidgets.QLCDNumber(Dialog)
        self.ZValue.setGeometry(QtCore.QRect(330, 160, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.ZValue.setFont(font)
        self.ZValue.setAutoFillBackground(False)
        self.ZValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.ZValue.setDigitCount(4)
        self.ZValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.ZValue.setObjectName("ZValue")
        self.XJog = QtWidgets.QLineEdit(Dialog)
        self.XJog.setGeometry(QtCore.QRect(400, 80, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.XJog.setFont(font)
        self.XJog.setAlignment(QtCore.Qt.AlignCenter)
        self.XJog.setObjectName("XJog")
        self.LabelJog = QtWidgets.QLabel(Dialog)
        self.LabelJog.setGeometry(QtCore.QRect(390, 50, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelJog.setFont(font)
        self.LabelJog.setAutoFillBackground(False)
        self.LabelJog.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelJog.setLineWidth(1)
        self.LabelJog.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelJog.setObjectName("LabelJog")
        self.LabelPosition = QtWidgets.QLabel(Dialog)
        self.LabelPosition.setGeometry(QtCore.QRect(290, 50, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelPosition.setFont(font)
        self.LabelPosition.setAutoFillBackground(False)
        self.LabelPosition.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelPosition.setLineWidth(1)
        self.LabelPosition.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelPosition.setObjectName("LabelPosition")
        self.YValue = QtWidgets.QLCDNumber(Dialog)
        self.YValue.setGeometry(QtCore.QRect(330, 120, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.YValue.setFont(font)
        self.YValue.setAutoFillBackground(False)
        self.YValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.YValue.setDigitCount(4)
        self.YValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.YValue.setObjectName("YValue")
        self.YJog = QtWidgets.QLineEdit(Dialog)
        self.YJog.setGeometry(QtCore.QRect(400, 120, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.YJog.setFont(font)
        self.YJog.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.YJog.setAlignment(QtCore.Qt.AlignCenter)
        self.YJog.setObjectName("YJog")
        self.LabelZ = QtWidgets.QLabel(Dialog)
        self.LabelZ.setGeometry(QtCore.QRect(300, 160, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelZ.setFont(font)
        self.LabelZ.setTextFormat(QtCore.Qt.PlainText)
        self.LabelZ.setScaledContents(False)
        self.LabelZ.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelZ.setWordWrap(False)
        self.LabelZ.setObjectName("LabelZ")
        self.LabelSpeed = QtWidgets.QLabel(Dialog)
        self.LabelSpeed.setGeometry(QtCore.QRect(290, 210, 111, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelSpeed.setFont(font)
        self.LabelSpeed.setAutoFillBackground(False)
        self.LabelSpeed.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelSpeed.setLineWidth(1)
        self.LabelSpeed.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelSpeed.setObjectName("LabelSpeed")
        self.XValue = QtWidgets.QLCDNumber(Dialog)
        self.XValue.setGeometry(QtCore.QRect(330, 80, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.XValue.setFont(font)
        self.XValue.setAutoFillBackground(False)
        self.XValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.XValue.setDigitCount(4)
        self.XValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.XValue.setObjectName("XValue")
        self.LabelY = QtWidgets.QLabel(Dialog)
        self.LabelY.setGeometry(QtCore.QRect(300, 120, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelY.setFont(font)
        self.LabelY.setTextFormat(QtCore.Qt.PlainText)
        self.LabelY.setScaledContents(False)
        self.LabelY.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelY.setWordWrap(False)
        self.LabelY.setObjectName("LabelY")
        self.LabelX = QtWidgets.QLabel(Dialog)
        self.LabelX.setGeometry(QtCore.QRect(300, 80, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelX.setFont(font)
        self.LabelX.setTextFormat(QtCore.Qt.PlainText)
        self.LabelX.setScaledContents(False)
        self.LabelX.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelX.setWordWrap(False)
        self.LabelX.setObjectName("LabelX")
        self.ZJog = QtWidgets.QLineEdit(Dialog)
        self.ZJog.setGeometry(QtCore.QRect(400, 160, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.ZJog.setFont(font)
        self.ZJog.setAlignment(QtCore.Qt.AlignCenter)
        self.ZJog.setObjectName("ZJog")
        self.speed = QtWidgets.QComboBox(Dialog)
        self.speed.setGeometry(QtCore.QRect(330, 240, 50, 22))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        
        
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        #tems to drop down menu
        self.speed.addItem("1")
        self.speed.addItem("2")
        self.speed.addItem("3")
        self.speed.addItem("4")
        self.speed.addItem("5")
        self.speed.setCurrentIndex(2)
        
        
        #keyboard shortcuts
        self.right_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("right"), Dialog)
        self.right_shortcut.activated.connect(lambda: tinyG.jog("X",0.5,200))
        self.right_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.left_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("left"), Dialog)
        self.left_shortcut.activated.connect(lambda: tinyG.jog("X",-0.5,200))
        self.left_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.up_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("up"), Dialog)
        self.up_shortcut.activated.connect(lambda: tinyG.jog("Y",0.5,200))
        self.up_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.down_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("down"), Dialog)
        self.down_shortcut.activated.connect(lambda: tinyG.jog("Y",-0.5,200))
        self.down_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.zero_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("PgDown"), Dialog)
        self.zero_shortcut.activated.connect(lambda: tinyG.jog("Z",-0.5,200))
        self.zero_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.one_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("PgUp"), Dialog)
        self.one_shortcut.activated.connect(lambda: tinyG.jog("Z",0.5,200))
        self.one_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        
        #pushbuttons events
        self.updatePosition(tinyG)
        self.GoButton.clicked.connect(lambda: self.callJog(tinyG))
        self.Next.clicked.connect(lambda: self.callHoleDrill(tinyG, probeCommands))
        self.Next.clicked.connect(lambda: self.openSelect_Cranial_Procedure(tinyG, probeCommands))
        self.Next.clicked.connect(Dialog.close)
        self.GoButton.setDefault(True)
        
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Hole Drilling", "Hole Drilling"))
        self.label_2.setText(_translate("Dialog", "Craniobot v1.0 Created at U. of Minnesota"))
        self.Title.setText(_translate("Dialog", "Anchor Screw Drilling"))
        self.Xoffset_Label_2.setText(_translate("Dialog", "X (mm)"))
        self.X_Hole.setText(_translate("Dialog", "0"))
        self.Y_Hole.setText(_translate("Dialog", "0"))
        self.Yoffset_label_2.setText(_translate("Dialog", "Y (mm)"))
        self.Next.setText(_translate("Dialog", "Next"))
        self.GoButton.setText(_translate("Dialog", "Go!"))
        self.label_3.setText(_translate("Dialog", "Set Position"))
        self.XJog.setText(_translate("Dialog", "0"))
        self.LabelJog.setText(_translate("Dialog", "Jog (mm)"))
        self.LabelPosition.setText(_translate("Dialog", "Position (mm)"))
        self.YJog.setText(_translate("Dialog", "0"))
        self.LabelZ.setText(_translate("Dialog", "Z"))
        self.LabelSpeed.setText(_translate("Dialog", "Speed (1-5)"))
        self.LabelY.setText(_translate("Dialog", "Y"))
        self.LabelX.setText(_translate("Dialog", "X"))
        self.ZJog.setText(_translate("Dialog", "0"))



# %%
class Ui_Circular_Craniotomy(object):
    def  openSelect_Cranial_Procedure(self, tinyG, probeCommands):
        self.window = QtWidgets.QDialog()
        self.uiSelect_Cranial_Procedure = Ui_Select_Cranial_Procedure(tinyG, probeCommands)
        self.uiSelect_Cranial_Procedure.setupUi(self.window)
        self.window.show()
        
    def callCircularCraniotomyGCode(self,tinyG, probeCommands):
        if(self.X_Center.text()):
            Xoff=float(self.X_Center.text())
        if(self.Y_Center.text()):
            Yoff=float(self.Y_Center.text())
        if(self.Diameter.text()):
            Diameter=float(self.Diameter.text())
            nPoints=int(3.1415*Diameter/0.5)
            print(nPoints)
            craniotomy_probe = GenerateCircularCraniotomy(Xoff,Yoff,Diameter,nPoints) #pass craniotomy_probe.gCode to next window
            parameter="X center = "+ str(Xoff)+"mm, Y center = "+str(Yoff)+ "mm, Diameter = "+str(Diameter)+ "mm"
            procedure=cranialProcedure("Circular Craniotomy", parameter, craniotomy_probe.gCode)
            probeCommands.append(procedure)
        
    def updatePosition(self, tinyG):
        
        tinyG.ser.write(b'{"pos":n}\n')
        pos=str(tinyG.ser.readlines())
        
        initIndex=pos.find("pos")+6
        finalIndex=pos.find("\"a\"")-1
        newPos=pos[initIndex:finalIndex]

        xaxis=int(newPos[newPos.find("x")+3:newPos.find(",")-4])
        newPos=newPos[newPos.find(",")+1:]
        yaxis=int(newPos[newPos.find("y")+3:newPos.find(",")-4])
        newPos=newPos[newPos.find(",")+1:]
        zaxis=int(newPos[newPos.find("z")+3:len(newPos)-4])
        
        self.XValue.display(xaxis)
        self.YValue.display(yaxis)
        self.ZValue.display(zaxis)
        
    def callJog(self, tinyG):
        XMove=0
        YMove=0
        ZMove=0
        speed=300
        if(self.ZJog.text()):
            ZMove=float(self.ZJog.text())
        if(self.XJog.text()):
            XMove=float(self.XJog.text())
        if(self.YJog.text()):
            YMove=float(self.YJog.text())
        
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        tinyG.jog("x", XMove, int(speed))
        self.updatePosition(tinyG)
        tinyG.jog("y", YMove, int(speed))
        self.updatePosition(tinyG)
        tinyG.jog("z", ZMove, int(speed))
        self.updatePosition(tinyG)
        
    def setupUi(self, Dialog, tinyG,probeCommands):
        Dialog.setObjectName("Dialog")
        Dialog.resize(504, 285)
        Dialog.setStyleSheet("#mainView, #calibration_tab, #mask_tab, #integration_tab {\n"
"    background: #3C3C3C;\n"
"    border: 5px solid #3C3C3C;\n"
"}\n"
"\n"
"QTabWidget::tab-bar{\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabWidget::pane {\n"
"    border:  1px solid #2F2F2F;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QWidget{\n"
"    color: #F1F1F1;\n"
"}\n"
"\n"
"\n"
"QTabBar::tab:left, QTabBar::tab:right {\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"    font: normal 14px;\n"
"    color: #F1F1F1;\n"
"    border-radius:2px;\n"
"\n"
"    padding: 0px;\n"
"    width: 20px;\n"
"    min-height:140px;\n"
"}\n"
"\n"
"\n"
"QTabBar::tab::top, QTabBar::tab::bottom {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"    border-right: 0px solid white;\n"
"    color: #F1F1F1;\n"
"    font: normal 11px;\n"
"    border-radius:2px;\n"
"    min-width: 65px;\n"
"    height: 19px;\n"
"    padding: 0px;\n"
"    margin-top: 1px;\n"
"    margin-right: 1px;\n"
" }\n"
"QTabBar::tab::left:last, QTabBar::tab::right:last{\n"
"    border-bottom-left-radius: 10px;\n"
"    border-bottom-right-radius: 10px;\n"
"}\n"
"QTabBar::tab:left:first, QTabBar::tab:right:first{\n"
"    border-top-left-radius: 10px;\n"
"    border-top-right-radius: 10px;\n"
"}\n"
"\n"
"QTabWidget, QTabWidget::tab-bar,  QTabWidget::panel, QWidget{\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"QTabWidget::tab-bar {\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabBar::tab:hover {\n"
"    border: 1px solid #ADADAD;\n"
"}\n"
"\n"
"QTabBar:tab:selected{\n"
"    background: qlineargradient(\n"
"            x1: 0, y1: 1,\n"
"            x2: 0, y2: 0,\n"
"            stop: 0 #727272,\n"
"            stop: 1 #444444\n"
"        );\n"
"    border:1px solid  rgb(255, 120,00);/*#ADADAD; */\n"
"}\n"
"\n"
"QTabBar::tab:bottom:last, QTabBar::tab:top:last{\n"
"    border-top-right-radius: 10px;\n"
"    border-bottom-right-radius: 10px;\n"
"}\n"
"QTabBar::tab:bottom:first, QTabBar::tab:top:first{\n"
"    border-top-left-radius: 10px;\n"
"    border-bottom-left-radius: 10px;\n"
"}\n"
"QTabBar::tab:top:!selected {\n"
"    margin-top: 1px;\n"
"    padding-top:1px;\n"
"}\n"
"QTabBar::tab:bottom:!selected{\n"
"    margin-bottom: 1px;\n"
"    padding-bottom:1px;\n"
"}\n"
"\n"
"QGraphicsView {\n"
"    border-style: none;\n"
"}\n"
"\n"
"QLabel , QCheckBox, QGroupBox, QRadioButton, QListWidget::item, QPushButton, QToolBox::tab, QSpinBox, QDoubleSpinBox , QComboBox{\n"
"    color: #F1F1F1;\n"
"    font-size: 12px;\n"
"}\n"
"QCheckBox{\n"
"    border-radius: 5px;\n"
"}\n"
"QRadioButton, QCheckBox {\n"
"    font-weight: normal;\n"
"    height: 15px;\n"
"}\n"
"\n"
"QLineEdit  {\n"
"    border-radius: 2px;\n"
"    background: #F1F1F1;\n"
"    color: black;\n"
"    height: 18 px;\n"
"}\n"
"\n"
"QLineEdit::focus{\n"
"    border-style: none;\n"
"    border-radius: 2px;\n"
"    background: #F1F1F1;\n"
"    color: black;\n"
"}\n"
"\n"
"QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled{\n"
"    color:rgb(148, 148, 148)\n"
"}\n"
"QSpinBox, QDoubleSpinBox {\n"
"    background-color:  #F1F1F1;\n"
"    color: black;\n"
"    /*margin-left: -15px;\n"
"    margin-right: -2px;*/\n"
"}\n"
"\n"
"QComboBox QAbstractItemView{\n"
"    background: #2D2D30;\n"
"    color: #F1F1F1;\n"
"    selection-background-color: rgba(221, 124, 40, 120);\n"
"    border-radius: 5px;\n"
"    min-height: 40px;\n"
"\n"
"}\n"
"\n"
"QComboBox QAbstractItemView:QScrollbar::vertical {\n"
"    width:100px;\n"
"}\n"
"\n"
"QComboBox:!editable {\n"
"    margin-left: 1px;\n"
"    padding: 0px 10px 0px 10px;\n"
"    height: 23px;\n"
"    background-color: #3C3C3C;\n"
"}\n"
"\n"
"QComboBox::item{\n"
"    background-color: #3C3C3C;\n"
"}\n"
"\n"
"QComboBox::item::selected {\n"
"    background-color: #505050;\n"
"}\n"
"QToolBox::tab:QToolButton{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"\n"
"    border-radius:2px;\n"
"    padding-right: 10px;\n"
"\n"
"    color: #F1F1F1;\n"
"    font-size: 12px;\n"
"    padding: 3px;\n"
"}\n"
"QToolBox::tab:QToolButton{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"     border: 1px solid  #5B5B5B;\n"
"\n"
"     border-radius:2px;\n"
"     padding-right: 10px;\n"
"\n"
"      color: #F1F1F1;\n"
"    font-size: 12px;\n"
"    padding: 3px;\n"
"}\n"
"\n"
"QPushButton{\n"
"    color: #F1F1F1;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop:1 #505050);\n"
"    border: 1px solid #5B5B5B;\n"
"    border-radius: 5px;\n"
"    padding-left: 8px;\n"
"    height: 18px;\n"
"    padding-right: 8px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    margin-top: 2px;\n"
"    margin-left: 2px;\n"
"}\n"
"\n"
"QPushButton::disabled{\n"
"}\n"
"\n"
"QPushButton::hover {\n"
"    border:1px solid #ADADAD;\n"
"}\n"
"\n"
"QPushButton::checked {\n"
"    background: qlineargradient(\n"
"        x1: 0, y1: 1,\n"
"        x2: 0, y2: 0,\n"
"        stop: 0 #727272,\n"
"        stop: 1 #444444\n"
"    );\n"
"     border:1px solid  rgb(255, 120,00);\n"
"}\n"
"\n"
"QPushButton::focus {\n"
"    outline: None;\n"
"}\n"
"QGroupBox {\n"
"    border: 1px solid #ADADAD;\n"
"    border-radius: 4px;\n"
"    margin-top: 7px;\n"
"    padding: 0px\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 20px\n"
"}\n"
"\n"
"QSplitter::handle:hover {\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"\n"
"QGraphicsView{\n"
"    border-style: none;\n"
"}\n"
"\n"
"QScrollBar:vertical {\n"
"    border: 2px solid #3C3C3C;\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    width: 12px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #969696, stop:1 #CACACA);\n"
"    border-radius: 3px;\n"
"    min-height: 20px;\n"
"    padding: 15px;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:vertical {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"    background: none;\n"
"}\n"
"\n"
"QScrollBar:horizontal {\n"
"    border: 2px solid #3C3C3C;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    height: 12 px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #969696, stop:1 #CACACA);\n"
"    border-radius: 3px;\n"
"    min-width: 20px;\n"
"    padding: 15px;\n"
"}\n"
"QScrollBar::add-line:horizontal {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:horizontal {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n"
"    background: none;\n"
"}\n"
"\n"
"QSplitterHandle:hover {}\n"
"\n"
"QSplitter::handle:vertical{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #505050, stop: 0.7 #3C3C3C);\n"
"    height: 15px;\n"
"}\n"
"\n"
"QSplitter::handle:vertical:pressed, QSplitter::handle:vertical:hover{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #5C5C5C, stop: 0.7 #3C3C3C);\n"
"}\n"
"\n"
"QSplitter::handle:horizontal{\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #505050, stop: 0.7 #3C3C3C);\n"
"    width: 15px;\n"
"}\n"
"\n"
"QSplitter::handle:horizontal:pressed, QSplitter::handle:horizontal:hover{\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #5C5C5C, stop: 0.7 #3C3C3C);\n"
"}\n"
"\n"
"QSplitter::handle:hover {\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    spacing: 10px;\n"
"    color: #F1F1F1;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    border: None;\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    font-size: 12px;\n"
"    text-align: center;\n"
"}\n"
"\n"
"QTableWidget QPushButton {\n"
"    margin: 5px;\n"
"}\n"
"\n"
"\n"
"QTableWidget QPushButton::pressed{\n"
"    margin-top: 7px;\n"
"    margin-left: 7px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(177,80,0,255), stop:1 rgba(255,120,0,255));\n"
"    selection-color: #F1F1F1;\n"
"}\n"
"\n"
"#phase_table_widget QCheckBox, #overlay_table_widget QCheckBox {\n"
"    margin-left: 5px;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox, #phase_table_widget QDoubleSpinBox {\n"
"    min-width: 50;\n"
"    max-width: 70;\n"
"    background: transparent;\n"
"    background-color: transparent;\n"
"    color:#D1D1D1;\n"
"    border: 1px solid transparent;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox:disabled, #phase_table_widget QDoubleSpinBox:disabled {\n"
"    color:#888;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button, #overlay_table_widget QDoubleSpinBox::down-button,\n"
"#phase_table_widget QDoubleSpinBox::up-button, #phase_table_widget QDoubleSpinBox::down-button {\n"
"    width: 11px;\n"
"    height: 9px;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop:1 #505050);\n"
"    border: 0.5px solid #5B5B5B;\n"
"    border-radius: 2px;\n"
"}\n"
"#overlay_table_widget QDoubleSpinBox::up-button:hover, #overlay_table_widget QDoubleSpinBox::down-button:hover,\n"
"#phase_table_widget QDoubleSpinBox::up-button:hover, #phase_table_widget QDoubleSpinBox::down-button:hover\n"
"{\n"
"    border:0.5px solid #ADADAD;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button:pressed,  #phase_table_widget QDoubleSpinBox::up-button:pressed{\n"
"    width: 10px;\n"
"    height: 8px;\n"
"}\n"
"#overlay_table_widget QDoubleSpinBox::down-button:pressed, #phase_table_widget QDoubleSpinBox::down-button:pressed {\n"
"    width: 10px;\n"
"    height: 8px;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button, #phase_table_widget QDoubleSpinBox::up-button {\n"
"    image: url(dioptas/resources/icons/arrow_up.ico) 1;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::down-button, #phase_table_widget QDoubleSpinBox::down-button {\n"
"    image: url(dioptas/resources/icons/arrow_down.ico) 1;\n"
"}\n"
"\n"
"QFrame#main_frame {\n"
"    color: #F1F1F1;\n"
"    border: 1px solid #5B5B5B;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"#calibration_mode_btn, #mask_mode_btn, #integration_mode_btn {\n"
"    font: normal 12px;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"#calibration_mode_btn {\n"
"   border-top-right-radius:8px;\n"
"   border-bottom-right-radius: 8px;\n"
"}\n"
"\n"
"#integration_mode_btn {\n"
"   border-top-left-radius:8px;\n"
"   border-bottom-left-radius: 8px;\n"
"}")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(270, -20, 21, 341))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.line.setFont(font)
        self.line.setAutoFillBackground(False)
        self.line.setStyleSheet("color: rgb(0, 0, 0);")
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(3)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setObjectName("line")
        self.Next = QtWidgets.QPushButton(Dialog)
        self.Next.setGeometry(QtCore.QRect(140, 170, 61, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Next.setFont(font)
        self.Next.setObjectName("Next")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(50, 20, 161, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 260, 211, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.GetDiameter = QtWidgets.QLabel(Dialog)
        self.GetDiameter.setGeometry(QtCore.QRect(50, 140, 91, 16))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.GetDiameter.setFont(font)
        self.GetDiameter.setObjectName("GetDiameter")
        self.Xoffset_Label = QtWidgets.QLabel(Dialog)
        self.Xoffset_Label.setGeometry(QtCore.QRect(50, 80, 91, 16))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Xoffset_Label.setFont(font)
        self.Xoffset_Label.setObjectName("Xoffset_Label")
        self.Yoffset_label = QtWidgets.QLabel(Dialog)
        self.Yoffset_label.setGeometry(QtCore.QRect(50, 110, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Yoffset_label.setFont(font)
        self.Yoffset_label.setObjectName("Yoffset_label")
        self.X_Center = QtWidgets.QLineEdit(Dialog)
        self.X_Center.setGeometry(QtCore.QRect(140, 80, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.X_Center.setFont(font)
        self.X_Center.setAlignment(QtCore.Qt.AlignCenter)
        self.X_Center.setObjectName("X_Center")
        self.Y_Center = QtWidgets.QLineEdit(Dialog)
        self.Y_Center.setGeometry(QtCore.QRect(140, 110, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.Y_Center.setFont(font)
        self.Y_Center.setAlignment(QtCore.Qt.AlignCenter)
        self.Y_Center.setObjectName("Y_Center")
        self.Diameter = QtWidgets.QLineEdit(Dialog)
        self.Diameter.setGeometry(QtCore.QRect(140, 140, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.Diameter.setFont(font)
        self.Diameter.setAlignment(QtCore.Qt.AlignCenter)
        self.Diameter.setObjectName("Diameter")
        self.GoButton = QtWidgets.QPushButton(Dialog)
        self.GoButton.setGeometry(QtCore.QRect(400, 210, 61, 51))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.GoButton.setFont(font)
        self.GoButton.setObjectName("GoButton")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(340, 20, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.ZValue = QtWidgets.QLCDNumber(Dialog)
        self.ZValue.setGeometry(QtCore.QRect(330, 160, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.ZValue.setFont(font)
        self.ZValue.setAutoFillBackground(False)
        self.ZValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.ZValue.setDigitCount(4)
        self.ZValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.ZValue.setObjectName("ZValue")
        self.XJog = QtWidgets.QLineEdit(Dialog)
        self.XJog.setGeometry(QtCore.QRect(400, 80, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.XJog.setFont(font)
        self.XJog.setAlignment(QtCore.Qt.AlignCenter)
        self.XJog.setObjectName("XJog")
        self.LabelJog = QtWidgets.QLabel(Dialog)
        self.LabelJog.setGeometry(QtCore.QRect(390, 50, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelJog.setFont(font)
        self.LabelJog.setAutoFillBackground(False)
        self.LabelJog.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelJog.setLineWidth(1)
        self.LabelJog.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelJog.setObjectName("LabelJog")
        self.LabelPosition = QtWidgets.QLabel(Dialog)
        self.LabelPosition.setGeometry(QtCore.QRect(290, 50, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelPosition.setFont(font)
        self.LabelPosition.setAutoFillBackground(False)
        self.LabelPosition.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelPosition.setLineWidth(1)
        self.LabelPosition.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelPosition.setObjectName("LabelPosition")
        self.YValue = QtWidgets.QLCDNumber(Dialog)
        self.YValue.setGeometry(QtCore.QRect(330, 120, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.YValue.setFont(font)
        self.YValue.setAutoFillBackground(False)
        self.YValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.YValue.setDigitCount(4)
        self.YValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.YValue.setObjectName("YValue")
        self.YJog = QtWidgets.QLineEdit(Dialog)
        self.YJog.setGeometry(QtCore.QRect(400, 120, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.YJog.setFont(font)
        self.YJog.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.YJog.setAlignment(QtCore.Qt.AlignCenter)
        self.YJog.setObjectName("YJog")
        self.LabelZ = QtWidgets.QLabel(Dialog)
        self.LabelZ.setGeometry(QtCore.QRect(300, 160, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelZ.setFont(font)
        self.LabelZ.setTextFormat(QtCore.Qt.PlainText)
        self.LabelZ.setScaledContents(False)
        self.LabelZ.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelZ.setWordWrap(False)
        self.LabelZ.setObjectName("LabelZ")
        self.LabelSpeed = QtWidgets.QLabel(Dialog)
        self.LabelSpeed.setGeometry(QtCore.QRect(290, 210, 111, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelSpeed.setFont(font)
        self.LabelSpeed.setAutoFillBackground(False)
        self.LabelSpeed.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelSpeed.setLineWidth(1)
        self.LabelSpeed.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelSpeed.setObjectName("LabelSpeed")
        self.XValue = QtWidgets.QLCDNumber(Dialog)
        self.XValue.setGeometry(QtCore.QRect(330, 80, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.XValue.setFont(font)
        self.XValue.setAutoFillBackground(False)
        self.XValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.XValue.setDigitCount(4)
        self.XValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.XValue.setObjectName("XValue")
        self.LabelY = QtWidgets.QLabel(Dialog)
        self.LabelY.setGeometry(QtCore.QRect(300, 120, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelY.setFont(font)
        self.LabelY.setTextFormat(QtCore.Qt.PlainText)
        self.LabelY.setScaledContents(False)
        self.LabelY.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelY.setWordWrap(False)
        self.LabelY.setObjectName("LabelY")
        self.LabelX = QtWidgets.QLabel(Dialog)
        self.LabelX.setGeometry(QtCore.QRect(300, 80, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelX.setFont(font)
        self.LabelX.setTextFormat(QtCore.Qt.PlainText)
        self.LabelX.setScaledContents(False)
        self.LabelX.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelX.setWordWrap(False)
        self.LabelX.setObjectName("LabelX")
        self.ZJog = QtWidgets.QLineEdit(Dialog)
        self.ZJog.setGeometry(QtCore.QRect(400, 160, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.ZJog.setFont(font)
        self.ZJog.setAlignment(QtCore.Qt.AlignCenter)
        self.ZJog.setObjectName("ZJog")
        self.speed = QtWidgets.QComboBox(Dialog)
        self.speed.setGeometry(QtCore.QRect(330, 240, 50, 22))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        
        #add items to drop down menu
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        self.speed.addItem("1")
        self.speed.addItem("2")
        self.speed.addItem("3")
        self.speed.addItem("4")
        self.speed.addItem("5")
        self.speed.setCurrentIndex(2)
        
        #keyboard shortcuts
        self.right_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("right"), Dialog)
        self.right_shortcut.activated.connect(lambda: tinyG.jog("X",0.5,200))
        self.right_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.left_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("left"), Dialog)
        self.left_shortcut.activated.connect(lambda: tinyG.jog("X",-0.5,200))
        self.left_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.up_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("up"), Dialog)
        self.up_shortcut.activated.connect(lambda: tinyG.jog("Y",0.5,200))
        self.up_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.down_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("down"), Dialog)
        self.down_shortcut.activated.connect(lambda: tinyG.jog("Y",-0.5,200))
        self.down_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.zero_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("PgDown"), Dialog)
        self.zero_shortcut.activated.connect(lambda: tinyG.jog("Z",-0.5,200))
        self.zero_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.one_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("PgUp"), Dialog)
        self.one_shortcut.activated.connect(lambda: tinyG.jog("Z",0.5,200))
        self.one_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        
        #pushbuttons events
        self.updatePosition(tinyG)
        self.GoButton.clicked.connect(lambda: self.callJog(tinyG))
        self.GoButton.setDefault(True)
        self.Next.clicked.connect(lambda: self.callCircularCraniotomyGCode(tinyG, probeCommands))
        self.Next.clicked.connect(lambda: self.openSelect_Cranial_Procedure(tinyG, probeCommands))
        self.Next.clicked.connect(Dialog.close)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)  
        # -DanielEnd

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Circular Craniotomy"))
        self.Next.setText(_translate("Dialog", "Next"))
        self.label_4.setText(_translate("Dialog", "Circular Craniotomy "))
        self.label_2.setText(_translate("Dialog", "Craniobot v1.0 Created at U. of Minnesota"))
        self.GetDiameter.setText(_translate("Dialog", "Diameter (mm)"))
        self.Xoffset_Label.setText(_translate("Dialog", "X (mm)"))
        self.Yoffset_label.setText(_translate("Dialog", "Y (mm)"))
        self.X_Center.setText(_translate("Dialog", "0"))
        self.Y_Center.setText(_translate("Dialog", "0"))
        self.Diameter.setText(_translate("Dialog", "0"))
        self.GoButton.setText(_translate("Dialog", "Go!"))
        self.label_3.setText(_translate("Dialog", "Set Position"))
        self.XJog.setText(_translate("Dialog", "0"))
        self.LabelJog.setText(_translate("Dialog", "Jog (mm)"))
        self.LabelPosition.setText(_translate("Dialog", "Position (mm)"))
        self.YJog.setText(_translate("Dialog", "0"))
        self.LabelZ.setText(_translate("Dialog", "Z"))
        self.LabelSpeed.setText(_translate("Dialog", "Speed (1-5)"))
        self.LabelY.setText(_translate("Dialog", "Y"))
        self.LabelX.setText(_translate("Dialog", "X"))
        self.ZJog.setText(_translate("Dialog", "0"))

#%%
class Ui_SetXYZ_Origin(object):
    #surface profiling step
    
    def callJog(self, tinyG):
        XMove=0
        YMove=0
        ZMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        if(self.ZJog.text()):
            ZMove=float(self.ZJog.text())
            tinyG.jog("z", ZMove, int(speed))  
        if(self.XJog.text()):
            XMove=float(self.XJog.text())
            tinyG.jog("x", XMove, int(speed))
        if(self.YJog.text()):
            YMove=float(self.YJog.text())
            tinyG.jog("y", YMove, int(speed))
        
        time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3):
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
    
    def callJogX(self,tinyG):
        XMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        if(self.XJog.text()):
            XMove=float(self.XJog.text())
            tinyG.jog("x", XMove, int(speed))
            time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
        
    def callJogY(self,tinyG):
        YMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        if(self.YJog.text()):
            YMove=float(self.YJog.text())
            tinyG.jog("y", YMove, int(speed))
            time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
        
    def callJogZ(self,tinyG):
        ZMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        if(self.ZJog.text()):
            ZMove=float(self.ZJog.text())
            tinyG.jog("z", ZMove, int(speed))
            time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
        
    def updatePosition(self, tinyG):
        tinyG.ser.write(b'{"pos":n}\n')
        pos=str(tinyG.ser.readlines())
        
        initIndex=pos.find("pos")+6
        finalIndex=pos.find("\"a\"")-1
        newPos=pos[initIndex:finalIndex]

        xaxis=int(newPos[newPos.find("x")+3:newPos.find(",")-4])
        newPos=newPos[newPos.find(",")+1:]
        yaxis=int(newPos[newPos.find("y")+3:newPos.find(",")-4])
        newPos=newPos[newPos.find(",")+1:]
        zaxis=int(newPos[newPos.find("z")+3:len(newPos)-4])
        
        self.XValue.display(xaxis)
        self.YValue.display(yaxis)
        self.ZValue.display(zaxis)
    
    def  firstProbe(self, tinyG, probeCommands):
        #runs first probe and stops upon contact
        tinyG.runSingleProbe()
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        while(stat.find("stat")<0):
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            time.sleep(1)
        self.updatePosition(tinyG)
    
    def  setOrig(self, tinyG, probeCommands):
        #sets the origin, to be used after run first probe
        tinyG.setOrigin()
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        while(stat.find("stat")<0):
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            time.sleep(1)
        self.updatePosition(tinyG)
    
    def  openInstructions(self):
        self.window = QtWidgets.QDialog()
        self.uiI_Probing = Ui_I_Probing()
        self.uiI_Probing.setupUi(self.window)
        self.window.show()
    
    def  openMillingConfig(self, tinyG, probeCommands):
        #open milling step after surface profiling step is completed
        self.window = QtWidgets.QDialog()
        self.uiMillingConfig = Ui_MillingConfig()
        self.uiMillingConfig.setupUi(self.window, tinyG, probeCommands)
        self.window.show()
        
    def  runProbing(self, tinyG, probeCommands):
        #run probing routine for all cranial procedures in the list that haven't been probed yet
        millingPaths=[]
        for i in probeCommands:
            if(i.probed==0): #if not probed yet
                tinyG.runProbe(i.gCode_out)
                time.sleep(1)
                tinyG.ser.write(b'{"stat":n}\n')
                stat=str(tinyG.ser.readlines())
                val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
                while(val!=3 and val!=4):
                    tinyG.ser.write(b'{"stat":n}\n')
                    stat=str(tinyG.ser.readlines())
                    val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
                    time.sleep(1)
                self.updatePosition(tinyG)
                self.updatePosition(tinyG)
                i.millingPath=tinyG.probe_output
                i.millingDepth=0
                i.probed=1
                millingPaths.append(tinyG.probe_output)
        
        counter=0
        for i in probeCommands:
            self.millCoords = list([[],[],[],[]])
            x = i.millingPath[0]["r"]["prb"]["x"]
            y = i.millingPath[0]["r"]["prb"]["y"]
            for item in i.millingPath:
                #extract xyz coordinates for each point in the milling path
                x = item["r"]["prb"]["x"]
                y = item["r"]["prb"]["y"]
                z = item["r"]["prb"]["z"]
                self.millCoords[0].append(x)
                self.millCoords[1].append(y)
                self.millCoords[2].append(z)
            #Final step is to return to the starting point of the contour
            x = i.millingPath[0]["r"]["prb"]["x"]
            y = i.millingPath[0]["r"]["prb"]["y"]
            z = i.millingPath[0]["r"]["prb"]["z"]
            self.millCoords[0].append(x)
            self.millCoords[1].append(y)
            self.millCoords[2].append(z)
            #create scatter with all milling coordinates
            trace1 = go.Scatter3d(
            x=self.millCoords[0],
            y=self.millCoords[1],
            z=self.millCoords[2],
            #graphics setup
            mode='lines+markers',
            marker=dict(size=4,line=dict(color='rgba(217, 217, 217, 0.14)',width=0.5),opacity=0.8))
            data = [trace1]
            layout = go.Layout(margin=dict(l=0,r=0,b=0,t=0))
    
            counter=counter+1 #allows for multiple files
            fig = go.Figure(data=data, layout=layout)
            py.offline.plot(fig, filename='mill_path'+str(counter)+'.html')
        self.openMillingConfig(tinyG, probeCommands)
        
    def  removeProcedure(self, Dialog, probeCommands):
        if(self.removeNumber.text()):
            removeN=(int(self.removeNumber.text()))
        if (removeN>0):
            del probeCommands[removeN-1] #deletes a probe command from the list
        self.retranslateUi(Dialog, probeCommands)
    
    def  openSelect_Cranial_Procedure(self, tinyG, probeCommands):
        self.window = QtWidgets.QDialog()
        self.uiSelect_Cranial_Procedure = Ui_Select_Cranial_Procedure(tinyG, probeCommands)
        self.uiSelect_Cranial_Procedure.setupUi(self.window)
        self.window.show()
     
    def serialCommand(self,tinyG):
        if(self.gcodeManual.text()):
            com=str(self.gcodeManual.text())
            command = '{{"gc":"{}"}}\n'.format(com)
            tinyG.ser.write(command.encode('utf-8'))
        time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG) 

    def setupUi(self, Dialog, tinyG, probeCommands):
        Dialog.setObjectName("Dialog")
        Dialog.resize(719, 343)
        Dialog.setStyleSheet("#mainView, #calibration_tab, #mask_tab, #integration_tab {\n"
"    background: #3C3C3C;\n"
"    border: 5px solid #3C3C3C;\n"
"}\n"
"\n"
"QTabWidget::tab-bar{\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabWidget::pane {\n"
"    border:  1px solid #2F2F2F;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QWidget{\n"
"    color: #F1F1F1;\n"
"}\n"
"\n"
"\n"
"QTabBar::tab:left, QTabBar::tab:right {\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"    font: normal 14px;\n"
"    color: #F1F1F1;\n"
"    border-radius:2px;\n"
"\n"
"    padding: 0px;\n"
"    width: 20px;\n"
"    min-height:140px;\n"
"}\n"
"\n"
"\n"
"QTabBar::tab::top, QTabBar::tab::bottom {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"    border-right: 0px solid white;\n"
"    color: #F1F1F1;\n"
"    font: normal 11px;\n"
"    border-radius:2px;\n"
"    min-width: 65px;\n"
"    height: 19px;\n"
"    padding: 0px;\n"
"    margin-top: 1px;\n"
"    margin-right: 1px;\n"
" }\n"
"QTabBar::tab::left:last, QTabBar::tab::right:last{\n"
"    border-bottom-left-radius: 10px;\n"
"    border-bottom-right-radius: 10px;\n"
"}\n"
"QTabBar::tab:left:first, QTabBar::tab:right:first{\n"
"    border-top-left-radius: 10px;\n"
"    border-top-right-radius: 10px;\n"
"}\n"
"\n"
"QTabWidget, QTabWidget::tab-bar,  QTabWidget::panel, QWidget{\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"QTabWidget::tab-bar {\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabBar::tab:hover {\n"
"    border: 1px solid #ADADAD;\n"
"}\n"
"\n"
"QTabBar:tab:selected{\n"
"    background: qlineargradient(\n"
"            x1: 0, y1: 1,\n"
"            x2: 0, y2: 0,\n"
"            stop: 0 #727272,\n"
"            stop: 1 #444444\n"
"        );\n"
"    border:1px solid  rgb(255, 120,00);/*#ADADAD; */\n"
"}\n"
"\n"
"QTabBar::tab:bottom:last, QTabBar::tab:top:last{\n"
"    border-top-right-radius: 10px;\n"
"    border-bottom-right-radius: 10px;\n"
"}\n"
"QTabBar::tab:bottom:first, QTabBar::tab:top:first{\n"
"    border-top-left-radius: 10px;\n"
"    border-bottom-left-radius: 10px;\n"
"}\n"
"QTabBar::tab:top:!selected {\n"
"    margin-top: 1px;\n"
"    padding-top:1px;\n"
"}\n"
"QTabBar::tab:bottom:!selected{\n"
"    margin-bottom: 1px;\n"
"    padding-bottom:1px;\n"
"}\n"
"\n"
"QGraphicsView {\n"
"    border-style: none;\n"
"}\n"
"\n"
"QLabel , QCheckBox, QGroupBox, QRadioButton, QListWidget::item, QPushButton, QToolBox::tab, QSpinBox, QDoubleSpinBox , QComboBox{\n"
"    color: #F1F1F1;\n"
"    font-size: 12px;\n"
"}\n"
"QCheckBox{\n"
"    border-radius: 5px;\n"
"}\n"
"QRadioButton, QCheckBox {\n"
"    font-weight: normal;\n"
"    height: 15px;\n"
"}\n"
"\n"
"QLineEdit  {\n"
"    border-radius: 2px;\n"
"    background: #F1F1F1;\n"
"    color: black;\n"
"    height: 18 px;\n"
"}\n"
"\n"
"QLineEdit::focus{\n"
"    border-style: none;\n"
"    border-radius: 2px;\n"
"    background: #F1F1F1;\n"
"    color: black;\n"
"}\n"
"\n"
"QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled{\n"
"    color:rgb(148, 148, 148)\n"
"}\n"
"QSpinBox, QDoubleSpinBox {\n"
"    background-color:  #F1F1F1;\n"
"    color: black;\n"
"    /*margin-left: -15px;\n"
"    margin-right: -2px;*/\n"
"}\n"
"\n"
"QComboBox QAbstractItemView{\n"
"    background: #2D2D30;\n"
"    color: #F1F1F1;\n"
"    selection-background-color: rgba(221, 124, 40, 120);\n"
"    border-radius: 5px;\n"
"    min-height: 40px;\n"
"\n"
"}\n"
"\n"
"QComboBox QAbstractItemView:QScrollbar::vertical {\n"
"    width:100px;\n"
"}\n"
"\n"
"QComboBox:!editable {\n"
"    margin-left: 1px;\n"
"    padding: 0px 10px 0px 10px;\n"
"    height: 23px;\n"
"    background-color: #3C3C3C;\n"
"}\n"
"\n"
"QComboBox::item{\n"
"    background-color: #3C3C3C;\n"
"}\n"
"\n"
"QComboBox::item::selected {\n"
"    background-color: #505050;\n"
"}\n"
"QToolBox::tab:QToolButton{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"\n"
"    border-radius:2px;\n"
"    padding-right: 10px;\n"
"\n"
"    color: #F1F1F1;\n"
"    font-size: 12px;\n"
"    padding: 3px;\n"
"}\n"
"QToolBox::tab:QToolButton{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"     border: 1px solid  #5B5B5B;\n"
"\n"
"     border-radius:2px;\n"
"     padding-right: 10px;\n"
"\n"
"      color: #F1F1F1;\n"
"    font-size: 12px;\n"
"    padding: 3px;\n"
"}\n"
"\n"
"QPushButton{\n"
"    color: #F1F1F1;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop:1 #505050);\n"
"    border: 1px solid #5B5B5B;\n"
"    border-radius: 5px;\n"
"    padding-left: 8px;\n"
"    height: 18px;\n"
"    padding-right: 8px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    margin-top: 2px;\n"
"    margin-left: 2px;\n"
"}\n"
"\n"
"QPushButton::disabled{\n"
"}\n"
"\n"
"QPushButton::hover {\n"
"    border:1px solid #ADADAD;\n"
"}\n"
"\n"
"QPushButton::checked {\n"
"    background: qlineargradient(\n"
"        x1: 0, y1: 1,\n"
"        x2: 0, y2: 0,\n"
"        stop: 0 #727272,\n"
"        stop: 1 #444444\n"
"    );\n"
"     border:1px solid  rgb(255, 120,00);\n"
"}\n"
"\n"
"QPushButton::focus {\n"
"    outline: None;\n"
"}\n"
"QGroupBox {\n"
"    border: 1px solid #ADADAD;\n"
"    border-radius: 4px;\n"
"    margin-top: 7px;\n"
"    padding: 0px\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 20px\n"
"}\n"
"\n"
"QSplitter::handle:hover {\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"\n"
"QGraphicsView{\n"
"    border-style: none;\n"
"}\n"
"\n"
"QScrollBar:vertical {\n"
"    border: 2px solid #3C3C3C;\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    width: 12px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #969696, stop:1 #CACACA);\n"
"    border-radius: 3px;\n"
"    min-height: 20px;\n"
"    padding: 15px;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:vertical {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"    background: none;\n"
"}\n"
"\n"
"QScrollBar:horizontal {\n"
"    border: 2px solid #3C3C3C;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    height: 12 px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #969696, stop:1 #CACACA);\n"
"    border-radius: 3px;\n"
"    min-width: 20px;\n"
"    padding: 15px;\n"
"}\n"
"QScrollBar::add-line:horizontal {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:horizontal {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n"
"    background: none;\n"
"}\n"
"\n"
"QSplitterHandle:hover {}\n"
"\n"
"QSplitter::handle:vertical{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #505050, stop: 0.7 #3C3C3C);\n"
"    height: 15px;\n"
"}\n"
"\n"
"QSplitter::handle:vertical:pressed, QSplitter::handle:vertical:hover{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #5C5C5C, stop: 0.7 #3C3C3C);\n"
"}\n"
"\n"
"QSplitter::handle:horizontal{\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #505050, stop: 0.7 #3C3C3C);\n"
"    width: 15px;\n"
"}\n"
"\n"
"QSplitter::handle:horizontal:pressed, QSplitter::handle:horizontal:hover{\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #5C5C5C, stop: 0.7 #3C3C3C);\n"
"}\n"
"\n"
"QSplitter::handle:hover {\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    spacing: 10px;\n"
"    color: #F1F1F1;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    border: None;\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    font-size: 12px;\n"
"    text-align: center;\n"
"}\n"
"\n"
"QTableWidget QPushButton {\n"
"    margin: 5px;\n"
"}\n"
"\n"
"\n"
"QTableWidget QPushButton::pressed{\n"
"    margin-top: 7px;\n"
"    margin-left: 7px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(177,80,0,255), stop:1 rgba(255,120,0,255));\n"
"    selection-color: #F1F1F1;\n"
"}\n"
"\n"
"#phase_table_widget QCheckBox, #overlay_table_widget QCheckBox {\n"
"    margin-left: 5px;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox, #phase_table_widget QDoubleSpinBox {\n"
"    min-width: 50;\n"
"    max-width: 70;\n"
"    background: transparent;\n"
"    background-color: transparent;\n"
"    color:#D1D1D1;\n"
"    border: 1px solid transparent;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox:disabled, #phase_table_widget QDoubleSpinBox:disabled {\n"
"    color:#888;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button, #overlay_table_widget QDoubleSpinBox::down-button,\n"
"#phase_table_widget QDoubleSpinBox::up-button, #phase_table_widget QDoubleSpinBox::down-button {\n"
"    width: 11px;\n"
"    height: 9px;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop:1 #505050);\n"
"    border: 0.5px solid #5B5B5B;\n"
"    border-radius: 2px;\n"
"}\n"
"#overlay_table_widget QDoubleSpinBox::up-button:hover, #overlay_table_widget QDoubleSpinBox::down-button:hover,\n"
"#phase_table_widget QDoubleSpinBox::up-button:hover, #phase_table_widget QDoubleSpinBox::down-button:hover\n"
"{\n"
"    border:0.5px solid #ADADAD;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button:pressed,  #phase_table_widget QDoubleSpinBox::up-button:pressed{\n"
"    width: 10px;\n"
"    height: 8px;\n"
"}\n"
"#overlay_table_widget QDoubleSpinBox::down-button:pressed, #phase_table_widget QDoubleSpinBox::down-button:pressed {\n"
"    width: 10px;\n"
"    height: 8px;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button, #phase_table_widget QDoubleSpinBox::up-button {\n"
"    image: url(dioptas/resources/icons/arrow_up.ico) 1;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::down-button, #phase_table_widget QDoubleSpinBox::down-button {\n"
"    image: url(dioptas/resources/icons/arrow_down.ico) 1;\n"
"}\n"
"\n"
"QFrame#main_frame {\n"
"    color: #F1F1F1;\n"
"    border: 1px solid #5B5B5B;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"#calibration_mode_btn, #mask_mode_btn, #integration_mode_btn {\n"
"    font: normal 12px;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"#calibration_mode_btn {\n"
"   border-top-right-radius:8px;\n"
"   border-bottom-right-radius: 8px;\n"
"}\n"
"\n"
"#integration_mode_btn {\n"
"   border-top-left-radius:8px;\n"
"   border-bottom-left-radius: 8px;\n"
"}")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(410, -20, 21, 371))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.line.setFont(font)
        self.line.setAutoFillBackground(False)
        self.line.setStyleSheet("color: rgb(0, 0, 0);")
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(1)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setObjectName("line")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(100, 20, 261, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 310, 241, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.runProbe = QtWidgets.QPushButton(Dialog)
        self.runProbe.setGeometry(QtCore.QRect(10, 240, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.runProbe.setFont(font)
        self.runProbe.setObjectName("runProbe")
        self.singleProbe = QtWidgets.QPushButton(Dialog)
        self.singleProbe.setGeometry(QtCore.QRect(10, 160, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.singleProbe.setFont(font)
        self.singleProbe.setObjectName("singleProbe")
        self.instructionText = QtWidgets.QPlainTextEdit(Dialog)
        self.instructionText.setGeometry(QtCore.QRect(210, 60, 191, 231))
        self.instructionText.setObjectName("instructionText")
        self.removeButton = QtWidgets.QPushButton(Dialog)
        self.removeButton.setGeometry(QtCore.QRect(10, 80, 141, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.removeButton.setFont(font)
        self.removeButton.setObjectName("removeButton")
        self.removeNumber = QtWidgets.QLineEdit(Dialog)
        self.removeNumber.setGeometry(QtCore.QRect(160, 80, 31, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.removeNumber.setFont(font)
        self.removeNumber.setAlignment(QtCore.Qt.AlignCenter)
        self.removeNumber.setObjectName("removeNumber")
        self.addProcedures = QtWidgets.QPushButton(Dialog)
        self.addProcedures.setGeometry(QtCore.QRect(10, 120, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.addProcedures.setFont(font)
        self.addProcedures.setObjectName("addProcedures")
        self.XJog = QtWidgets.QLineEdit(Dialog)
        self.XJog.setGeometry(QtCore.QRect(580, 80, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.XJog.setFont(font)
        self.XJog.setAlignment(QtCore.Qt.AlignCenter)
        self.XJog.setObjectName("XJog")
        self.YJog = QtWidgets.QLineEdit(Dialog)
        self.YJog.setGeometry(QtCore.QRect(580, 120, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.YJog.setFont(font)
        self.YJog.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.YJog.setAlignment(QtCore.Qt.AlignCenter)
        self.YJog.setObjectName("YJog")
        self.LabelJog = QtWidgets.QLabel(Dialog)
        self.LabelJog.setGeometry(QtCore.QRect(570, 50, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelJog.setFont(font)
        self.LabelJog.setAutoFillBackground(False)
        self.LabelJog.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelJog.setLineWidth(1)
        self.LabelJog.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelJog.setObjectName("LabelJog")
        self.LabelPosition = QtWidgets.QLabel(Dialog)
        self.LabelPosition.setGeometry(QtCore.QRect(470, 50, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelPosition.setFont(font)
        self.LabelPosition.setAutoFillBackground(False)
        self.LabelPosition.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelPosition.setLineWidth(1)
        self.LabelPosition.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelPosition.setObjectName("LabelPosition")
        self.LabelY = QtWidgets.QLabel(Dialog)
        self.LabelY.setGeometry(QtCore.QRect(480, 120, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelY.setFont(font)
        self.LabelY.setTextFormat(QtCore.Qt.PlainText)
        self.LabelY.setScaledContents(False)
        self.LabelY.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelY.setWordWrap(False)
        self.LabelY.setObjectName("LabelY")
        self.GoButton = QtWidgets.QPushButton(Dialog)
        self.GoButton.setGeometry(QtCore.QRect(580, 210, 61, 51))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.GoButton.setFont(font)
        self.GoButton.setObjectName("GoButton")
        self.YValue = QtWidgets.QLCDNumber(Dialog)
        self.YValue.setGeometry(QtCore.QRect(510, 120, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.YValue.setFont(font)
        self.YValue.setAutoFillBackground(False)
        self.YValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.YValue.setDigitCount(4)
        self.YValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.YValue.setObjectName("YValue")
        self.LabelZ = QtWidgets.QLabel(Dialog)
        self.LabelZ.setGeometry(QtCore.QRect(480, 160, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelZ.setFont(font)
        self.LabelZ.setTextFormat(QtCore.Qt.PlainText)
        self.LabelZ.setScaledContents(False)
        self.LabelZ.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelZ.setWordWrap(False)
        self.LabelZ.setObjectName("LabelZ")
        self.LabelSpeed = QtWidgets.QLabel(Dialog)
        self.LabelSpeed.setGeometry(QtCore.QRect(470, 210, 111, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelSpeed.setFont(font)
        self.LabelSpeed.setAutoFillBackground(False)
        self.LabelSpeed.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelSpeed.setLineWidth(1)
        self.LabelSpeed.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelSpeed.setObjectName("LabelSpeed")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(520, 20, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.XValue = QtWidgets.QLCDNumber(Dialog)
        self.XValue.setGeometry(QtCore.QRect(510, 80, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.XValue.setFont(font)
        self.XValue.setAutoFillBackground(False)
        self.XValue.setStyleSheet("\n"
"background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"\n"
"")
        self.XValue.setDigitCount(4)
        self.XValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.XValue.setObjectName("XValue")
        self.ZValue = QtWidgets.QLCDNumber(Dialog)
        self.ZValue.setGeometry(QtCore.QRect(510, 160, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.ZValue.setFont(font)
        self.ZValue.setAutoFillBackground(False)
        self.ZValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;")
        self.ZValue.setDigitCount(4)
        self.ZValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.ZValue.setObjectName("ZValue")
        self.LabelX = QtWidgets.QLabel(Dialog)
        self.LabelX.setGeometry(QtCore.QRect(480, 80, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelX.setFont(font)
        self.LabelX.setTextFormat(QtCore.Qt.PlainText)
        self.LabelX.setScaledContents(False)
        self.LabelX.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelX.setWordWrap(False)
        self.LabelX.setObjectName("LabelX")
        self.ZJog = QtWidgets.QLineEdit(Dialog)
        self.ZJog.setGeometry(QtCore.QRect(580, 160, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.ZJog.setFont(font)
        self.ZJog.setAlignment(QtCore.Qt.AlignCenter)
        self.ZJog.setObjectName("ZJog")
        self.Instructions = QtWidgets.QPushButton(Dialog)
        self.Instructions.setGeometry(QtCore.QRect(380, 20, 31, 21))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.Instructions.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Instructions.setFont(font)
        self.Instructions.setStyleSheet("QPushButton{\n"
"background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"border-radius: 10px;\n"
"}")
        self.Instructions.setObjectName("Instructions")
        self.speed = QtWidgets.QComboBox(Dialog)
        self.speed.setGeometry(QtCore.QRect(510, 240, 50, 22))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        self.setOrigin = QtWidgets.QPushButton(Dialog)
        self.setOrigin.setGeometry(QtCore.QRect(10, 200, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.setOrigin.setFont(font)
        self.setOrigin.setObjectName("setOrigin")
        self.gcodeManual = QtWidgets.QLineEdit(Dialog)
        self.gcodeManual.setGeometry(QtCore.QRect(460, 300, 161, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.gcodeManual.setFont(font)
        self.gcodeManual.setText("")
        self.gcodeManual.setAlignment(QtCore.Qt.AlignCenter)
        self.gcodeManual.setObjectName("gcodeManual")
        self.LabelGcode = QtWidgets.QLabel(Dialog)
        self.LabelGcode.setGeometry(QtCore.QRect(480, 280, 111, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelGcode.setFont(font)
        self.LabelGcode.setAutoFillBackground(False)
        self.LabelGcode.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelGcode.setLineWidth(1)
        self.LabelGcode.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelGcode.setObjectName("LabelGcode")
        self.SendButton = QtWidgets.QPushButton(Dialog)
        self.SendButton.setGeometry(QtCore.QRect(630, 300, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.SendButton.setFont(font)
        self.SendButton.setObjectName("SendButton")
        self.goX = QtWidgets.QPushButton(Dialog)
        self.goX.setGeometry(QtCore.QRect(650, 80, 51, 21))
        self.goX.setStyleSheet("")
        self.goX.setObjectName("goX")
        self.goY = QtWidgets.QPushButton(Dialog)
        self.goY.setGeometry(QtCore.QRect(650, 120, 51, 21))
        self.goY.setStyleSheet("")
        self.goY.setObjectName("goY")
        self.goZ = QtWidgets.QPushButton(Dialog)
        self.goZ.setGeometry(QtCore.QRect(650, 160, 51, 21))
        self.goZ.setStyleSheet("")
        self.goZ.setObjectName("goZ")
        
        self.instructionText.setReadOnly(True)
        
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        self.speed.addItem("1")
        self.speed.addItem("2")
        self.speed.addItem("3")
        self.speed.addItem("4")
        self.speed.addItem("5")
        self.speed.setCurrentIndex(2)
        
        
        self.right_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("right"), Dialog)
        self.right_shortcut.activated.connect(lambda: tinyG.jog("X",0.5,200))
        self.right_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.left_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("left"), Dialog)
        self.left_shortcut.activated.connect(lambda: tinyG.jog("X",-0.5,200))
        self.left_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.up_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("up"), Dialog)
        self.up_shortcut.activated.connect(lambda: tinyG.jog("Y",0.5,200))
        self.up_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.down_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("down"), Dialog)
        self.down_shortcut.activated.connect(lambda: tinyG.jog("Y",-0.5,200))
        self.down_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.zero_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("PgDown"), Dialog)
        self.zero_shortcut.activated.connect(lambda: tinyG.jog("Z",-0.5,200))
        self.zero_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.one_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("PgUp"), Dialog)
        self.one_shortcut.activated.connect(lambda: tinyG.jog("Z",0.5,200))
        self.one_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        
        self.removeButton.clicked.connect(lambda: self.removeProcedure(Dialog,probeCommands))
        self.goX.clicked.connect(lambda: self.callJogX(tinyG))
        self.goY.clicked.connect(lambda: self.callJogY(tinyG))
        self.goZ.clicked.connect(lambda: self.callJogZ(tinyG))
        self.Instructions.clicked.connect(lambda: self.openInstructions())
        self.singleProbe.clicked.connect(lambda: self.firstProbe(tinyG, probeCommands))
        self.setOrigin.clicked.connect(lambda: self.setOrig(tinyG, probeCommands))
        self.runProbe.clicked.connect(lambda: self.runProbing(tinyG,probeCommands))
        self.runProbe.clicked.connect(Dialog.close)
        self.updatePosition(tinyG)
        self.GoButton.clicked.connect(lambda: self.callJog(tinyG))
        self.GoButton.setDefault(True)
        self.addProcedures.clicked.connect(lambda: self.openSelect_Cranial_Procedure(tinyG, probeCommands))
        self.addProcedures.clicked.connect(Dialog.close)
        self.SendButton.clicked.connect(lambda: self.serialCommand(tinyG))
        self.retranslateUi(Dialog, probeCommands)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog, probeCommands):
        commandText=""
        counter=0
        for i in probeCommands:
            if(i.probed==0):
                probed="Not probed"
            else:
                probed="Probed"
            counter=counter+1
            #write cranial procedure details to txt window
            commandText=commandText+"Procedure #"+str(counter)+"\nType: " +i.procedureType+"\n"+ "Parameters: "+i.parameter+"\n"+probed+"\n\n"
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Surface Profiling"))
        self.label_4.setText(_translate("Dialog", "Surface Profiling Configurations"))
        self.label_2.setText(_translate("Dialog", "Craniobot v1.0 Created at U. of Minnesota"))
        self.runProbe.setText(_translate("Dialog", "Start Surface Profiling"))
        self.singleProbe.setText(_translate("Dialog", "Find Origin"))
        self.instructionText.setPlainText(_translate("Dialog", commandText))
        self.removeButton.setText(_translate("Dialog", "Remove Procedure "))
        self.removeNumber.setText(_translate("Dialog", "0"))
        self.addProcedures.setText(_translate("Dialog", "Add More Procedures"))
        self.XJog.setText(_translate("Dialog", "0"))
        self.YJog.setText(_translate("Dialog", "0"))
        self.LabelJog.setText(_translate("Dialog", "Jog (mm)"))
        self.LabelPosition.setText(_translate("Dialog", "Position (mm)"))
        self.LabelY.setText(_translate("Dialog", "Y"))
        self.GoButton.setText(_translate("Dialog", "Go!"))
        self.LabelZ.setText(_translate("Dialog", "Z"))
        self.LabelSpeed.setText(_translate("Dialog", "Speed (1-5)"))
        self.label_3.setText(_translate("Dialog", "Set Position"))
        self.LabelX.setText(_translate("Dialog", "X"))
        self.ZJog.setText(_translate("Dialog", "0"))
        self.Instructions.setText(_translate("Dialog", "?"))
        self.setOrigin.setText(_translate("Dialog", "Set Origin"))
        self.LabelGcode.setText(_translate("Dialog", "G-code command"))
        self.SendButton.setText(_translate("Dialog", "Send"))
        self.goX.setText(_translate("Dialog", "Go X"))
        self.goY.setText(_translate("Dialog", "Go Y"))
        self.goZ.setText(_translate("Dialog", "Go Z"))
        
# %%
class Ui_Skull_Thinning(object):
    def  openSelect_Cranial_Procedure(self, tinyG, probeCommands):
        self.window = QtWidgets.QDialog()
        self.uiSelect_Cranial_Procedure = Ui_Select_Cranial_Procedure(tinyG, probeCommands)
        self.uiSelect_Cranial_Procedure.setupUi(self.window)
        self.window.show()
        
    def callSkullThinningGCode(self,tinyG, probeCommands):
        if(self.X_Center.text()):
            x1=float(self.X_Center.text())
        if(self.Y_Center.text()):
            y1=float(self.Y_Center.text())
        if(self.X_Center_2.text()):
            x2=float(self.X_Center_2.text())
        if(self.Y_Center_2.text()):
            y2=float(self.Y_Center_2.text())
            craniotomy_probe = GenerateSkullThinning(x1,y1,x2,y2,0.25)
            parameter="X1 = "+ str(x1)+"mm, Y1 = "+str(y1)+ "mm, X2 = "+str(x2)+ "mm, Y2 = "+str(y2)+ "mm"
            procedure=cranialProcedure("Skull Thinning", parameter, craniotomy_probe.gCode)
            probeCommands.append(procedure)
        
    def callJog(self, tinyG):
        XMove=0
        YMove=0
        ZMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        if(self.ZJog.text()):
            ZMove=float(self.ZJog.text())
            tinyG.jog("z", ZMove, int(speed)) 
        if(self.XJog.text()):
            XMove=float(self.XJog.text())
            tinyG.jog("x", XMove, int(speed))
        if(self.YJog.text()):
            YMove=float(self.YJog.text())
            tinyG.jog("y", YMove, int(speed))
         
        time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3):
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
        
    def updatePosition(self, tinyG):
        tinyG.ser.write(b'{"pos":n}\n')
        pos=str(tinyG.ser.readlines())
        
        initIndex=pos.find("pos")+6
        finalIndex=pos.find("\"a\"")-1
        newPos=pos[initIndex:finalIndex]

        xaxis=int(newPos[newPos.find("x")+3:newPos.find(",")-4])
        newPos=newPos[newPos.find(",")+1:]
        yaxis=int(newPos[newPos.find("y")+3:newPos.find(",")-4])
        newPos=newPos[newPos.find(",")+1:]
        zaxis=int(newPos[newPos.find("z")+3:len(newPos)-4])
        
        self.XValue.display(xaxis)
        self.YValue.display(yaxis)
        self.ZValue.display(zaxis)
        
    def setupUi(self, Dialog,tinyG, probeCommands):
        Dialog.setObjectName("Dialog")
        Dialog.resize(502, 293)
        Dialog.setStyleSheet("#mainView, #calibration_tab, #mask_tab, #integration_tab {\n"
"    background: #3C3C3C;\n"
"    border: 5px solid #3C3C3C;\n"
"}\n"
"\n"
"QTabWidget::tab-bar{\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabWidget::pane {\n"
"    border:  1px solid #2F2F2F;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QWidget{\n"
"    color: #F1F1F1;\n"
"}\n"
"\n"
"\n"
"QTabBar::tab:left, QTabBar::tab:right {\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"    font: normal 14px;\n"
"    color: #F1F1F1;\n"
"    border-radius:2px;\n"
"\n"
"    padding: 0px;\n"
"    width: 20px;\n"
"    min-height:140px;\n"
"}\n"
"\n"
"\n"
"QTabBar::tab::top, QTabBar::tab::bottom {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"    border-right: 0px solid white;\n"
"    color: #F1F1F1;\n"
"    font: normal 11px;\n"
"    border-radius:2px;\n"
"    min-width: 65px;\n"
"    height: 19px;\n"
"    padding: 0px;\n"
"    margin-top: 1px;\n"
"    margin-right: 1px;\n"
" }\n"
"QTabBar::tab::left:last, QTabBar::tab::right:last{\n"
"    border-bottom-left-radius: 10px;\n"
"    border-bottom-right-radius: 10px;\n"
"}\n"
"QTabBar::tab:left:first, QTabBar::tab:right:first{\n"
"    border-top-left-radius: 10px;\n"
"    border-top-right-radius: 10px;\n"
"}\n"
"\n"
"QTabWidget, QTabWidget::tab-bar,  QTabWidget::panel, QWidget{\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"QTabWidget::tab-bar {\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabBar::tab:hover {\n"
"    border: 1px solid #ADADAD;\n"
"}\n"
"\n"
"QTabBar:tab:selected{\n"
"    background: qlineargradient(\n"
"            x1: 0, y1: 1,\n"
"            x2: 0, y2: 0,\n"
"            stop: 0 #727272,\n"
"            stop: 1 #444444\n"
"        );\n"
"    border:1px solid  rgb(255, 120,00);/*#ADADAD; */\n"
"}\n"
"\n"
"QTabBar::tab:bottom:last, QTabBar::tab:top:last{\n"
"    border-top-right-radius: 10px;\n"
"    border-bottom-right-radius: 10px;\n"
"}\n"
"QTabBar::tab:bottom:first, QTabBar::tab:top:first{\n"
"    border-top-left-radius: 10px;\n"
"    border-bottom-left-radius: 10px;\n"
"}\n"
"QTabBar::tab:top:!selected {\n"
"    margin-top: 1px;\n"
"    padding-top:1px;\n"
"}\n"
"QTabBar::tab:bottom:!selected{\n"
"    margin-bottom: 1px;\n"
"    padding-bottom:1px;\n"
"}\n"
"\n"
"QGraphicsView {\n"
"    border-style: none;\n"
"}\n"
"\n"
"QLabel , QCheckBox, QGroupBox, QRadioButton, QListWidget::item, QPushButton, QToolBox::tab, QSpinBox, QDoubleSpinBox , QComboBox{\n"
"    color: #F1F1F1;\n"
"    font-size: 12px;\n"
"}\n"
"QCheckBox{\n"
"    border-radius: 5px;\n"
"}\n"
"QRadioButton, QCheckBox {\n"
"    font-weight: normal;\n"
"    height: 15px;\n"
"}\n"
"\n"
"QLineEdit  {\n"
"    border-radius: 2px;\n"
"    background: #F1F1F1;\n"
"    color: black;\n"
"    height: 18 px;\n"
"}\n"
"\n"
"QLineEdit::focus{\n"
"    border-style: none;\n"
"    border-radius: 2px;\n"
"    background: #F1F1F1;\n"
"    color: black;\n"
"}\n"
"\n"
"QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled{\n"
"    color:rgb(148, 148, 148)\n"
"}\n"
"QSpinBox, QDoubleSpinBox {\n"
"    background-color:  #F1F1F1;\n"
"    color: black;\n"
"    /*margin-left: -15px;\n"
"    margin-right: -2px;*/\n"
"}\n"
"\n"
"QComboBox QAbstractItemView{\n"
"    background: #2D2D30;\n"
"    color: #F1F1F1;\n"
"    selection-background-color: rgba(221, 124, 40, 120);\n"
"    border-radius: 5px;\n"
"    min-height: 40px;\n"
"\n"
"}\n"
"\n"
"QComboBox QAbstractItemView:QScrollbar::vertical {\n"
"    width:100px;\n"
"}\n"
"\n"
"QComboBox:!editable {\n"
"    margin-left: 1px;\n"
"    padding: 0px 10px 0px 10px;\n"
"    height: 23px;\n"
"    background-color: #3C3C3C;\n"
"}\n"
"\n"
"QComboBox::item{\n"
"    background-color: #3C3C3C;\n"
"}\n"
"\n"
"QComboBox::item::selected {\n"
"    background-color: #505050;\n"
"}\n"
"QToolBox::tab:QToolButton{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"\n"
"    border-radius:2px;\n"
"    padding-right: 10px;\n"
"\n"
"    color: #F1F1F1;\n"
"    font-size: 12px;\n"
"    padding: 3px;\n"
"}\n"
"QToolBox::tab:QToolButton{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"     border: 1px solid  #5B5B5B;\n"
"\n"
"     border-radius:2px;\n"
"     padding-right: 10px;\n"
"\n"
"      color: #F1F1F1;\n"
"    font-size: 12px;\n"
"    padding: 3px;\n"
"}\n"
"\n"
"QPushButton{\n"
"    color: #F1F1F1;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop:1 #505050);\n"
"    border: 1px solid #5B5B5B;\n"
"    border-radius: 5px;\n"
"    padding-left: 8px;\n"
"    height: 18px;\n"
"    padding-right: 8px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    margin-top: 2px;\n"
"    margin-left: 2px;\n"
"}\n"
"\n"
"QPushButton::disabled{\n"
"}\n"
"\n"
"QPushButton::hover {\n"
"    border:1px solid #ADADAD;\n"
"}\n"
"\n"
"QPushButton::checked {\n"
"    background: qlineargradient(\n"
"        x1: 0, y1: 1,\n"
"        x2: 0, y2: 0,\n"
"        stop: 0 #727272,\n"
"        stop: 1 #444444\n"
"    );\n"
"     border:1px solid  rgb(255, 120,00);\n"
"}\n"
"\n"
"QPushButton::focus {\n"
"    outline: None;\n"
"}\n"
"QGroupBox {\n"
"    border: 1px solid #ADADAD;\n"
"    border-radius: 4px;\n"
"    margin-top: 7px;\n"
"    padding: 0px\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 20px\n"
"}\n"
"\n"
"QSplitter::handle:hover {\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"\n"
"QGraphicsView{\n"
"    border-style: none;\n"
"}\n"
"\n"
"QScrollBar:vertical {\n"
"    border: 2px solid #3C3C3C;\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    width: 12px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #969696, stop:1 #CACACA);\n"
"    border-radius: 3px;\n"
"    min-height: 20px;\n"
"    padding: 15px;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:vertical {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"    background: none;\n"
"}\n"
"\n"
"QScrollBar:horizontal {\n"
"    border: 2px solid #3C3C3C;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    height: 12 px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #969696, stop:1 #CACACA);\n"
"    border-radius: 3px;\n"
"    min-width: 20px;\n"
"    padding: 15px;\n"
"}\n"
"QScrollBar::add-line:horizontal {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:horizontal {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n"
"    background: none;\n"
"}\n"
"\n"
"QSplitterHandle:hover {}\n"
"\n"
"QSplitter::handle:vertical{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #505050, stop: 0.7 #3C3C3C);\n"
"    height: 15px;\n"
"}\n"
"\n"
"QSplitter::handle:vertical:pressed, QSplitter::handle:vertical:hover{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #5C5C5C, stop: 0.7 #3C3C3C);\n"
"}\n"
"\n"
"QSplitter::handle:horizontal{\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #505050, stop: 0.7 #3C3C3C);\n"
"    width: 15px;\n"
"}\n"
"\n"
"QSplitter::handle:horizontal:pressed, QSplitter::handle:horizontal:hover{\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #5C5C5C, stop: 0.7 #3C3C3C);\n"
"}\n"
"\n"
"QSplitter::handle:hover {\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    spacing: 10px;\n"
"    color: #F1F1F1;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    border: None;\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    font-size: 12px;\n"
"    text-align: center;\n"
"}\n"
"\n"
"QTableWidget QPushButton {\n"
"    margin: 5px;\n"
"}\n"
"\n"
"\n"
"QTableWidget QPushButton::pressed{\n"
"    margin-top: 7px;\n"
"    margin-left: 7px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(177,80,0,255), stop:1 rgba(255,120,0,255));\n"
"    selection-color: #F1F1F1;\n"
"}\n"
"\n"
"#phase_table_widget QCheckBox, #overlay_table_widget QCheckBox {\n"
"    margin-left: 5px;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox, #phase_table_widget QDoubleSpinBox {\n"
"    min-width: 50;\n"
"    max-width: 70;\n"
"    background: transparent;\n"
"    background-color: transparent;\n"
"    color:#D1D1D1;\n"
"    border: 1px solid transparent;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox:disabled, #phase_table_widget QDoubleSpinBox:disabled {\n"
"    color:#888;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button, #overlay_table_widget QDoubleSpinBox::down-button,\n"
"#phase_table_widget QDoubleSpinBox::up-button, #phase_table_widget QDoubleSpinBox::down-button {\n"
"    width: 11px;\n"
"    height: 9px;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop:1 #505050);\n"
"    border: 0.5px solid #5B5B5B;\n"
"    border-radius: 2px;\n"
"}\n"
"#overlay_table_widget QDoubleSpinBox::up-button:hover, #overlay_table_widget QDoubleSpinBox::down-button:hover,\n"
"#phase_table_widget QDoubleSpinBox::up-button:hover, #phase_table_widget QDoubleSpinBox::down-button:hover\n"
"{\n"
"    border:0.5px solid #ADADAD;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button:pressed,  #phase_table_widget QDoubleSpinBox::up-button:pressed{\n"
"    width: 10px;\n"
"    height: 8px;\n"
"}\n"
"#overlay_table_widget QDoubleSpinBox::down-button:pressed, #phase_table_widget QDoubleSpinBox::down-button:pressed {\n"
"    width: 10px;\n"
"    height: 8px;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button, #phase_table_widget QDoubleSpinBox::up-button {\n"
"    image: url(dioptas/resources/icons/arrow_up.ico) 1;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::down-button, #phase_table_widget QDoubleSpinBox::down-button {\n"
"    image: url(dioptas/resources/icons/arrow_down.ico) 1;\n"
"}\n"
"\n"
"QFrame#main_frame {\n"
"    color: #F1F1F1;\n"
"    border: 1px solid #5B5B5B;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"#calibration_mode_btn, #mask_mode_btn, #integration_mode_btn {\n"
"    font: normal 12px;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"#calibration_mode_btn {\n"
"   border-top-right-radius:8px;\n"
"   border-bottom-right-radius: 8px;\n"
"}\n"
"\n"
"#integration_mode_btn {\n"
"   border-top-left-radius:8px;\n"
"   border-bottom-left-radius: 8px;\n"
"}")
        self.GoButton = QtWidgets.QPushButton(Dialog)
        self.GoButton.setGeometry(QtCore.QRect(410, 210, 61, 51))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.GoButton.setFont(font)
        self.GoButton.setObjectName("GoButton")
        self.YValue = QtWidgets.QLCDNumber(Dialog)
        self.YValue.setGeometry(QtCore.QRect(340, 120, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.YValue.setFont(font)
        self.YValue.setAutoFillBackground(False)
        self.YValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.YValue.setDigitCount(4)
        self.YValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.YValue.setObjectName("YValue")
        self.LabelJog = QtWidgets.QLabel(Dialog)
        self.LabelJog.setGeometry(QtCore.QRect(400, 50, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelJog.setFont(font)
        self.LabelJog.setAutoFillBackground(False)
        self.LabelJog.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelJog.setLineWidth(1)
        self.LabelJog.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelJog.setObjectName("LabelJog")
        self.Xoffset_Label = QtWidgets.QLabel(Dialog)
        self.Xoffset_Label.setGeometry(QtCore.QRect(30, 80, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Xoffset_Label.setFont(font)
        self.Xoffset_Label.setObjectName("Xoffset_Label")
        self.LabelX = QtWidgets.QLabel(Dialog)
        self.LabelX.setGeometry(QtCore.QRect(310, 80, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelX.setFont(font)
        self.LabelX.setTextFormat(QtCore.Qt.PlainText)
        self.LabelX.setScaledContents(False)
        self.LabelX.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelX.setWordWrap(False)
        self.LabelX.setObjectName("LabelX")
        self.X_Center = QtWidgets.QLineEdit(Dialog)
        self.X_Center.setGeometry(QtCore.QRect(90, 80, 41, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.X_Center.setFont(font)
        self.X_Center.setAlignment(QtCore.Qt.AlignCenter)
        self.X_Center.setObjectName("X_Center")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(90, 20, 121, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(20, 260, 211, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(280, -20, 21, 341))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.line.setFont(font)
        self.line.setAutoFillBackground(False)
        self.line.setStyleSheet("color: rgb(0, 0, 0);")
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(3)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setObjectName("line")
        self.Yoffset_label = QtWidgets.QLabel(Dialog)
        self.Yoffset_label.setGeometry(QtCore.QRect(150, 80, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Yoffset_label.setFont(font)
        self.Yoffset_label.setObjectName("Yoffset_label")
        self.LabelPosition = QtWidgets.QLabel(Dialog)
        self.LabelPosition.setGeometry(QtCore.QRect(300, 50, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelPosition.setFont(font)
        self.LabelPosition.setAutoFillBackground(False)
        self.LabelPosition.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelPosition.setLineWidth(1)
        self.LabelPosition.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelPosition.setObjectName("LabelPosition")
        self.LabelZ = QtWidgets.QLabel(Dialog)
        self.LabelZ.setGeometry(QtCore.QRect(310, 160, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelZ.setFont(font)
        self.LabelZ.setTextFormat(QtCore.Qt.PlainText)
        self.LabelZ.setScaledContents(False)
        self.LabelZ.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelZ.setWordWrap(False)
        self.LabelZ.setObjectName("LabelZ")
        self.LabelSpeed = QtWidgets.QLabel(Dialog)
        self.LabelSpeed.setGeometry(QtCore.QRect(300, 210, 111, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelSpeed.setFont(font)
        self.LabelSpeed.setAutoFillBackground(False)
        self.LabelSpeed.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelSpeed.setLineWidth(1)
        self.LabelSpeed.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelSpeed.setObjectName("LabelSpeed")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(350, 20, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.LabelY = QtWidgets.QLabel(Dialog)
        self.LabelY.setGeometry(QtCore.QRect(310, 120, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelY.setFont(font)
        self.LabelY.setTextFormat(QtCore.Qt.PlainText)
        self.LabelY.setScaledContents(False)
        self.LabelY.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelY.setWordWrap(False)
        self.LabelY.setObjectName("LabelY")
        self.YJog = QtWidgets.QLineEdit(Dialog)
        self.YJog.setGeometry(QtCore.QRect(410, 120, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.YJog.setFont(font)
        self.YJog.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.YJog.setAlignment(QtCore.Qt.AlignCenter)
        self.YJog.setObjectName("YJog")
        self.ZValue = QtWidgets.QLCDNumber(Dialog)
        self.ZValue.setGeometry(QtCore.QRect(340, 160, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.ZValue.setFont(font)
        self.ZValue.setAutoFillBackground(False)
        self.ZValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.ZValue.setDigitCount(4)
        self.ZValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.ZValue.setObjectName("ZValue")
        self.Y_Center = QtWidgets.QLineEdit(Dialog)
        self.Y_Center.setGeometry(QtCore.QRect(210, 80, 41, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.Y_Center.setFont(font)
        self.Y_Center.setAlignment(QtCore.Qt.AlignCenter)
        self.Y_Center.setObjectName("Y_Center")
        self.XValue = QtWidgets.QLCDNumber(Dialog)
        self.XValue.setGeometry(QtCore.QRect(340, 80, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.XValue.setFont(font)
        self.XValue.setAutoFillBackground(False)
        self.XValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.XValue.setDigitCount(4)
        self.XValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.XValue.setObjectName("XValue")
        self.Next = QtWidgets.QPushButton(Dialog)
        self.Next.setGeometry(QtCore.QRect(200, 190, 61, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Next.setFont(font)
        self.Next.setObjectName("Next")
        self.XJog = QtWidgets.QLineEdit(Dialog)
        self.XJog.setGeometry(QtCore.QRect(410, 80, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.XJog.setFont(font)
        self.XJog.setAlignment(QtCore.Qt.AlignCenter)
        self.XJog.setObjectName("XJog")
        self.ZJog = QtWidgets.QLineEdit(Dialog)
        self.ZJog.setGeometry(QtCore.QRect(410, 160, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.ZJog.setFont(font)
        self.ZJog.setAlignment(QtCore.Qt.AlignCenter)
        self.ZJog.setObjectName("ZJog")
        self.speed = QtWidgets.QComboBox(Dialog)
        self.speed.setGeometry(QtCore.QRect(340, 240, 50, 22))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        self.Xoffset_Label_2 = QtWidgets.QLabel(Dialog)
        self.Xoffset_Label_2.setGeometry(QtCore.QRect(30, 140, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Xoffset_Label_2.setFont(font)
        self.Xoffset_Label_2.setObjectName("Xoffset_Label_2")
        self.X_Center_2 = QtWidgets.QLineEdit(Dialog)
        self.X_Center_2.setGeometry(QtCore.QRect(90, 140, 41, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.X_Center_2.setFont(font)
        self.X_Center_2.setAlignment(QtCore.Qt.AlignCenter)
        self.X_Center_2.setObjectName("X_Center_2")
        self.Yoffset_label_2 = QtWidgets.QLabel(Dialog)
        self.Yoffset_label_2.setGeometry(QtCore.QRect(150, 140, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Yoffset_label_2.setFont(font)
        self.Yoffset_label_2.setObjectName("Yoffset_label_2")
        self.Y_Center_2 = QtWidgets.QLineEdit(Dialog)
        self.Y_Center_2.setGeometry(QtCore.QRect(210, 140, 41, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.Y_Center_2.setFont(font)
        self.Y_Center_2.setAlignment(QtCore.Qt.AlignCenter)
        self.Y_Center_2.setObjectName("Y_Center_2")
        
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        self.speed.addItem("1")
        self.speed.addItem("2")
        self.speed.addItem("3")
        self.speed.addItem("4")
        self.speed.addItem("5")
        self.speed.setCurrentIndex(2)
        self.right_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("right"), Dialog)
        self.right_shortcut.activated.connect(lambda: tinyG.jog("X",0.5,200))
        self.right_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.left_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("left"), Dialog)
        self.left_shortcut.activated.connect(lambda: tinyG.jog("X",-0.5,200))
        self.left_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.up_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("up"), Dialog)
        self.up_shortcut.activated.connect(lambda: tinyG.jog("Y",0.5,200))
        self.up_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.down_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("down"), Dialog)
        self.down_shortcut.activated.connect(lambda: tinyG.jog("Y",-0.5,200))
        self.down_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.zero_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("PgDown"), Dialog)
        self.zero_shortcut.activated.connect(lambda: tinyG.jog("Z",-0.5,200))
        self.zero_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.one_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("PgUp"), Dialog)
        self.one_shortcut.activated.connect(lambda: tinyG.jog("Z",0.5,200))
        self.one_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.updatePosition(tinyG)
        self.GoButton.clicked.connect(lambda: self.callJog(tinyG))
        # -DanielStart
        self.GoButton.setDefault(True)
        self.Next.clicked.connect(lambda: self.callSkullThinningGCode(tinyG, probeCommands))
        self.Next.clicked.connect(lambda: self.openSelect_Cranial_Procedure(tinyG, probeCommands))
        self.Next.clicked.connect(Dialog.close)
        
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Skull Thinning"))
        self.GoButton.setText(_translate("Dialog", "Go!"))
        self.LabelJog.setText(_translate("Dialog", "Jog (mm)"))
        self.Xoffset_Label.setText(_translate("Dialog", "X1 (mm)"))
        self.LabelX.setText(_translate("Dialog", "X"))
        self.X_Center.setText(_translate("Dialog", "0"))
        self.label_4.setText(_translate("Dialog", "Skull Thinning"))
        self.label_2.setText(_translate("Dialog", "Craniobot v1.0 Created at U. of Minnesota"))
        self.Yoffset_label.setText(_translate("Dialog", "Y1 (mm)"))
        self.LabelPosition.setText(_translate("Dialog", "Position (mm)"))
        self.LabelZ.setText(_translate("Dialog", "Z"))
        self.LabelSpeed.setText(_translate("Dialog", "Speed (1-5)"))
        self.label_3.setText(_translate("Dialog", "Set Position"))
        self.LabelY.setText(_translate("Dialog", "Y"))
        self.YJog.setText(_translate("Dialog", "0"))
        self.Y_Center.setText(_translate("Dialog", "0"))
        self.Next.setText(_translate("Dialog", "Next"))
        self.XJog.setText(_translate("Dialog", "0"))
        self.ZJog.setText(_translate("Dialog", "0"))
        self.Xoffset_Label_2.setText(_translate("Dialog", "X2 (mm)"))
        self.X_Center_2.setText(_translate("Dialog", "0"))
        self.Yoffset_label_2.setText(_translate("Dialog", "Y2 (mm)"))
        self.Y_Center_2.setText(_translate("Dialog", "0"))

# %%
class Ui_MillingConfig(object):
    def callJog(self, tinyG):
        XMove=0
        YMove=0
        ZMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        if(self.ZJog.text()):
            ZMove=float(self.ZJog.text())
            tinyG.jog("z", ZMove, int(speed))
        if(self.XJog.text()):
            XMove=float(self.XJog.text())
            tinyG.jog("x", XMove, int(speed))
        if(self.YJog.text()):
            YMove=float(self.YJog.text())
            tinyG.jog("y", YMove, int(speed))
         
        time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3):
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
    
    def callJogX(self,tinyG):
        XMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        if(self.XJog.text()):
            XMove=float(self.XJog.text())
            tinyG.jog("x", XMove, int(speed))
            time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
        
    def callJogY(self,tinyG):
        YMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        if(self.YJog.text()):
            YMove=float(self.YJog.text())
            tinyG.jog("y", YMove, int(speed))
            time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
        
    def callJogZ(self,tinyG):
        ZMove=0
        speed=300
        speed_quant=int(self.speed.currentText())
        speed=speed_quant*100
        if(self.ZJog.text()):
            ZMove=float(self.ZJog.text())
            tinyG.jog("z", ZMove, int(speed))
            time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
    
    def goxyOrigin(self, tinyG):
        tinyG.goToXYOrigin(200)
        time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3):
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)
        
    def updatePosition(self, tinyG):
        tinyG.ser.write(b'{"pos":n}\n')
        pos=str(tinyG.ser.readlines())
        
        initIndex=pos.find("pos")+6
        finalIndex=pos.find("\"a\"")-1
        newPos=pos[initIndex:finalIndex]

        xaxis=int(newPos[newPos.find("x")+3:newPos.find(",")-4])
        newPos=newPos[newPos.find(",")+1:]
        yaxis=int(newPos[newPos.find("y")+3:newPos.find(",")-4])
        newPos=newPos[newPos.find(",")+1:]
        zaxis=int(newPos[newPos.find("z")+3:len(newPos)-4])
        
        self.XValue.display(xaxis)
        self.YValue.display(yaxis)
        self.ZValue.display(zaxis)
    
    def  openInstructions(self):
        self.window = QtWidgets.QDialog()
        self.uiI_Milling = Ui_I_Milling()
        self.uiI_Milling.setupUi(self.window)
        self.window.show()
        
    def runMilling(self, tinyG, probeCommands, Dialog):
        #run milling commands based on depth and profiler output
        depth=abs(float(self.depthValue.text()))
        depth=depth/1000
        procedure=abs(int(self.procedureNumber.text()))
        counter=1
        for i in probeCommands:
            if (procedure==counter):
                newDepth=depth
                milling=MillPath(i.millingPath, newDepth)
                tinyG.runMill(milling.gCode)
                time.sleep(1)
                tinyG.ser.write(b'{"stat":n}\n')
                stat=str(tinyG.ser.readlines())
                val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
                while(val!=3 and val!=4):
                    tinyG.ser.write(b'{"stat":n}\n')
                    stat=str(tinyG.ser.readlines())
                    val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
                    time.sleep(1)
                self.updatePosition(tinyG)
                i.millingDepth=depth
            counter=counter+1 
        self.retranslateUi(Dialog, probeCommands)
        
    def origin(self, tinyG):
        tinyG.setOrigin()
        self.updatePosition(tinyG)        
    
    def serialCommand(self,tinyG):
        if(self.gcodeManual.text()):
            com=str(self.gcodeManual.text())
            command = '{{"gc":"{}"}}\n'.format(com)
            tinyG.ser.write(command.encode('utf-8'))
        time.sleep(1)
        tinyG.ser.write(b'{"stat":n}\n')
        stat=str(tinyG.ser.readlines())
        val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
        while(val!=3): #reads tinyg status and wait till operation has been processed before updating position
            tinyG.ser.write(b'{"stat":n}\n')
            stat=str(tinyG.ser.readlines())
            val=int(stat[stat.find("stat")+6:stat.find("stat")+7])
            time.sleep(1)
        self.updatePosition(tinyG)  
    
    def  openSetXYZ_Origin(self, tinyG, probeCommands):
        #Opens next window
        self.window = QtWidgets.QDialog()
        self.uiSetXYZ_Origin = Ui_SetXYZ_Origin()
        self.uiSetXYZ_Origin.setupUi(self.window, tinyG, probeCommands)
        self.window.show()
        
    def setupUi(self, Dialog, tinyG, probeCommands):
        Dialog.setObjectName("Dialog")
        Dialog.resize(736, 347)
        font = QtGui.QFont()
        font.setPointSize(8)
        Dialog.setFont(font)
        Dialog.setStyleSheet("#mainView, #calibration_tab, #mask_tab, #integration_tab {\n"
"    background: #3C3C3C;\n"
"    border: 5px solid #3C3C3C;\n"
"}\n"
"\n"
"QTabWidget::tab-bar{\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabWidget::pane {\n"
"    border:  1px solid #2F2F2F;\n"
"    border-radius: 3px;\n"
"}\n"
"\n"
"QWidget{\n"
"    color: #F1F1F1;\n"
"}\n"
"\n"
"\n"
"QTabBar::tab:left, QTabBar::tab:right {\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"    font: normal 14px;\n"
"    color: #F1F1F1;\n"
"    border-radius:2px;\n"
"\n"
"    padding: 0px;\n"
"    width: 20px;\n"
"    min-height:140px;\n"
"}\n"
"\n"
"\n"
"QTabBar::tab::top, QTabBar::tab::bottom {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"    border-right: 0px solid white;\n"
"    color: #F1F1F1;\n"
"    font: normal 11px;\n"
"    border-radius:2px;\n"
"    min-width: 65px;\n"
"    height: 19px;\n"
"    padding: 0px;\n"
"    margin-top: 1px;\n"
"    margin-right: 1px;\n"
" }\n"
"QTabBar::tab::left:last, QTabBar::tab::right:last{\n"
"    border-bottom-left-radius: 10px;\n"
"    border-bottom-right-radius: 10px;\n"
"}\n"
"QTabBar::tab:left:first, QTabBar::tab:right:first{\n"
"    border-top-left-radius: 10px;\n"
"    border-top-right-radius: 10px;\n"
"}\n"
"\n"
"QTabWidget, QTabWidget::tab-bar,  QTabWidget::panel, QWidget{\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"QTabWidget::tab-bar {\n"
"    alignment: center;\n"
"}\n"
"\n"
"QTabBar::tab:hover {\n"
"    border: 1px solid #ADADAD;\n"
"}\n"
"\n"
"QTabBar:tab:selected{\n"
"    background: qlineargradient(\n"
"            x1: 0, y1: 1,\n"
"            x2: 0, y2: 0,\n"
"            stop: 0 #727272,\n"
"            stop: 1 #444444\n"
"        );\n"
"    border:1px solid  rgb(255, 120,00);/*#ADADAD; */\n"
"}\n"
"\n"
"QTabBar::tab:bottom:last, QTabBar::tab:top:last{\n"
"    border-top-right-radius: 10px;\n"
"    border-bottom-right-radius: 10px;\n"
"}\n"
"QTabBar::tab:bottom:first, QTabBar::tab:top:first{\n"
"    border-top-left-radius: 10px;\n"
"    border-bottom-left-radius: 10px;\n"
"}\n"
"QTabBar::tab:top:!selected {\n"
"    margin-top: 1px;\n"
"    padding-top:1px;\n"
"}\n"
"QTabBar::tab:bottom:!selected{\n"
"    margin-bottom: 1px;\n"
"    padding-bottom:1px;\n"
"}\n"
"\n"
"QGraphicsView {\n"
"    border-style: none;\n"
"}\n"
"\n"
"QLabel , QCheckBox, QGroupBox, QRadioButton, QListWidget::item, QPushButton, QToolBox::tab, QSpinBox, QDoubleSpinBox , QComboBox{\n"
"    color: #F1F1F1;\n"
"    font-size: 12px;\n"
"}\n"
"QCheckBox{\n"
"    border-radius: 5px;\n"
"}\n"
"QRadioButton, QCheckBox {\n"
"    font-weight: normal;\n"
"    height: 15px;\n"
"}\n"
"\n"
"QLineEdit  {\n"
"    border-radius: 2px;\n"
"    background: #F1F1F1;\n"
"    color: black;\n"
"    height: 18 px;\n"
"}\n"
"\n"
"QLineEdit::focus{\n"
"    border-style: none;\n"
"    border-radius: 2px;\n"
"    background: #F1F1F1;\n"
"    color: black;\n"
"}\n"
"\n"
"QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled{\n"
"    color:rgb(148, 148, 148)\n"
"}\n"
"QSpinBox, QDoubleSpinBox {\n"
"    background-color:  #F1F1F1;\n"
"    color: black;\n"
"    /*margin-left: -15px;\n"
"    margin-right: -2px;*/\n"
"}\n"
"\n"
"QComboBox QAbstractItemView{\n"
"    background: #2D2D30;\n"
"    color: #F1F1F1;\n"
"    selection-background-color: rgba(221, 124, 40, 120);\n"
"    border-radius: 5px;\n"
"    min-height: 40px;\n"
"\n"
"}\n"
"\n"
"QComboBox QAbstractItemView:QScrollbar::vertical {\n"
"    width:100px;\n"
"}\n"
"\n"
"QComboBox:!editable {\n"
"    margin-left: 1px;\n"
"    padding: 0px 10px 0px 10px;\n"
"    height: 23px;\n"
"    background-color: #3C3C3C;\n"
"}\n"
"\n"
"QComboBox::item{\n"
"    background-color: #3C3C3C;\n"
"}\n"
"\n"
"QComboBox::item::selected {\n"
"    background-color: #505050;\n"
"}\n"
"QToolBox::tab:QToolButton{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"    border: 1px solid  #5B5B5B;\n"
"\n"
"    border-radius:2px;\n"
"    padding-right: 10px;\n"
"\n"
"    color: #F1F1F1;\n"
"    font-size: 12px;\n"
"    padding: 3px;\n"
"}\n"
"QToolBox::tab:QToolButton{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #3C3C3C, stop:1 #505050);\n"
"     border: 1px solid  #5B5B5B;\n"
"\n"
"     border-radius:2px;\n"
"     padding-right: 10px;\n"
"\n"
"      color: #F1F1F1;\n"
"    font-size: 12px;\n"
"    padding: 3px;\n"
"}\n"
"\n"
"QPushButton{\n"
"    color: #F1F1F1;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop:1 #505050);\n"
"    border: 1px solid #5B5B5B;\n"
"    border-radius: 5px;\n"
"    padding-left: 8px;\n"
"    height: 18px;\n"
"    padding-right: 8px;\n"
"}\n"
"\n"
"QPushButton:pressed{\n"
"    margin-top: 2px;\n"
"    margin-left: 2px;\n"
"}\n"
"\n"
"QPushButton::disabled{\n"
"}\n"
"\n"
"QPushButton::hover {\n"
"    border:1px solid #ADADAD;\n"
"}\n"
"\n"
"QPushButton::checked {\n"
"    background: qlineargradient(\n"
"        x1: 0, y1: 1,\n"
"        x2: 0, y2: 0,\n"
"        stop: 0 #727272,\n"
"        stop: 1 #444444\n"
"    );\n"
"     border:1px solid  rgb(255, 120,00);\n"
"}\n"
"\n"
"QPushButton::focus {\n"
"    outline: None;\n"
"}\n"
"QGroupBox {\n"
"    border: 1px solid #ADADAD;\n"
"    border-radius: 4px;\n"
"    margin-top: 7px;\n"
"    padding: 0px\n"
"}\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 20px\n"
"}\n"
"\n"
"QSplitter::handle:hover {\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"\n"
"QGraphicsView{\n"
"    border-style: none;\n"
"}\n"
"\n"
"QScrollBar:vertical {\n"
"    border: 2px solid #3C3C3C;\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    width: 12px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #969696, stop:1 #CACACA);\n"
"    border-radius: 3px;\n"
"    min-height: 20px;\n"
"    padding: 15px;\n"
"}\n"
"\n"
"QScrollBar::add-line:vertical {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:vertical {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {\n"
"    background: none;\n"
"}\n"
"\n"
"QScrollBar:horizontal {\n"
"    border: 2px solid #3C3C3C;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    height: 12 px;\n"
"    margin: 0px 0px 0px 0px;\n"
"}\n"
"\n"
"QScrollBar::handle:horizontal {\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #969696, stop:1 #CACACA);\n"
"    border-radius: 3px;\n"
"    min-width: 20px;\n"
"    padding: 15px;\n"
"}\n"
"QScrollBar::add-line:horizontal {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"\n"
"QScrollBar::sub-line:horizontal {\n"
"    border: 0px solid grey;\n"
"    height: 0px;\n"
"}\n"
"QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {\n"
"    background: none;\n"
"}\n"
"\n"
"QSplitterHandle:hover {}\n"
"\n"
"QSplitter::handle:vertical{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #505050, stop: 0.7 #3C3C3C);\n"
"    height: 15px;\n"
"}\n"
"\n"
"QSplitter::handle:vertical:pressed, QSplitter::handle:vertical:hover{\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #5C5C5C, stop: 0.7 #3C3C3C);\n"
"}\n"
"\n"
"QSplitter::handle:horizontal{\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #505050, stop: 0.7 #3C3C3C);\n"
"    width: 15px;\n"
"}\n"
"\n"
"QSplitter::handle:horizontal:pressed, QSplitter::handle:horizontal:hover{\n"
"    background: qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0.3 #3C3C3C,  stop:0.5 #5C5C5C, stop: 0.7 #3C3C3C);\n"
"}\n"
"\n"
"QSplitter::handle:hover {\n"
"    background: #3C3C3C;\n"
"}\n"
"\n"
"QHeaderView::section {\n"
"    spacing: 10px;\n"
"    color: #F1F1F1;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 #323232, stop:1 #505050);\n"
"    border: None;\n"
"    font-size: 12px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    font-size: 12px;\n"
"    text-align: center;\n"
"}\n"
"\n"
"QTableWidget QPushButton {\n"
"    margin: 5px;\n"
"}\n"
"\n"
"\n"
"QTableWidget QPushButton::pressed{\n"
"    margin-top: 7px;\n"
"    margin-left: 7px;\n"
"}\n"
"\n"
"QTableWidget {\n"
"    selection-background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(177,80,0,255), stop:1 rgba(255,120,0,255));\n"
"    selection-color: #F1F1F1;\n"
"}\n"
"\n"
"#phase_table_widget QCheckBox, #overlay_table_widget QCheckBox {\n"
"    margin-left: 5px;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox, #phase_table_widget QDoubleSpinBox {\n"
"    min-width: 50;\n"
"    max-width: 70;\n"
"    background: transparent;\n"
"    background-color: transparent;\n"
"    color:#D1D1D1;\n"
"    border: 1px solid transparent;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox:disabled, #phase_table_widget QDoubleSpinBox:disabled {\n"
"    color:#888;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button, #overlay_table_widget QDoubleSpinBox::down-button,\n"
"#phase_table_widget QDoubleSpinBox::up-button, #phase_table_widget QDoubleSpinBox::down-button {\n"
"    width: 11px;\n"
"    height: 9px;\n"
"    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #323232, stop:1 #505050);\n"
"    border: 0.5px solid #5B5B5B;\n"
"    border-radius: 2px;\n"
"}\n"
"#overlay_table_widget QDoubleSpinBox::up-button:hover, #overlay_table_widget QDoubleSpinBox::down-button:hover,\n"
"#phase_table_widget QDoubleSpinBox::up-button:hover, #phase_table_widget QDoubleSpinBox::down-button:hover\n"
"{\n"
"    border:0.5px solid #ADADAD;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button:pressed,  #phase_table_widget QDoubleSpinBox::up-button:pressed{\n"
"    width: 10px;\n"
"    height: 8px;\n"
"}\n"
"#overlay_table_widget QDoubleSpinBox::down-button:pressed, #phase_table_widget QDoubleSpinBox::down-button:pressed {\n"
"    width: 10px;\n"
"    height: 8px;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::up-button, #phase_table_widget QDoubleSpinBox::up-button {\n"
"    image: url(dioptas/resources/icons/arrow_up.ico) 1;\n"
"}\n"
"\n"
"#overlay_table_widget QDoubleSpinBox::down-button, #phase_table_widget QDoubleSpinBox::down-button {\n"
"    image: url(dioptas/resources/icons/arrow_down.ico) 1;\n"
"}\n"
"\n"
"QFrame#main_frame {\n"
"    color: #F1F1F1;\n"
"    border: 1px solid #5B5B5B;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"#calibration_mode_btn, #mask_mode_btn, #integration_mode_btn {\n"
"    font: normal 12px;\n"
"    border-radius: 1px;\n"
"}\n"
"\n"
"#calibration_mode_btn {\n"
"   border-top-right-radius:8px;\n"
"   border-bottom-right-radius: 8px;\n"
"}\n"
"\n"
"#integration_mode_btn {\n"
"   border-top-left-radius:8px;\n"
"   border-bottom-left-radius: 8px;\n"
"}")
        self.GoButton = QtWidgets.QPushButton(Dialog)
        self.GoButton.setGeometry(QtCore.QRect(590, 210, 61, 51))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.GoButton.setFont(font)
        self.GoButton.setObjectName("GoButton")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(430, -30, 21, 411))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.line.setFont(font)
        self.line.setAutoFillBackground(False)
        self.line.setStyleSheet("color: rgb(0, 0, 0);")
        self.line.setFrameShadow(QtWidgets.QFrame.Plain)
        self.line.setLineWidth(1)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setObjectName("line")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(130, 20, 221, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 320, 241, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.instructionText = QtWidgets.QPlainTextEdit(Dialog)
        self.instructionText.setGeometry(QtCore.QRect(240, 60, 181, 241))
        self.instructionText.setObjectName("instructionText")
        self.procedureNumber = QtWidgets.QLineEdit(Dialog)
        self.procedureNumber.setGeometry(QtCore.QRect(190, 150, 31, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.procedureNumber.setFont(font)
        self.procedureNumber.setAlignment(QtCore.Qt.AlignCenter)
        self.procedureNumber.setObjectName("procedureNumber")
        self.depthValue = QtWidgets.QLineEdit(Dialog)
        self.depthValue.setGeometry(QtCore.QRect(190, 190, 31, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.depthValue.setFont(font)
        self.depthValue.setAlignment(QtCore.Qt.AlignCenter)
        self.depthValue.setObjectName("depthValue")
        self.runMill = QtWidgets.QPushButton(Dialog)
        self.runMill.setGeometry(QtCore.QRect(20, 230, 201, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.runMill.setFont(font)
        self.runMill.setObjectName("runMill")
        self.LabelPosition_2 = QtWidgets.QLabel(Dialog)
        self.LabelPosition_2.setGeometry(QtCore.QRect(20, 190, 161, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelPosition_2.setFont(font)
        self.LabelPosition_2.setAutoFillBackground(False)
        self.LabelPosition_2.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelPosition_2.setLineWidth(1)
        self.LabelPosition_2.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelPosition_2.setObjectName("LabelPosition_2")
        self.LabelPosition_3 = QtWidgets.QLabel(Dialog)
        self.LabelPosition_3.setGeometry(QtCore.QRect(20, 150, 161, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelPosition_3.setFont(font)
        self.LabelPosition_3.setAutoFillBackground(False)
        self.LabelPosition_3.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelPosition_3.setLineWidth(1)
        self.LabelPosition_3.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelPosition_3.setObjectName("LabelPosition_3")
        self.resetOrigin = QtWidgets.QPushButton(Dialog)
        self.resetOrigin.setGeometry(QtCore.QRect(20, 110, 201, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.resetOrigin.setFont(font)
        self.resetOrigin.setObjectName("resetOrigin")
        self.Instructions = QtWidgets.QPushButton(Dialog)
        self.Instructions.setGeometry(QtCore.QRect(390, 20, 31, 21))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(241, 241, 241))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(50, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.Instructions.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Instructions.setFont(font)
        self.Instructions.setStyleSheet("QPushButton{\n"
"background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"border-radius: 10px;\n"
"}")
        self.Instructions.setObjectName("Instructions")
        self.xyOrigin = QtWidgets.QPushButton(Dialog)
        self.xyOrigin.setGeometry(QtCore.QRect(20, 70, 201, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.xyOrigin.setFont(font)
        self.xyOrigin.setObjectName("xyOrigin")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(530, 20, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.ZValue = QtWidgets.QLCDNumber(Dialog)
        self.ZValue.setGeometry(QtCore.QRect(520, 160, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.ZValue.setFont(font)
        self.ZValue.setAutoFillBackground(False)
        self.ZValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.ZValue.setDigitCount(4)
        self.ZValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.ZValue.setObjectName("ZValue")
        self.XJog = QtWidgets.QLineEdit(Dialog)
        self.XJog.setGeometry(QtCore.QRect(590, 80, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.XJog.setFont(font)
        self.XJog.setAlignment(QtCore.Qt.AlignCenter)
        self.XJog.setObjectName("XJog")
        self.LabelJog = QtWidgets.QLabel(Dialog)
        self.LabelJog.setGeometry(QtCore.QRect(580, 50, 81, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelJog.setFont(font)
        self.LabelJog.setAutoFillBackground(False)
        self.LabelJog.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelJog.setLineWidth(1)
        self.LabelJog.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelJog.setObjectName("LabelJog")
        self.LabelPosition = QtWidgets.QLabel(Dialog)
        self.LabelPosition.setGeometry(QtCore.QRect(480, 50, 101, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelPosition.setFont(font)
        self.LabelPosition.setAutoFillBackground(False)
        self.LabelPosition.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelPosition.setLineWidth(1)
        self.LabelPosition.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelPosition.setObjectName("LabelPosition")
        self.YValue = QtWidgets.QLCDNumber(Dialog)
        self.YValue.setGeometry(QtCore.QRect(520, 120, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.YValue.setFont(font)
        self.YValue.setAutoFillBackground(False)
        self.YValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.YValue.setDigitCount(4)
        self.YValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.YValue.setObjectName("YValue")
        self.YJog = QtWidgets.QLineEdit(Dialog)
        self.YJog.setGeometry(QtCore.QRect(590, 120, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.YJog.setFont(font)
        self.YJog.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.YJog.setAlignment(QtCore.Qt.AlignCenter)
        self.YJog.setObjectName("YJog")
        self.LabelZ = QtWidgets.QLabel(Dialog)
        self.LabelZ.setGeometry(QtCore.QRect(490, 160, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelZ.setFont(font)
        self.LabelZ.setTextFormat(QtCore.Qt.PlainText)
        self.LabelZ.setScaledContents(False)
        self.LabelZ.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelZ.setWordWrap(False)
        self.LabelZ.setObjectName("LabelZ")
        self.LabelSpeed = QtWidgets.QLabel(Dialog)
        self.LabelSpeed.setGeometry(QtCore.QRect(480, 210, 111, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelSpeed.setFont(font)
        self.LabelSpeed.setAutoFillBackground(False)
        self.LabelSpeed.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelSpeed.setLineWidth(1)
        self.LabelSpeed.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelSpeed.setObjectName("LabelSpeed")
        self.XValue = QtWidgets.QLCDNumber(Dialog)
        self.XValue.setGeometry(QtCore.QRect(520, 80, 51, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.XValue.setFont(font)
        self.XValue.setAutoFillBackground(False)
        self.XValue.setStyleSheet("background-color: rgb(50,50,50);\n"
"border-style: solid;\n"
"border-color: white;\n"
"border-width: 1px;\n"
"")
        self.XValue.setDigitCount(4)
        self.XValue.setSegmentStyle(QtWidgets.QLCDNumber.Filled)
        self.XValue.setObjectName("XValue")
        self.LabelY = QtWidgets.QLabel(Dialog)
        self.LabelY.setGeometry(QtCore.QRect(490, 120, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelY.setFont(font)
        self.LabelY.setTextFormat(QtCore.Qt.PlainText)
        self.LabelY.setScaledContents(False)
        self.LabelY.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelY.setWordWrap(False)
        self.LabelY.setObjectName("LabelY")
        self.LabelX = QtWidgets.QLabel(Dialog)
        self.LabelX.setGeometry(QtCore.QRect(490, 80, 21, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelX.setFont(font)
        self.LabelX.setTextFormat(QtCore.Qt.PlainText)
        self.LabelX.setScaledContents(False)
        self.LabelX.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelX.setWordWrap(False)
        self.LabelX.setObjectName("LabelX")
        self.ZJog = QtWidgets.QLineEdit(Dialog)
        self.ZJog.setGeometry(QtCore.QRect(590, 160, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.ZJog.setFont(font)
        self.ZJog.setAlignment(QtCore.Qt.AlignCenter)
        self.ZJog.setObjectName("ZJog")
        self.speed = QtWidgets.QComboBox(Dialog)
        self.speed.setGeometry(QtCore.QRect(520, 240, 50, 22))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        self.LabelGcode = QtWidgets.QLabel(Dialog)
        self.LabelGcode.setGeometry(QtCore.QRect(500, 280, 111, 20))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.LabelGcode.setFont(font)
        self.LabelGcode.setAutoFillBackground(False)
        self.LabelGcode.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.LabelGcode.setLineWidth(1)
        self.LabelGcode.setAlignment(QtCore.Qt.AlignCenter)
        self.LabelGcode.setObjectName("LabelGcode")
        self.gcodeManual = QtWidgets.QLineEdit(Dialog)
        self.gcodeManual.setGeometry(QtCore.QRect(480, 300, 161, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        font.setStrikeOut(False)
        font.setKerning(True)
        self.gcodeManual.setFont(font)
        self.gcodeManual.setText("")
        self.gcodeManual.setAlignment(QtCore.Qt.AlignCenter)
        self.gcodeManual.setObjectName("gcodeManual")
        self.SendButton = QtWidgets.QPushButton(Dialog)
        self.SendButton.setGeometry(QtCore.QRect(650, 300, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.SendButton.setFont(font)
        self.SendButton.setObjectName("SendButton")
        self.Back = QtWidgets.QPushButton(Dialog)
        self.Back.setGeometry(QtCore.QRect(20, 270, 201, 31))
        font = QtGui.QFont()
        font.setPointSize(-1)
        self.Back.setFont(font)
        self.Back.setObjectName("Back")
        self.goX = QtWidgets.QPushButton(Dialog)
        self.goX.setGeometry(QtCore.QRect(660, 80, 51, 21))
        self.goX.setStyleSheet("")
        self.goX.setObjectName("goX")
        self.goZ = QtWidgets.QPushButton(Dialog)
        self.goZ.setGeometry(QtCore.QRect(660, 160, 51, 21))
        self.goZ.setStyleSheet("")
        self.goZ.setObjectName("goZ")
        self.goY = QtWidgets.QPushButton(Dialog)
        self.goY.setGeometry(QtCore.QRect(660, 120, 51, 21))
        self.goY.setStyleSheet("")
        self.goY.setObjectName("goY")
        
        self.GoButton.setDefault(True)
        self.instructionText.setReadOnly(True)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        self.speed.addItem("1")
        self.speed.addItem("2")
        self.speed.addItem("3")
        self.speed.addItem("4")
        self.speed.addItem("5")
        self.speed.setCurrentIndex(2)
        self.right_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("right"), Dialog)
        self.right_shortcut.activated.connect(lambda: tinyG.jog("X",0.5,200))
        self.right_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.left_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("left"), Dialog)
        self.left_shortcut.activated.connect(lambda: tinyG.jog("X",-0.5,200))
        self.left_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.up_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("up"), Dialog)
        self.up_shortcut.activated.connect(lambda: tinyG.jog("Y",0.5,200))
        self.up_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.down_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("down"), Dialog)
        self.down_shortcut.activated.connect(lambda: tinyG.jog("Y",-0.5,200))
        self.down_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.zero_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("PgDown"), Dialog)
        self.zero_shortcut.activated.connect(lambda: tinyG.jog("Z",-0.5,200))
        self.zero_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.one_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("PgUp"), Dialog)
        self.one_shortcut.activated.connect(lambda: tinyG.jog("Z",0.5,200))
        self.one_shortcut.activated.connect(lambda: self.updatePosition(tinyG))
        self.GoButton.setDefault(True)
        self.Instructions.clicked.connect(lambda: self.openInstructions())
        self.runMill.clicked.connect(lambda: self.runMilling(tinyG,probeCommands, Dialog))
        self.GoButton.clicked.connect(lambda: self.callJog(tinyG))
        self.xyOrigin.clicked.connect(lambda: self.goxyOrigin(tinyG))
        self.resetOrigin.clicked.connect(lambda: self.origin(tinyG))
        self.updatePosition(tinyG)
        self.SendButton.clicked.connect(lambda: self.serialCommand(tinyG))   
        self.Back.clicked.connect(lambda: self.openSetXYZ_Origin(tinyG,probeCommands))
        self.Back.clicked.connect(Dialog.close)
        self.goX.clicked.connect(lambda: self.callJogX(tinyG))
        self.goY.clicked.connect(lambda: self.callJogY(tinyG))
        self.goZ.clicked.connect(lambda: self.callJogZ(tinyG))
        self.retranslateUi(Dialog, probeCommands)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog, probeCommands):
        commandText=""
        counter=0
        for i in probeCommands:
            counter=counter+1
            commandText=commandText+"Procedure #"+str(counter)+"\nType: " +i.procedureType+"\n"+ "Parameters: "+i.parameter+"\nCurrent Depth: "+str(int(i.millingDepth*1000))+"\u03BCm\n\n"
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Milling Configurations"))
        self.label_4.setText(_translate("Dialog", "Milling Configurations"))
        self.label_2.setText(_translate("Dialog", "Craniobot v1.0 Created at U. of Minnesota"))
        self.instructionText.setPlainText(_translate("Dialog", commandText))
        self.procedureNumber.setText(_translate("Dialog", "1"))
        self.depthValue.setText(_translate("Dialog", "50"))
        self.runMill.setText(_translate("Dialog", "Run Mill"))
        self.LabelPosition_2.setText(_translate("Dialog", "<html><head/><body><p>Milling Depth (μm)</p></body></html>"))
        self.LabelPosition_3.setText(_translate("Dialog", "<html><head/><body><p>Procedure Number</p></body></html>"))
        self.resetOrigin.setText(_translate("Dialog", "Reset Origin"))
        self.Instructions.setText(_translate("Dialog", "?"))
        self.xyOrigin.setText(_translate("Dialog", "Go to XY Origin"))
        self.GoButton.setText(_translate("Dialog", "Go!"))
        self.label_3.setText(_translate("Dialog", "Set Position"))
        self.XJog.setText(_translate("Dialog", "0"))
        self.LabelJog.setText(_translate("Dialog", "Jog (mm)"))
        self.LabelPosition.setText(_translate("Dialog", "Position (mm)"))
        self.YJog.setText(_translate("Dialog", "0"))
        self.LabelZ.setText(_translate("Dialog", "Z"))
        self.LabelSpeed.setText(_translate("Dialog", "Speed (1-5)"))
        self.LabelY.setText(_translate("Dialog", "Y"))
        self.LabelX.setText(_translate("Dialog", "X"))
        self.ZJog.setText(_translate("Dialog", "0"))
        self.LabelGcode.setText(_translate("Dialog", "G-code command"))
        self.SendButton.setText(_translate("Dialog", "Send"))
        self.Back.setText(_translate("Dialog", "Back to Surface Profiling"))
        self.Back.setText(_translate("Dialog", "Back to Surface Profiling"))
        self.goX.setText(_translate("Dialog", "Go X"))
        self.goZ.setText(_translate("Dialog", "Go Z"))
        self.goY.setText(_translate("Dialog", "Go Y"))
        
# %%
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Select_Cranial_Procedure = QtWidgets.QDialog()
    ui = Ui_Select_Cranial_Procedure()
    ui.setupUi(Select_Cranial_Procedure)
    Select_Cranial_Procedure.show()
    sys.exit(app.exec_())
