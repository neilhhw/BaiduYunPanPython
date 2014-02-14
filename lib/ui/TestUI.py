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

ft = confManager.getValue('UniFileSync', 'folders')

ui.nameLabel.setText(confManager.getValue('UniFileSync', 'user'))

#print ft

flistItem = QListWidgetItem(QIcon('icon/folder.png'), ft, ui.folderList)
ui.folderList.insertItem(1, flistItem)

statusBar = QStatusBar(d)
statusBar.showMessage('I am OK!')
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


fileDialog = QFileDialog(d)
fileDialog.setWindowTitle('Select Folder')

def select():
    """select folder"""
    fileDialog.getExistingDirectory()
    if fileDialog.exec_() == QDialog.Accepted:
        folderPath = fileDialog.selectedFiles()[0]
        print folderPath


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
