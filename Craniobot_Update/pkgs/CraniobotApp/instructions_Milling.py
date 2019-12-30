# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'instructions_Milling.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_I_Milling(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(771, 643)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.plainTextEdit.setGeometry(QtCore.QRect(30, 30, 701, 581))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.plainTextEdit.setFont(font)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.plainTextEdit.setReadOnly(True)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.plainTextEdit.setPlainText(_translate("Dialog", "1) Coat the skull surface in a thin layer of sterile saline.\n"
"\n"
"2) Ensure there is no skin or fat tissue on the way of the milling path. (If there is any, cut it or push it away gently using a micro-curette or a cotton-tipped applicator). \n"
"\n"
"3) Autoclave the cutting tools prior to surgery. Sterilize the cutting tool using 70% ethanol and rinse it with saline. For craniotomies, a 200 µm square end mill works best, whereas for skull thinning a 300 µm ball end mill works best. \n"
"\n"
"4) Using jog commands retract the spindle to make room for tool exchange. Replace the surface profiler with the endmill. \n"
"\n"
"5) Press the “Go to XY origin” to bring the tool directly above bregma. Then, using the “z” axis jog command, slowly lower the endmill such that it meets bregma. Once the tool is just touching the skull surface at bregma, press the “Reset Origin” button (Fig xx). \n"
"\n"
"Tip: the reference image taken in step XX is useful for ensuring the endmill is at the same bregma location.\n"
"\n"
"CRITICAL!! Ensure the endmill is registered to the same position, else, the craniotomy will be lateral offset. If there is a lateral offset, use the “x,y” jog commands to realign with bregma.  \n"
"\n"
"CRITICAL!! Ensure the endmill is not exerting force on the skull when registering the origin. This may result in an offset in the z direction below the plane that surface profiling was performed in, leading to inaccurate drilling depths.\n"
"\n"
"CAUTION! Ensure the tip of the end mill is above the top most point of the skull by atleast 1 mm before pressing ‘Got to XY origin’\n"
"\n"
"6) Apply saline to keep the skull moist and cool during the procedure. The text window on the right of panel 1 of the GUI will show the configuration of the selected procedures as well as the current drilling depth. Enter the number of the desired milling procedure and the drilling depth for the first iteration. A reasonable number to start with is 40-50 µm. The value entered is how much deeper the machine is going to drill with respect to the current depth shown on the right.\n"
"\n"
"7) Turn on the DC power source connected to the spindle.\n"
"\n"
"8) Milling: Press the “Run Mill” button to start skull milling procedure. An html window will open to display the interpolated 3D milling path. \n"
"\n"
"9) The Craniobot will start milling the skull. After the first milling pass, the spindle is taken back to the origin. Repeat steps 6-8 until the desired depth has been achieved for each cranial procedure.\n"
""))
        
