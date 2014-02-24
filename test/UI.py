#!/usr/bin/env python
#-*- coding: utf-8 -*-
import wx
import threading

from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.MsgBus import *

TRAY_TOOLTIP = u'Uni File Sync'
TRAY_ICON = 'icon.png'
FILESYNC_CONF_TITLE = u'Unit File Sync Configuration'


class FolderPanel(wx.Panel):
    """docstring for FolderPanel"""
    def __init__(self, parent):
        super(FolderPanel, self).__init__(parent)

class NetConfPanel(wx.Panel):
    """docstring for NetConfPanel"""
    def __init__(self, parent):
        super(NetConfPanel, self).__init__(parent)

class ExplorePanel(wx.Panel):
    """docstring for ExplorePanel"""
    def __init__(self, parent):
        super(ExplorePanel, self).__init__(parent)

class MainTabPanel(wx.Notebook):
    """main tab panel"""
    def __init__(self, parent):
        super(MainTabPanel, self).__init__(parent)
        self.parent = parent
        self.folderPanel = FolderPanel(self)
        self.AddPage(self.folderPanel, u'Folders')
        self.netConfPanel = NetConfPanel(self)
        self.AddPage(self.netConfPanel, u'Net Configuration')
        self.explorePanel = ExplorePanel(self)
        self.AddPage(self.explorePanel, u'Explore')


class ConfFrame(wx.Frame):
    def __init__(self, parent=None):
        w = 800
        h = 600
        ScreenWidth, ScreenHeight = wx.GetDisplaySize()
        x = (ScreenWidth - w) / 2
        y = (ScreenHeight - h) / 2
        FrameStyle = wx.DEFAULT_FRAME_STYLE
        FrameStyle &= ~wx.RESIZE_BORDER
        wx.Frame.__init__(self, parent, size=(w, h), pos=(x, y), title=FILESYNC_CONF_TITLE, style=FrameStyle)
        self.MainPanel = MainTabPanel(self)

#==================================================================

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
        create_menu_item(menu, u'Configure File Sync', self.on_config)
        menu.AppendSeparator()
        create_menu_item(menu, u'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        print 'Tray icon was left-clicked.'

    def on_config(self, event):
        self.confFrame = ConfFrame(parent=None)
        self.confFrame.Show(True)

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)


class UniFileSyncUI(wx.App):
    """File Sync UI"""
    def __init__(self, arg=None):
        super(UniFileSyncUI, self).__init__()
        self.arg = arg

    def OnInit(self):
        """File Sync UI init"""
        TaskBarIcon()
        return True

class UniFileSyncUIThread(threading.Thread):
    """UniFileSync UI thread"""
    def __init__(self, name):
        super(UniFileSyncUIThread, self).__init__()
        if not name:
            self.setName(name)

    def run(self):
        """thread entry"""
        self.app = UniFileSyncUI()
        self.app.MainLoop()

    def stop(self):
        """stop GUI thread"""
        self.app.ExitMainLoop()
        wx.WakeUpMainThread()

if __name__ == '__main__':
    u = UniFileSyncUIThread('UniFileSyncUI thread Test')
    u.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info('[UniFileSyncUIThread Test]: User press Ctrl+C')
        u.stop()
