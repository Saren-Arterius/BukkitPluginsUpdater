#!/usr/bin/python

# capitals.py

import wx

class MyDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(700,500), style=wx.DEFAULT_DIALOG_STYLE)

        hbox  = wx.BoxSizer(wx.HORIZONTAL)

        pluginsBox = wx.BoxSizer(wx.VERTICAL)
        versionsBox = wx.BoxSizer(wx.VERTICAL)
        
        self.plugins = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.plugins.InsertColumn(0, 'Plugin')
        self.plugins.InsertColumn(1, 'Version')
        self.plugins.SetColumnWidth(0, 140)
        self.plugins.SetColumnWidth(1, 153)
        
        self.versions = wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        self.versions.InsertColumn(0, 'Version')
        self.versions.InsertColumn(1, 'Game version')
        self.versions.SetColumnWidth(0, 140)
        self.versions.SetColumnWidth(1, 153)
        
        pluginsBox.Add(self.plugins, 1, wx.EXPAND | wx.ALL, 3)
        versionsBox.Add(self.versions, 1, wx.EXPAND | wx.ALL, 3)
        
        hbox.Add(pluginsBox, 1, wx.EXPAND)
        hbox.Add(versionsBox, 1, wx.EXPAND)
        
        self.SetSizer(hbox)

class Main(wx.App):
    def OnInit(self):
        dia = MyDialog(None, -1, 'Bukkit plugin updater')
        dia.ShowModal()
        dia.Destroy()
        return True

app = Main()
app.MainLoop()