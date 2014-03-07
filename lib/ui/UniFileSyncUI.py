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
from UniFileSync.lib.common.PluginManager import PluginManager

class UniFileSyncUI(QMainWindow):
    """UniFileSyncUI class"""
    def __init__(self, name=None):
        super(UniFileSyncUI, self).__init__()

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

        #connect the signal with slot
        self.connectUISlots(self.ui)
        #set UI label
        username = ConfManager.getManager().getValue('UI', 'username')
        self.ui.nameLabel.setText(username)

        #Start server immediately
        self.server.start()
        #self.server.getHandler('start')({'name': 'all'})
        msg = self.server.initMsg('start', None, MSG_UNIQUE_ID_T_CONTROLLER, False, {'name': 'all'})
        UMsgBus.getBus().send(msg)

        self.server.addCallBack(self.statusupdate)
        self.server.addCallBack(self.infoLabelUpdate)

        #setup list
        self.setupFolderList(self.ui.folderList)
        self.setupPluginList(self.ui.pluginList)
        self.setupNetworkConf()

        #Init status bar
        stBarConf = ConfManager.getManager().getValue('UI', 'statusbar')
        self.statusbar.showMessage(stBarConf['messages']['init'])

        #Init system icon
        self.trayIcon.show()
        self.showTrayIconMessage()


    def setupNetworkConf(self):
        """setup network configuration into UI"""
        conf = ConfManager.getManager().getValue('common', 'network')
        self.ui.proxyLineEdit.setText(conf['proxy'])
        self.ui.portLineEdit.setText("%s" % conf['port'])

    def closeEvent(self, event):
        """override close event"""
        if self.trayIcon.isVisible():
            self.hide()
            event.ignore()

        ConfManager.getManager().save()
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
        conf = ConfManager.getManager().getValue('UI', 'trayicon')
        popup = conf['popup']

        self.trayIcon.showMessage(popup['title'], popup['message'])

    def setupFolderList(self, folderList):
        """setup folder list for showing"""
        fts = ConfManager.getManager().getValue('common', 'folders')
        i = 0
        for ft in fts:
            flistItem = QListWidgetItem(QIcon('icon/folder.png'), ft, folderList)
            folderList.insertItem(i, flistItem)
            i += 1

    def setupPluginList(self, pluginList):
        """setup plugin list from configuration file"""
        fts = ConfManager.getManager().getValue('common', 'plugins')
        i = 0
        for ft in fts:
            flistItem = QListWidgetItem(QIcon('icon/plugin.png'), ft['name'], pluginList)
            pluginList.insertItem(i, flistItem)
            i += 1

    def show(self):
        """ovrride parent show method"""
        super(UniFileSyncUI, self).show()

        #Init status bar
        stBarConf = ConfManager.getManager().getValue('UI', 'statusbar')
        self.statusbar.showMessage(stBarConf['messages']['init'])

        #set UI label
        username = ConfManager.getManager().getValue('UI', 'username')
        self.ui.nameLabel.setText(username)

    def connectUISlots(self, ui):
        """connect ui component with slots"""
        ui.connBtn.clicked.connect(lambda : self.connBtnSlots(ui.connBtn))
        ui.addFolderBtn.clicked.connect(lambda: self.connBtnSlots(ui.addFolderBtn))
        ui.rmFolderBtn.clicked.connect(lambda: self.connBtnSlots(ui.rmFolderBtn))
        ui.saveBtn.clicked.connect(lambda: self.connBtnSlots(ui.saveBtn))
        ui.unloadBtn.clicked.connect(lambda: self.connBtnSlots(ui.unloadBtn))
        ui.reloadBtn.clicked.connect(lambda: self.connBtnSlots(ui.reloadBtn))
        ui.resetBtn.clicked.connect(lambda: self.connBtnSlots(ui.resetBtn))
        ui.addPluginBtn.clicked.connect(lambda: self.connBtnSlots(ui.addPluginBtn))

        self.connect(self, SIGNAL('statusupdate(int)'), self, SLOT('statusbarUpdate(int)'))

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
                logging.debug('[%s]: add folder path %s', self.getName(), str(folderPath))
                self.ui.folderList.insertItem(self.ui.folderList.count(), listItem)
                folderList = ConfManager.getManager().getValue('common', 'folders')
                folderList.append(str(folderPath))
                ConfManager.getManager().setValue('common', 'folders', folderList)
                #send watch dir request
                msg =  self.server.initMsg('watch', None, MSG_UNIQUE_ID_T_CONTROLLER, True, {'path': str(folderPath), 'action': 'add'})
                UMsgBus.getBus().send(msg)
                self.statusbar.showMessage('Adding watch path %s' % folderPath)

        elif btn is self.ui.rmFolderBtn:
            row = self.ui.folderList.currentRow()
            item = self.ui.folderList.currentItem()
            folderList = ConfManager.getManager().getValue('common', 'folders')
            self.statusbar.showMessage('Removing watch path %s' % item.text())
            folderList.remove(str(item.text()))
            ConfManager.getManager().setValue('common', 'folders', folderList)
            logging.debug('[%s]: remove item %d %s', self.getName(), row, item.text())
            msg =  self.server.initMsg('watch', None, MSG_UNIQUE_ID_T_CONTROLLER, True, {'path': str(item.text()), 'action': 'rm'})
            UMsgBus.getBus().send(msg)
            self.ui.folderList.takeItem(row)

        elif btn is self.ui.saveBtn:
            proxyConf = ConfManager.getManager().getValue('common', 'network')
            server = str(self.ui.proxyLineEdit.text())

            if server != "" and server != None:
                user = str(self.ui.proxyNameLineEdit.text())
                password = str(self.ui.proxyPwdLineEdit.text())
                logging.debug('[%s]: save server=>%s user=>%s password=>%s into configuration',
                              self.getName(), server, user, password)
                proxyConf['proxy'] = server
                proxyConf['user'] = user
                proxyConf['password'] = password
                ConfManager.getManager().setValue('common', 'network', proxyConf)
                msg =  self.server.initMsg('proxy', None, MSG_UNIQUE_ID_T_CONTROLLER, True,
                            {'http': 'http://%s' % server, 'https': 'https://%s' % server})
                UMsgBus.getBus().send(msg)
                self.statusbar.showMessage('Applying proxy %s' % server)

                ConfManager.getManager().save()

        elif btn is self.ui.resetBtn:
            proxyConf = ConfManager.getManager().getValue('common', 'network')
            server = proxyConf['proxy']
            user = proxyConf['user']
            password = proxyConf['password']
            port = proxyConf['port']

            self.ui.proxyLineEdit.setText(server)
            self.ui.proxyNameLineEdit.setText(user)
            self.ui.proxyPwdLineEdit.setText(password)
            self.ui.portLineEdit.setText(str(port))
            self.ui.serverEnableCheckBox.setCheckState(0)

        elif btn is self.ui.unloadBtn:
            row = self.ui.pluginList.currentRow()
            it = str(self.ui.pluginList.currentItem().text())
            logging.debug('[%s]: unload plugin name %s', self.getName(), it)
            self.statusbar.showMessage('Unloading plugin %s' % it)
            PluginManager.getManager().unload(it)
            self.ui.pluginList.takeItem(row)
            conf = ConfManager.getManager().getValue('common', 'plugins')
            for pc in conf:
                if pc['name'] == it:
                    conf.remove(pc)
            ConfManager.getManager().setValue('common', 'plugins', conf)

        elif btn is self.ui.reloadBtn:
            row = self.ui.pluginList.currentRow()
            it = str(self.ui.pluginList.currentItem().text())
            logging.debug('[%s]: reload plugin name %s', self.getName(), it)
            self.statusbar.showMessage('Reloading plugin %s' % it)
            PluginManager.getManager().reload(it)

        elif btn is self.ui.addPluginBtn:
            path = QFileDialog.getOpenFileName(self)
            PluginManager.getManager().loadPluginFromPath(str(path))


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

    def statusupdate(self, param):
        """call back for status update"""
        self.emit(SIGNAL('statusupdate(int)'), param['result'])
        print 'Signal emit'

    def statusbarUpdate(self, res):
        """statusbar update callback"""
        #logging.debug('[%s] statusbarUpdate called', self.getName())
        #self.emit(SIGNAL('statusUpdate'), ERR_STR_TABLE[param['result']])
        print 'Are you here?'
        self.statusbar.showMessage(ERR_STR_TABLE[res])

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
