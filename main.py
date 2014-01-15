#!/usr/bin/python
from bukkit_plugin import *
from time import sleep
from error import Error
import wx

plugins = []

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, obj):
        wx.FileDropTarget.__init__(self)
        self.obj = obj

    def OnDropFiles(self, x, y, filenames):
        print(filenames)
        for filename in filenames:
            try:
                newPlugin = bukkitPlugin(filename)
                print(newPlugin)
                for plugin in plugins:
                    if newPlugin.hash == plugin.hash:
                        raise Error("{0} already exists in plugin list.".format(newPlugin.name))
                plugins.append(newPlugin)
            except Exception as e:
                self.obj.changeText(str(e))
        return self.updatePluginList()
        
    def updatePluginList(self):
        self.obj.plugins.DeleteAllItems()
        for plugin in plugins:
            num_items = self.obj.plugins.GetItemCount()
            self.obj.plugins.InsertItem(num_items, plugin.name)
            self.obj.plugins.SetItem(num_items, 1, plugin.version)
            self.obj.plugins.SetItem(num_items, 2, plugin.hash)
        return True

class MainDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(1200,500), style=wx.DEFAULT_DIALOG_STYLE)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.textBox, self.buttonBox, self.controlBox = wx.BoxSizer(wx.VERTICAL), wx.BoxSizer(wx.VERTICAL), wx.BoxSizer(wx.VERTICAL)
        self.pluginsBox, self.versionsBox = wx.BoxSizer(wx.VERTICAL), wx.BoxSizer(wx.VERTICAL)

        self.plugins, self.versions = wx.ListCtrl(self, -1, style=wx.LC_REPORT), wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        
        self.plugins.InsertColumn(0, 'Plugin')
        self.plugins.InsertColumn(1, 'Version')
        self.plugins.InsertColumn(2, 'Hash') #Hidden column
        self.plugins.SetColumnWidth(0, 200)
        self.plugins.SetColumnWidth(1, 90)
        self.plugins.SetColumnWidth(2, 0)

        self.versions.InsertColumn(0, 'Name')
        self.versions.InsertColumn(1, 'Release type')
        self.versions.InsertColumn(2, 'Status')
        self.versions.InsertColumn(3, 'Date')
        self.versions.InsertColumn(4, 'Game version')
        self.versions.InsertColumn(5, 'Filename')
        self.versions.InsertColumn(6, 'Downloads')
        self.versions.SetColumnWidth(1, 90)
        self.versions.SetColumnWidth(4, 90)
        
        self.controlPanel = wx.Panel(self, -1)
        
        self.textPanel = wx.Panel(self.controlPanel, -1)
        self.text = wx.StaticText(self.textPanel, -1, 'Drag and drop the plugins folder or *.jar here.')
        self.textBox.Add(self.text, 0, wx.EXPAND, 5)
        self.textPanel.SetSizer(self.textBox)
        
        self.buttonPanel = wx.Panel(self.controlPanel, -1)
        self.buttonBox.Add(wx.Button(self.buttonPanel, 2, 'Download'), 0, wx.ALIGN_CENTER | wx.TOP)
        self.buttonBox.Add(wx.Button(self.buttonPanel, 1, 'Lazy'), 0, wx.ALIGN_CENTER | wx.TOP, 20)
        self.buttonBox.Add(wx.Button(self.buttonPanel, 0, 'Close'), 0, wx.ALIGN_CENTER | wx.TOP, 20)
        self.buttonPanel.SetSizer(self.buttonBox)

        self.controlBox.Add(self.textPanel, 1, wx.ALIGN_CENTER | wx.TOP, 150)
        self.controlBox.Add(self.buttonPanel, 1, wx.ALIGN_CENTER | wx.TOP, 80)
        self.controlPanel.SetSizer(self.controlBox)
        self.controlPanel.SetDropTarget(FileDropTarget(self))
        
        self.pluginsBox.Add(self.plugins, 1, wx.EXPAND | wx.ALL, 3)
        self.versionsBox.Add(self.versions, 1, wx.EXPAND | wx.ALL, 3)

        self.hbox.Add(self.pluginsBox, 0, wx.EXPAND)
        self.hbox.Add(self.controlPanel, 1, wx.EXPAND)
        self.hbox.Add(self.versionsBox, 2, wx.EXPAND)
        
        self.SetSizer(self.hbox)
        
        self.Bind(wx.EVT_BUTTON, self.onClose, id=0)
        self.Bind(wx.EVT_BUTTON, self.onLazy, id=1)
        self.Bind(wx.EVT_BUTTON, self.onDownload, id=2)
        
    def onClose(self, event):
        self.Close()
        
    def onLazy(self, event):
        return self.changeText("You are lazy, huh?")
        
    def onDownload(self, event):
        return self.changeText("You want to download something, huh?")
        
    def changeText(self, text):
        self.text.SetLabel(text)
        return True

class Main(wx.App):
    def OnInit(self):
        dia = MainDialog(None, -1, 'Bukkit plugin updater')
        dia.ShowModal()
        dia.Destroy()
        return True

app = Main()
app.MainLoop()