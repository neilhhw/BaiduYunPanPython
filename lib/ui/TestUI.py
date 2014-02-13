import sys
from PyQt4.QtGui import QApplication, QWidget, QSystemTrayIcon, QIcon, QMenu, QAction, QDialog, QLayout
from PyQt4.QtCore import QString, SIGNAL, SLOT
from UniFileSyncPop import Ui_UniFileSyncPop

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


app = QApplication(sys.argv)

m = QWidget()
d = QDialog(m)

t = QSystemTrayIcon(m)
t.setIcon(QIcon('icon.png'))
t.showMessage(_fromUtf8('UniFileSyncPop Message'), _fromUtf8('This is UniFileSyncUI!!'))

ui = Ui_UniFileSyncPop()
ui.setupUi(d)

def func():
    """docstring for func"""
    print 'I am OK'

ui.connBtn.connect(ui.connBtn, SIGNAL('clicked()'), func)

d.setFixedSize(d.size())

menu = QMenu(m)
es = menu.addAction(_fromUtf8('ShowConfig'))
menu.connect(es, SIGNAL('triggered()'), d, SLOT('show()'))

ea = menu.addAction(_fromUtf8('Exit'))
menu.connect(ea, SIGNAL('triggered()'), app, SLOT('quit()'))

t.setContextMenu(menu)

t.show()

app.setQuitOnLastWindowClosed(False)

sys.exit(app.exec_())
