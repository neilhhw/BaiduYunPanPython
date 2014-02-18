# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UniFileSyncPop.ui'
#
# Created: Tue Feb 18 10:15:31 2014
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

class Ui_UniFileSyncPop(object):
    def setupUi(self, UniFileSyncPop):
        UniFileSyncPop.setObjectName(_fromUtf8("UniFileSyncPop"))
        UniFileSyncPop.resize(529, 369)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(UniFileSyncPop.sizePolicy().hasHeightForWidth())
        UniFileSyncPop.setSizePolicy(sizePolicy)
        self.nameLabel = QtGui.QLabel(UniFileSyncPop)
        self.nameLabel.setGeometry(QtCore.QRect(20, 10, 91, 41))
        self.nameLabel.setObjectName(_fromUtf8("nameLabel"))
        self.connBtn = QtGui.QPushButton(UniFileSyncPop)
        self.connBtn.setGeometry(QtCore.QRect(150, 20, 75, 23))
        self.connBtn.setObjectName(_fromUtf8("connBtn"))
        self.mainTabWidget = QtGui.QTabWidget(UniFileSyncPop)
        self.mainTabWidget.setGeometry(QtCore.QRect(0, 70, 531, 281))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainTabWidget.sizePolicy().hasHeightForWidth())
        self.mainTabWidget.setSizePolicy(sizePolicy)
        self.mainTabWidget.setObjectName(_fromUtf8("mainTabWidget"))
        self.folderTab = QtGui.QWidget()
        self.folderTab.setObjectName(_fromUtf8("folderTab"))
        self.scrollArea = QtGui.QScrollArea(self.folderTab)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 401, 261))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 399, 259))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.folderList = QtGui.QListWidget(self.scrollAreaWidgetContents)
        self.folderList.setGeometry(QtCore.QRect(0, 0, 401, 261))
        self.folderList.setObjectName(_fromUtf8("folderList"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.addFolderBtn = QtGui.QPushButton(self.folderTab)
        self.addFolderBtn.setGeometry(QtCore.QRect(430, 40, 75, 23))
        self.addFolderBtn.setObjectName(_fromUtf8("addFolderBtn"))
        self.RmFolderBtn = QtGui.QPushButton(self.folderTab)
        self.RmFolderBtn.setGeometry(QtCore.QRect(430, 110, 75, 23))
        self.RmFolderBtn.setObjectName(_fromUtf8("RmFolderBtn"))
        self.mainTabWidget.addTab(self.folderTab, _fromUtf8(""))
        self.NetTab = QtGui.QWidget()
        self.NetTab.setObjectName(_fromUtf8("NetTab"))
        self.serverLabel = QtGui.QLabel(self.NetTab)
        self.serverLabel.setGeometry(QtCore.QRect(20, 30, 91, 31))
        self.serverLabel.setObjectName(_fromUtf8("serverLabel"))
        self.serverLineEdit = QtGui.QLineEdit(self.NetTab)
        self.serverLineEdit.setGeometry(QtCore.QRect(110, 40, 121, 20))
        self.serverLineEdit.setObjectName(_fromUtf8("serverLineEdit"))
        self.proxyNameLabel = QtGui.QLabel(self.NetTab)
        self.proxyNameLabel.setGeometry(QtCore.QRect(20, 70, 91, 31))
        self.proxyNameLabel.setObjectName(_fromUtf8("proxyNameLabel"))
        self.proxyNameLineEdit = QtGui.QLineEdit(self.NetTab)
        self.proxyNameLineEdit.setGeometry(QtCore.QRect(110, 80, 121, 20))
        self.proxyNameLineEdit.setObjectName(_fromUtf8("proxyNameLineEdit"))
        self.proxyPwdLabel = QtGui.QLabel(self.NetTab)
        self.proxyPwdLabel.setGeometry(QtCore.QRect(20, 110, 91, 31))
        self.proxyPwdLabel.setObjectName(_fromUtf8("proxyPwdLabel"))
        self.proxyPwdLineEdit = QtGui.QLineEdit(self.NetTab)
        self.proxyPwdLineEdit.setGeometry(QtCore.QRect(110, 120, 121, 20))
        self.proxyPwdLineEdit.setObjectName(_fromUtf8("proxyPwdLineEdit"))
        self.saveBtn = QtGui.QPushButton(self.NetTab)
        self.saveBtn.setGeometry(QtCore.QRect(100, 210, 75, 23))
        self.saveBtn.setObjectName(_fromUtf8("saveBtn"))
        self.resetBtn = QtGui.QPushButton(self.NetTab)
        self.resetBtn.setGeometry(QtCore.QRect(300, 210, 75, 23))
        self.resetBtn.setObjectName(_fromUtf8("resetBtn"))
        self.mainTabWidget.addTab(self.NetTab, _fromUtf8(""))
        self.confTab = QtGui.QWidget()
        self.confTab.setObjectName(_fromUtf8("confTab"))
        self.mainTabWidget.addTab(self.confTab, _fromUtf8(""))
        self.pluginTab = QtGui.QWidget()
        self.pluginTab.setObjectName(_fromUtf8("pluginTab"))
        self.pluginList = QtGui.QListWidget(self.pluginTab)
        self.pluginList.setGeometry(QtCore.QRect(0, 0, 371, 261))
        self.pluginList.setObjectName(_fromUtf8("pluginList"))
        self.unloadBtn = QtGui.QPushButton(self.pluginTab)
        self.unloadBtn.setGeometry(QtCore.QRect(400, 110, 75, 23))
        self.unloadBtn.setObjectName(_fromUtf8("unloadBtn"))
        self.reloadBtn = QtGui.QPushButton(self.pluginTab)
        self.reloadBtn.setGeometry(QtCore.QRect(400, 180, 75, 23))
        self.reloadBtn.setObjectName(_fromUtf8("reloadBtn"))
        self.addBtn = QtGui.QPushButton(self.pluginTab)
        self.addBtn.setGeometry(QtCore.QRect(400, 50, 75, 23))
        self.addBtn.setObjectName(_fromUtf8("addBtn"))
        self.mainTabWidget.addTab(self.pluginTab, _fromUtf8(""))
        self.infoLabel = QtGui.QLabel(UniFileSyncPop)
        self.infoLabel.setGeometry(QtCore.QRect(290, 10, 221, 61))
        self.infoLabel.setObjectName(_fromUtf8("infoLabel"))

        self.retranslateUi(UniFileSyncPop)
        self.mainTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(UniFileSyncPop)

    def retranslateUi(self, UniFileSyncPop):
        UniFileSyncPop.setWindowTitle(_translate("UniFileSyncPop", "UniFileSyncPop", None))
        self.nameLabel.setText(_translate("UniFileSyncPop", "Hou Hongwei", None))
        self.connBtn.setText(_translate("UniFileSyncPop", "Connect", None))
        self.folderList.setSortingEnabled(True)
        self.addFolderBtn.setText(_translate("UniFileSyncPop", "Add", None))
        self.RmFolderBtn.setText(_translate("UniFileSyncPop", "Remove", None))
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.folderTab), _translate("UniFileSyncPop", "Folders", None))
        self.serverLabel.setText(_translate("UniFileSyncPop", "Proxy Server", None))
        self.proxyNameLabel.setText(_translate("UniFileSyncPop", "User Name", None))
        self.proxyPwdLabel.setText(_translate("UniFileSyncPop", "Password", None))
        self.saveBtn.setText(_translate("UniFileSyncPop", "Save", None))
        self.resetBtn.setText(_translate("UniFileSyncPop", "Reset", None))
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.NetTab), _translate("UniFileSyncPop", "Network", None))
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.confTab), _translate("UniFileSyncPop", "Configuration", None))
        self.unloadBtn.setText(_translate("UniFileSyncPop", "unload", None))
        self.reloadBtn.setText(_translate("UniFileSyncPop", "reload", None))
        self.addBtn.setText(_translate("UniFileSyncPop", "add", None))
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.pluginTab), _translate("UniFileSyncPop", "Plugins", None))
        self.infoLabel.setText(_translate("UniFileSyncPop", "Cloud Disk info label", None))

