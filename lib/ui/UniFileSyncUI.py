#!/usr/bin/env python
#-*- coding:utf-8 -*-
from PyQt4.QtCore import QString, SIGNAL, SLOT
from PyQt4.QtGui import (
        QApplication,
        QWidget,
        QSystemTrayIcon,
        QIcon,
        QMenu,
        QAction,
        QDialog,
        QListWidgetItem,
        QMainWindow,
        QStatusBar,
        QFileDialog,
        qApp)

from UniFileSyncPop import Ui_UniFileSyncPop

from UniFileSync.lib.common.ConfManager import ConfManager
from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.MsgBus import *
from UniFileSync.lib.common.Error import *
from UniFileSync.lib.common.UServer import UServer

class UniFileSyncUI(QMainWindow):
    """UniFileSyncUI class"""
    def __init__(self, name=None):
        super(UniFileSyncUI, self).__init__()

        self.confManager = ConfManager.getManager()

        self.ui = Ui_UniFileSyncPop()
        self.ui.setupUi(self)

        self.setFixedSize(self.size())

        self.server = UServer()
        self.server.regSelfToBus()

        if name:
            self.server.setName(name)

        self.createActions()
        self.createTrayIcon()
        self.createStatusBar()

        qApp.setQuitOnLastWindowClosed(False)

        self.trayIcon.show()
        self.showTrayIconMessage()

        #setup folder list
        self.setupFolderList(self.ui.folderList)

    def closeEvent(self, event):
        """override close event"""
        logging.debug('[%s] is closed', self.server.getName())

    def createActions(self):
        """create tray icon menu action"""
        self.configAction = QAction("&ShowConfig", self, triggered=self.show)
        self.exitAction = QAction("&Exit", self)
        self.exitAction.triggered.connect(lambda: self.server.getHandler('stop')({'name': 'all'}))
        self.exitAction.triggered.connect(qApp.quit)

    def createTrayIcon(self):
        """create system tray icon"""
        self.trayIconMenu = QMenu(self)
        es = self.trayIconMenu.addAction(self.configAction)

        self.trayIconMenu.addSeparator()

        ea = self.trayIconMenu.addAction(self.exitAction)

        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)
        self.trayIcon.setIcon(QIcon('icon/tray.png'))

    def showTrayIconMessage(self):
        """show tray icon message"""
        conf = self.confManager.getValue('UI', 'trayicon')
        popup = conf['popup']

        self.trayIcon.showMessage(popup['title'], popup['message'])

    def setupFolderList(self, folderList):
        """setup folder list for showing"""
        fts = self.confManager.getValue('common', 'folders')
        i = 0
        for ft in fts:
            flistItem = QListWidgetItem(QIcon('icon/folder.png'), ft, folderList)
            folderList.insertItem(i, flistItem)
            i += 1

    def show(self):
        """ovrride parent show method"""
        super(UniFileSyncUI, self).show()

        #Init status bar
        stBarConf = self.confManager.getValue('UI', 'statusbar')
        self.statusbar.showMessage(stBarConf['messages']['init'])


        #connect the signal with slot
        self.connectUISlots(self.ui)

        #set UI label
        username = self.confManager.getValue('UI', 'username')
        self.ui.nameLabel.setText(username)

    def connectUISlots(self, ui):
        """connect ui component with slots"""
        ui.connBtn.clicked.connect(lambda : self.connBtnSlots(ui.connBtn))
        ui.addFolderBtn.clicked.connect(lambda: self.connBtnSlots(ui.addFolderBtn))
        ui.rmFolderBtn.clicked.connect(lambda: self.connBtnSlots(ui.rmFolderBtn))

    def connBtnSlots(self, btn):
        """docstring for connBtnSlots"""
        if btn is self.ui.connBtn:
            if btn.text() == 'Connect':
                self.server.getHandler('start')({'name': 'all'})
                btn.setText('Disconnect')
            else:
                self.server.getHandler('stop')({'name': 'all'})
        elif btn is self.ui.addFolderBtn:
            fileDialog = QFileDialog(self)
            fileDialog.setWindowTitle('Select Folder')
            folderPath = fileDialog.getExistingDirectory()
            if folderPath != "":
                listItem = QListWidgetItem(QIcon('icon/folder.png'), folderPath, self.ui.folderList)
                self.ui.folderList.insertItem(self.ui.folderList.count(), listItem)
        elif btn is self.ui.rmFolderBtn:
            listItem = self.ui.folderList.currentItem()
            print listItem.text()
            self.ui.folderList.removeItemWidget(listItem)

    def createStatusBar(self):
        """create status bar"""

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = UniFileSyncUI('UniFileSync UI')
    #w.show()
    sys.exit(app.exec_())