class Ui_I_Probing(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(650, 537)
        self.instructionText = QtWidgets.QPlainTextEdit(Dialog)
        self.instructionText.setGeometry(QtCore.QRect(30, 30, 581, 471))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.instructionText.setFont(font)
        self.instructionText.setObjectName("instructionText")
        self.instructionText.setReadOnly(True)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.instructionText.setPlainText(_translate("Dialog", "1) The text box on the right lists the procedures in the order that they were selected. Procedures can be removed using the ‘Remove Procedure’ button. More procedures can be added by clicking the ‘Add More Procedures’ button, which will revert the GUI back to procedure selection mode. Proceed to the next step if the procedures listed in the text box are as desired. \n"
"\n"
"2) Use the jog commands in the panel on the right of the GUI to guide the surface profiler’s stylus tip to ~1-2 mm above bregma. CAUTION!! As the tip approaches bregma, decrease the speed and/or distance for fine adjustments to avoid accidentally touching the stylus through the skull. \n"
"\n"
"3) Press “Find Origin” button. The Craniobot will lower the stylus tip down at a rate of 5 mm/min until it touches the skull surface. \n"
"\n"
"4) Verify that the stylus tip is at bregma by visualizing it under a stereomicroscope. If it is not, raise it ~1 mm in the z direction using jog commands, then make fine lateral adjustments in the x-y direction to position it above bregma. Once the stylus tip is above bregma, press “Set Origin”. Repeat steps 4-5 until satisfied with the position of the stylus at bregma. Tip: Using the trinocular camera, or eye piece camera on the microscope, take a photograph of the position of the stylus tip on the surface of the skull. This will be useful as a reference setting the origin of the cutting tool during step xx.\n"
"\n"
"5) Click “Start Surface Profiling” button. The Craniobot will begin surface profiling.\n"
"\n"
"Tip: It is highly recommended to watch the first few measurements to make sure that the surface profiler does not make false positive measurements. If it does, immediately stop the machine using the emergency push button. Retry once if a false positive is measured. If the issue persists, refer to the troubleshooting steps in the Machine Startup section about how to reduce surface profiler errors. Once the profiling is completed, the software will automatically open an html window with a 3D plot with the measured points for each of the procedures selected.\n"
"\n"
"\n"
""))

class Ui_I_Select(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(757, 503)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.plainTextEdit.setGeometry(QtCore.QRect(30, 30, 691, 441))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(9)
        self.plainTextEdit.setFont(font)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.plainTextEdit.setReadOnly(True)
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.plainTextEdit.setPlainText(_translate("Dialog", "1) Make sure all the pre-operation steps have been executed before moving onto the next steps.\n"
"\n"
"2) A list of four choices are available to the user: (i) Circular craniotomy, (ii) skull thinning, (iii) craniotomy of arbitrary shape and (iv) anchor hole drilling. Click on the desired craniobot procedures. Multiple procedures can be selected if needed. Select a cranial procedure from this list. \n"
"\n"
"(i) If “Circular Craniotomy” was selected, panel 1 of the GUI provides the user with options to specify the location and dimensions of the circular craniotomy . Enter the location of the center of the craniotomy (x and y coordinates relative to bregma) the diameter of the craniotomy and the number of points along the circular perimeter where the skull surface needs to be profiled. Click ‘Next’ when done.\n"
"\n"
"(ii) If “Other Craniotomy Patterns”, was selected, the GUI will prompt the user to upload a comma-separated values (.csv) file with x and y coordinates (relative to bregma) of pilot points where surface profiling needs to be performed. Upload the .csv file specifying the desired craniotomy profile. Click ‘Next’ when done. NOTE: The profiling will be more accurate if the number points specified is higher, but also requires more time to profile. In general, profiling points ~0.5 mm apart along the perimeter is sufficient.  \n"
"\n"
"(iii) If “Skull Thinning” was selected, panel 1 of the GUI provides the user with options to specify the location and dimensions of rectangular area for skull thinning. Specify the x and y coordinates of two non-adjacent vertexes of a rectangle. The Craniobot will generate a raster pattern with points separated by 0.15 mm covering the rectangular area. \n"
"\n"
"(iv) If “Anchor Hole Drilling” option was selected, the GUI will prompt a window asking for the x and y coordinates where the bone screws need to be implanted. Enter the desired location and click ‘Next’.\n"
"\n"
"3) Clicking ‘Next’ in the previous step results in the GUI returning to the procedure selection mode. If more than one procedure is desired (e.g., circular craniotomy and anchor hole) repeat Step 2. After choosing the desired cranial procedures, press “Surface Profiling Configuration” button.  This GUI will now move to the Surface profiling configurations mode"))


class Ui_I_Jog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(557, 303)
        self.frame_5 = QtWidgets.QFrame(Dialog)
        self.frame_5.setGeometry(QtCore.QRect(400, 60, 91, 71))
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_5.setObjectName("frame_5")
        self.label = QtWidgets.QLabel(self.frame_5)
        self.label.setGeometry(QtCore.QRect(20, 20, 61, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.frame_6 = QtWidgets.QFrame(Dialog)
        self.frame_6.setGeometry(QtCore.QRect(400, 140, 91, 71))
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_6.setObjectName("frame_6")
        self.label_2 = QtWidgets.QLabel(self.frame_6)
        self.label_2.setGeometry(QtCore.QRect(20, 20, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.frame_7 = QtWidgets.QFrame(Dialog)
        self.frame_7.setGeometry(QtCore.QRect(160, 140, 81, 71))
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_7.setObjectName("frame_7")
        self.label_5 = QtWidgets.QLabel(self.frame_7)
        self.label_5.setGeometry(QtCore.QRect(30, 10, 31, 51))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(27)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.frame_8 = QtWidgets.QFrame(Dialog)
        self.frame_8.setGeometry(QtCore.QRect(250, 140, 81, 71))
        self.frame_8.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_8.setObjectName("frame_8")
        self.label_3 = QtWidgets.QLabel(self.frame_8)
        self.label_3.setGeometry(QtCore.QRect(20, 10, 51, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(27)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.frame_9 = QtWidgets.QFrame(Dialog)
        self.frame_9.setGeometry(QtCore.QRect(70, 140, 81, 71))
        self.frame_9.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_9.setObjectName("frame_9")
        self.label_4 = QtWidgets.QLabel(self.frame_9)
        self.label_4.setGeometry(QtCore.QRect(20, 10, 51, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(27)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.frame_10 = QtWidgets.QFrame(Dialog)
        self.frame_10.setGeometry(QtCore.QRect(160, 60, 81, 71))
        self.frame_10.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame_10.setObjectName("frame_10")
        self.label_6 = QtWidgets.QLabel(self.frame_10)
        self.label_6.setGeometry(QtCore.QRect(30, 10, 31, 41))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(27)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setGeometry(QtCore.QRect(190, 20, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setGeometry(QtCore.QRect(190, 220, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setGeometry(QtCore.QRect(40, 160, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(Dialog)
        self.label_10.setGeometry(QtCore.QRect(340, 160, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(Dialog)
        self.label_11.setGeometry(QtCore.QRect(500, 80, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(Dialog)
        self.label_12.setGeometry(QtCore.QRect(500, 160, 51, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(Dialog)
        self.label_13.setGeometry(QtCore.QRect(60, 260, 181, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "PgUp"))
        self.label_2.setText(_translate("Dialog", "PgDn"))
        self.label_5.setText(_translate("Dialog", "<html><head/><body><p>↓</p></body></html>"))
        self.label_3.setText(_translate("Dialog", "<html><head/><body><p>→</p></body></html>"))
        self.label_4.setText(_translate("Dialog", "<html><head/><body><p>←</p></body></html>"))
        self.label_6.setText(_translate("Dialog", "<html><head/><body><p>↑</p></body></html>"))
        self.label_7.setText(_translate("Dialog", "Y+"))
        self.label_8.setText(_translate("Dialog", "Y-"))
        self.label_9.setText(_translate("Dialog", "X-"))
        self.label_10.setText(_translate("Dialog", "X+"))
        self.label_11.setText(_translate("Dialog", "Z+"))
        self.label_12.setText(_translate("Dialog", "Z-"))
        self.label_13.setText(_translate("Dialog", "Speed: #*100 mm/min"))

