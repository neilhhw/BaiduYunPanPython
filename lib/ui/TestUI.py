import sys
from PyQt4.QtGui import QApplication, QWidget, QSystemTrayIcon, QIcon, QMenu, QAction, QFrame
from PyQt4.QtCore import QString, SIGNAL, SLOT
from UniFileSyncPop import Ui_Form

try:
    _fromUtf8 = QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s



app = QApplication(sys.argv)

m = QWidget()

ui = Ui_Form()

ui.setupUi(m)

t = QSystemTrayIcon(m)
t.setIcon(QIcon('icon.png'))
t.showMessage(_fromUtf8('UniFileSyncPop Message'), _fromUtf8('This is UniFileSyncUI!!'))

menu = QMenu(m)
es = menu.addAction(_fromUtf8('ShowConfig'))
menu.connect(es, SIGNAL('triggered()'), m, SLOT('show()'))

ea = menu.addAction(_fromUtf8('Exit'))
menu.connect(ea, SIGNAL('triggered()'), app, SLOT('quit()'))

t.setContextMenu(menu)

t.show()

sys.exit(app.exec_())
