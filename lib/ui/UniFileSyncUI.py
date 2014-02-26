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

        #setup list
        self.setupFolderList(self.ui.folderList)
        self.setupPluginList(self.ui.pluginList)

        #Init status bar
        stBarConf = self.confManager.getValue('UI', 'statusbar')
        self.statusbar.showMessage(stBarConf['messages']['init'])

        #connect the signal with slot
        self.connectUISlots(self.ui)

        #set UI label
        username = self.confManager.getValue('UI', 'username')
        self.ui.nameLabel.setText(username)

        #Start server immediately
        self.server.start()
        #self.server.getHandler('start')({'name': 'all'})
        msg = self.server.initMsg('start', None, MSG_UNIQUE_ID_T_CONTROLLER, False, {'name': 'all'})
        UMsgBus.getBus().send(msg)

        self.server.addCallBack(self.statusbarUpdate)
        self.server.addCallBack(self.infoLabelUpdate)

    def closeEvent(self, event):
        """override close event"""
        if self.trayIcon.isVisible():
            self.hide()
            event.ignore()

        self.confManager.save()
        logging.debug('[%s] is closed, window is hide, configuration is saved', self.getName())

    def createActions(self):
        """create tray icon menu action"""
        self.configAction = QAction("&ShowConfig", self, triggered=self.show)
        self.exitAction = QAction("&Exit", self)
        self.exitAction.triggered.connect(lambda: UMsgBus.getBus().send(self.server.initMsg('stop', None, MSG_UNIQUE_ID_T_CONTROLLER, False, {'name': 'all'})))
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

    def setupPluginList(self, pluginList):
        """setup plugin list from configuration file"""
        fts = self.confManager.getValue('common', 'plugins')
        i = 0
        for ft in fts:
            flistItem = QListWidgetItem(QIcon('icon/plugin.png'), ft['name'], pluginList)
            pluginList.insertItem(i, flistItem)
            i += 1

    def show(self):
        """ovrride parent show method"""
        super(UniFileSyncUI, self).show()

        #Init status bar
        stBarConf = self.confManager.getValue('UI', 'statusbar')
        self.statusbar.showMessage(stBarConf['messages']['init'])

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
                msg = self.server.initMsg('info', None, MSG_UNIQUE_ID_T_CONTROLLER, True, {'name': 'all'})
                UMsgBus.getBus().send(msg)
                #res, data = self.server.getHandler('info')({'name': 'all'})
                btn.setText('Connecting')
                #self.ui.infoLabel.setText(data)
                logging.debug('[%s]: Press Connect to getCloudInfo', self.getName())
            elif btn.text() == 'Disconnect':
                #self.server.getHandler('stop')({'name': 'all'})
                btn.setText('Connect')
                self.ui.infoLabel.setText('Cloud Disk is disconnected')

        elif btn is self.ui.addFolderBtn:
            fileDialog = QFileDialog(self)
            fileDialog.setWindowTitle('Select Folder')
            folderPath = fileDialog.getExistingDirectory()
            if folderPath != "":
                listItem = QListWidgetItem(QIcon('icon/folder.png'), folderPath, self.ui.folderList)
                self.ui.folderList.insertItem(self.ui.folderList.count(), listItem)
        elif btn is self.ui.rmFolderBtn:
            row = self.ui.folderList.currentRow()
            self.ui.folderList.takeItem(row)
            logging.debug('[%s]: remove item %d', self.getName(), row)

    def createStatusBar(self):
        """create status bar"""

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

    def setName(self, name):
        """set server name"""
        self.server.setName(name)

    def getName(self):
        """get server name"""
        return self.server.getName()

    def statusbarUpdate(self, param):
        """statusbar update callback"""
        logging.debug('[%s] statusbarUpdate called', self.getName())
        self.statusbar.showMessage(ERR_STR_TABLE[param['result']])

    def infoLabelUpdate(self, param):
        """infoLabelUpdate"""
        if param['data']:
            logging.debug('[%s] infoLabelUpdate called', self.getName())
            self.ui.infoLabel.setText(param['data'])
            self.ui.connBtn.setText('Disconnect')

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = UniFileSyncUI('UniFileSync UI')
    #w.show()
    sys.exit(app.exec_())
