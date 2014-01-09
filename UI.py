import wx

TRAY_TOOLTIP = 'File Sync for Baidu Cloud'
TRAY_ICON = 'icon.png'

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item


class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self):
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Configure File Sync', self.on_config)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        print 'Tray icon was left-clicked.'

    def on_config(self, event):
        print 'Hello, world!'
        frame = wx.Frame(parent=None, title='File Sync for Baidu Cloud')
        frame.Show()

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)


class FileSyncUI(wx.App):
    """File Sync UI"""
    def __init__(self, arg=None):
        super(FileSyncUI, self).__init__()
        self.arg = arg

    def OnInit(self):
        """File Sync UI init"""
        TaskBarIcon()
        return True

def wx_main():
    app = FileSyncUI()
    frame = wx.Frame(parent=None, title='Test')
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    wx_main()
