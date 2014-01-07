import wx


class ConfFrame( wx.Frame ):
	def __init__( self, parent ):
		wx.Frame.__init__( self, parent, id = wx.ID_ANY, title = u"FileSync UI Configuration",
                           pos = wx.DefaultPosition, size = wx.Size(600, 480),
                           style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.ConfTabPanel = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.FolderPanel = wx.Panel( self.ConfTabPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer5 = wx.BoxSizer( wx.VERTICAL )

		self.m_listbook2 = wx.Listbook( self.FolderPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LB_DEFAULT )

		bSizer5.Add( self.m_listbook2, 1, wx.EXPAND |wx.ALL, 5 )


		self.FolderPanel.SetSizer( bSizer5 )
		self.FolderPanel.Layout()
		bSizer5.Fit( self.FolderPanel )
		self.ConfTabPanel.AddPage( self.FolderPanel, u"Folders", True )
		self.m_panel10 = wx.Panel( self.ConfTabPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.ConfTabPanel.AddPage( self.m_panel10, u"a page", False )
		self.m_panel11 = wx.Panel( self.ConfTabPanel, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.ConfTabPanel.AddPage( self.m_panel11, u"a page", False )

		bSizer1.Add( self.ConfTabPanel, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass

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
        self.confFrame = ConfFrame(parent=None)

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
        print 'Open configuration Form'
        self.confFrame.Show(True)

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
    app.MainLoop()

if __name__ == '__main__':
    wx_main()
