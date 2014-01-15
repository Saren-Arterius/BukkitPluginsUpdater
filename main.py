#!/usr/bin/python

# capitals.py

import wx

class MyDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(1200,500), style=wx.DEFAULT_DIALOG_STYLE)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        buttonBox, controlBox, pluginsBox, versionsBox = wx.BoxSizer(wx.VERTICAL), wx.BoxSizer(wx.VERTICAL), wx.BoxSizer(wx.VERTICAL), wx.BoxSizer(wx.VERTICAL)

        self.plugins, self.versions = wx.ListCtrl(self, -1, style=wx.LC_REPORT), wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        
        self.plugins.InsertColumn(0, 'Plugin')
        self.plugins.InsertColumn(1, 'Version')
        self.plugins.SetColumnWidth(0, 200)
        self.plugins.SetColumnWidth(1, 90)

        self.versions.InsertColumn(0, 'Name')
        self.versions.InsertColumn(1, 'Release type')
        self.versions.InsertColumn(2, 'Status')
        self.versions.InsertColumn(3, 'Date')
        self.versions.InsertColumn(4, 'Game version')
        self.versions.InsertColumn(5, 'Filename')
        self.versions.InsertColumn(6, 'Downloads')
        self.versions.SetColumnWidth(1, 90)
        self.versions.SetColumnWidth(4, 90)
        
        controlPanel = wx.Panel(self, -1, style=wx.SIMPLE_BORDER)
        buttonPanel = wx.Panel(controlPanel, -1, style=wx.SIMPLE_BORDER)
        
        buttonBox.Add(wx.Button(buttonPanel, 13, 'Lazy'), 0, wx.ALIGN_CENTER | wx.TOP, 50)
        buttonBox.Add(wx.Button(buttonPanel, 14, 'Close'), 0, wx.ALIGN_CENTER | wx.TOP, 20)
        buttonPanel.SetSizer(buttonBox)
        
        controlBox.Add(buttonPanel, 1, wx.ALIGN_CENTER | wx.TOP, 100)
        controlPanel.SetSizer(controlBox)
        
        pluginsBox.Add(self.plugins, 1, wx.EXPAND | wx.ALL, 3)
        versionsBox.Add(self.versions, 1, wx.EXPAND | wx.ALL, 3)

        hbox.Add(pluginsBox, 1, wx.EXPAND)
        hbox.Add(controlPanel, 1, wx.EXPAND)
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