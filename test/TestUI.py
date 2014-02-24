import sys
import socket
import json

from UniFileSync.lib.common.ConfManager import ConfManager

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
        QFileDialog)
from PyQt4.QtCore import QString, SIGNAL, SLOT

from UniFileSyncPop import Ui_UniFileSyncPop


try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)

m = QWidget()
d = QMainWindow(m)

t = QSystemTrayIcon(m)
t.setIcon(QIcon('icon/tray.png'))

ui = Ui_UniFileSyncPop()
ui.setupUi(d)

d.setFixedSize(d.size())


req = {'type': 'request'}

confManager = ConfManager.getManager()

fts = confManager.getValue('common', 'folders')

ui.nameLabel.setText(confManager.getValue('UI', 'username'))

i = 0
for ft in fts:
    flistItem = QListWidgetItem(QIcon('icon/folder.png'), ft, ui.folderList)
    ui.folderList.insertItem(i, flistItem)
    i += 1

statusBar = QStatusBar(d)
#print confManager.getValue('UI', 'window')
statusBar.showMessage(confManager.getValue('UI', 'statusbar')['messages']['init'])
d.setStatusBar(statusBar)

def connect(btn):
    """connect to UniFileSync Server"""
    req['param'] = {'name': 'all'}

    print btn.text()

    if btn.text() == 'Connect':
        req['action'] = 'start'
    else:
        req['action'] = 'stop'

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 8089))

        d = json.dumps(req)
        sock.send(d)
        buf = sock.recv(1024)
        r = json.loads(buf)
        if r['res'] == 0:
            if req['action'] == 'start':
                btn.setText('Disconect')
            else:
                btn.setText('Connect')
        sock.close()
    except socket.error, e:
        print '%s' % e

def select():
    """select folder"""
    fileDialog = QFileDialog(d)
    fileDialog.setWindowTitle('Select Folder')
    folderPath = fileDialog.getExistingDirectory()
    #print folderPath
    fts.append('%s' % folderPath)
    confManager.setValue('common', 'folders', fts)
    confManager.save()


ui.connBtn.connect(ui.connBtn, SIGNAL('clicked()'), lambda: connect(ui.connBtn))
ui.addFolderBtn.clicked.connect(select)

menu = QMenu(m)
es = menu.addAction('ShowConfig')
menu.connect(es, SIGNAL('triggered()'), d, SLOT('show()'))

menu.addSeparator()

ea = menu.addAction("&Exit")
menu.connect(ea, SIGNAL('triggered()'), app, SLOT('quit()'))

t.setContextMenu(menu)

t.show()
t.showMessage('UniFileSyncPop Message', 'This is UniFileSyncUI!!')

sys.exit(app.exec_())
