"""
Craniobot: start screen
University of Minnesota - Twin Cities
Biosensing and Biorobotics Lab
author: Daniel Sousa Schulman
email: sousa013@umn.edu // dschul@umich.edu
PI: Suhasa Kodandaramaiah (suhasabk@umn.edu)
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from CraniobotApp.Select_Cranial_Procedure import Ui_Select_Cranial_Procedure

class Ui_Initial(object):
    
    def  openSelect_Cranial_Procedure(self):
        self.window = QtWidgets.QDialog()
        self.uiSelect_Cranial_Procedure = Ui_Select_Cranial_Procedure()
        self.uiSelect_Cranial_Procedure.setupUi(self.window)
        self.window.show()
        
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(892, 719)
        self.StartButton = QtWidgets.QPushButton(Dialog)
        self.StartButton.setGeometry(QtCore.QRect(380, 590, 151, 61))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.StartButton.setFont(font)
        self.StartButton.setObjectName("StartButton")
        self.CraniobotLabel = QtWidgets.QLabel(Dialog)
        self.CraniobotLabel.setGeometry(QtCore.QRect(310, 510, 281, 81))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(26)
        self.CraniobotLabel.setFont(font)
        self.CraniobotLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.CraniobotLabel.setObjectName("CraniobotLabel")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(120, 490, 211, 211))
        self.label.setObjectName("label")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(620, 550, 341, 91))
        self.label_3.setObjectName("label_3")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(100, 10, 691, 501))
        self.label_2.setObjectName("label_2")
        
        self.StartButton.clicked.connect(lambda: self.openSelect_Cranial_Procedure())
        self.StartButton.clicked.connect(Dialog.close)
        
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.StartButton.setText(_translate("Dialog", "START"))
        self.CraniobotLabel.setText(_translate("Dialog", "Craniobot 2019.1"))
        self.label.setText(_translate("Dialog", "<html><head/><body><p><img src=\":/newPrefix/lab-logo1.jpg\"/></p></body></html>"))
        self.label_3.setText(_translate("Dialog", "<html><head/><body><p><img src=\":/newPrefix/UMN-Logo2.png\"/></p></body></html>"))
        self.label_2.setText(_translate("Dialog", "<html><head/><body><p><img src=\":/newPrefix/cranioFront.jpg\"/></p></body></html>"))

import CraniobotApp.test2
import CraniobotApp.test3
import CraniobotApp.test


def main():
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Initial = QtWidgets.QDialog()
    ui = Ui_Initial()
    ui.setupUi(Initial)
    Initial.show()
    sys.exit(app.exec_())
