# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UniFileSyncPop.ui'
#
# Created: Wed Feb 12 10:42:48 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(497, 350)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.label = QtGui.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(50, 10, 161, 41))
        self.label.setObjectName(_fromUtf8("label"))
        self.pushButton = QtGui.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(340, 20, 75, 23))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.tabWidget = QtGui.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(0, 70, 501, 281))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.scrollArea = QtGui.QScrollArea(self.tab)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 501, 261))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 499, 259))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.listWidget = QtGui.QListWidget(self.scrollAreaWidgetContents)
        self.listWidget.setGeometry(QtCore.QRect(0, 0, 501, 261))
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.label_2 = QtGui.QLabel(self.tab_2)
        self.label_2.setGeometry(QtCore.QRect(20, 30, 91, 31))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.lineEdit = QtGui.QLineEdit(self.tab_2)
        self.lineEdit.setGeometry(QtCore.QRect(110, 40, 121, 20))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.label_3 = QtGui.QLabel(self.tab_2)
        self.label_3.setGeometry(QtCore.QRect(20, 70, 91, 31))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.lineEdit_2 = QtGui.QLineEdit(self.tab_2)
        self.lineEdit_2.setGeometry(QtCore.QRect(110, 80, 121, 20))
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.label_4 = QtGui.QLabel(self.tab_2)
        self.label_4.setGeometry(QtCore.QRect(20, 110, 91, 31))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.lineEdit_3 = QtGui.QLineEdit(self.tab_2)
        self.lineEdit_3.setGeometry(QtCore.QRect(110, 120, 121, 20))
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.pushButton_2 = QtGui.QPushButton(self.tab_2)
        self.pushButton_2.setGeometry(QtCore.QRect(90, 210, 75, 23))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.pushButton_3 = QtGui.QPushButton(self.tab_2)
        self.pushButton_3.setGeometry(QtCore.QRect(320, 210, 75, 23))
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self.listWidget_2 = QtGui.QListWidget(self.tab_4)
        self.listWidget_2.setGeometry(QtCore.QRect(0, 0, 371, 261))
        self.listWidget_2.setObjectName(_fromUtf8("listWidget_2"))
        self.pushButton_4 = QtGui.QPushButton(self.tab_4)
        self.pushButton_4.setGeometry(QtCore.QRect(390, 40, 75, 23))
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.pushButton_5 = QtGui.QPushButton(self.tab_4)
        self.pushButton_5.setGeometry(QtCore.QRect(390, 130, 75, 23))
        self.pushButton_5.setObjectName(_fromUtf8("pushButton_5"))
        self.tabWidget.addTab(self.tab_4, _fromUtf8(""))

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label.setText(_translate("Form", "Hou Hongwei", None))
        self.pushButton.setText(_translate("Form", "Connect", None))
        self.listWidget.setSortingEnabled(True)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Folders", None))
        self.label_2.setText(_translate("Form", "Proxy Server", None))
        self.label_3.setText(_translate("Form", "User Name", None))
        self.label_4.setText(_translate("Form", "Password", None))
        self.pushButton_2.setText(_translate("Form", "Save", None))
        self.pushButton_3.setText(_translate("Form", "Reset", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "Network", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Form", "Configuration", None))
        self.pushButton_4.setText(_translate("Form", "unload", None))
        self.pushButton_5.setText(_translate("Form", "reload", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("Form", "Plugins", None))

