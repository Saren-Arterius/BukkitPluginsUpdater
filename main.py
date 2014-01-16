#!/usr/bin/python
from bukkit_plugin import *
from error import Error
from Levenshtein import ratio
from multiprocessing import Pool
import datetime
import wx
import webbrowser

plugins = []
class inputDialog(wx.Dialog):
    def __init__(self, *args, **kw):
        wx.Dialog.__init__(self)
        self.InitUI()

    def InitUI(self):
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        sb = wx.StaticBox(pnl, label='Colors')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)        
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)        
        hbox1.Add(wx.RadioButton(pnl, label='Custom'))
        hbox1.Add(wx.TextCtrl(pnl), flag=wx.LEFT, border=5)
        sbs.Add(hbox1)
        pnl.SetSizer(sbs)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)
        self.SetSizer(vbox)
        okButton.Bind(wx.EVT_BUTTON, self.OnClose)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def OnClose(self, e):
        self.Destroy()

class FileDropTarget(wx.FileDropTarget):
    def __init__(self, obj):
        wx.FileDropTarget.__init__(self)
        self.obj = obj

    def OnDropFiles(self, x, y, filenames):
        return self.obj.addPluginFiles(filenames)

class MainDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(1200,500), style=wx.DEFAULT_DIALOG_STYLE)
        self.initUI()
        self.bindEvent()

    def initUI(self):
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.textBox, self.buttonBox, self.controlBox = wx.BoxSizer(wx.VERTICAL), wx.BoxSizer(wx.VERTICAL), wx.BoxSizer(wx.VERTICAL)
        self.pluginsBox, self.versionsBox = wx.BoxSizer(wx.VERTICAL), wx.BoxSizer(wx.VERTICAL)

        self.plugins, self.versions = wx.ListCtrl(self, -1, style=wx.LC_REPORT), wx.ListCtrl(self, -1, style=wx.LC_REPORT)
        
        self.plugins.InsertColumn(0, 'Hash') #Hidden column
        self.plugins.InsertColumn(1, 'Plugin')
        self.plugins.InsertColumn(2, 'Version')
        
        self.plugins.SetColumnWidth(0, 0)
        self.plugins.SetColumnWidth(1, 180)
        self.plugins.SetColumnWidth(2, 90)

        self.versions.InsertColumn(0, 'href') #Hidden column
        self.versions.InsertColumn(1, 'Name')
        self.versions.InsertColumn(2, 'Release type')
        self.versions.InsertColumn(3, 'Status')
        self.versions.InsertColumn(4, 'Date')
        self.versions.InsertColumn(5, 'Game version')
        self.versions.InsertColumn(6, 'Filename')
        self.versions.InsertColumn(7, 'Downloads')
        self.versions.SetColumnWidth(0, 0)
        self.versions.SetColumnWidth(2, 90)
        self.versions.SetColumnWidth(5, 90)
        
        self.controlPanel = wx.Panel(self, -1)
        
        self.textPanel = wx.Panel(self.controlPanel, -1)
        self.text = wx.StaticText(self.textPanel, -1, 'Drag and drop the plugins folder or *.jar here.\nBukkit plugin updater v0.0.1\nAuthor: Saren')
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
        
    def bindEvent(self):
        self.Bind(wx.EVT_BUTTON, self.onClose, id=0)
        self.Bind(wx.EVT_BUTTON, self.onLazy, id=1)
        self.Bind(wx.EVT_BUTTON, self.onDownload, id=2)
        self.plugins.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onPluginSelected, self.plugins)
        self.versions.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onVersionSelected, self.versions)
        self.versions.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onVersionDoubleClick, self.versions)
        
        wx.MessageBox('Download completed', 'Info', wx.OK | wx.ICON_INFORMATION)
        fileInputDialog = inputDialog()
        
    def onClose(self, event):
        self.Close()
        
    def onLazy(self, event):
        return self.changeText("You are lazy, huh?")
        
    def onDownload(self, event):
        return self.changeText("You want to download something, huh?")
        
    def onPluginSelected(self, event):
        self.changeText("Loading...Please wait...")
        self.versions.DeleteAllItems()
        result = self.updateVersionList(event.GetText())
        if isinstance(result, dict):
            if result["sim"] >= 0.8:
                return self.changeText("Plugin info downloaded from BukkitDev! \n(Similarity: {0})".format(round(result["sim"], 2)))
            else:
                return self.warn("Warning: The BukkitDev plugin name\nis kind of different! Use with caution.\n(bukkitDevName: {0})\n(Similarity: {1})".format(result["bukkitDevName"], round(result["sim"], 3)))
        return False
        
    def onVersionDoubleClick(self, event):
        return webbrowser.open(event.GetText())
        
    def onVersionSelected(self, event):
        return self.changeText("Double click to open plugin update log,\nor click download button to \ndownload the plugin and save to disk.")
        
    def changeText(self, text):
        self.text.SetForegroundColour((0,0,0))
        self.text.SetLabel(text)
        return True
        
    def warn(self, text):
        self.text.SetForegroundColour((255,0,0))
        self.text.SetLabel(text)
        return True

    def addPluginFiles(self, filenames):
        for filename in filenames:
            try:
                newPlugin = bukkitPlugin(filename)
                print(newPlugin)
                for plugin in plugins:
                    if newPlugin.hash == plugin.hash:
                        raise Error("{0} already exists in plugin list.".format(newPlugin.name))
                plugins.append(newPlugin)
            except Exception as e:
                self.warn(str(e))
        return self.updatePluginList()
        
    def updatePluginList(self):
        self.plugins.DeleteAllItems()
        for plugin in plugins:
            num_items = self.plugins.GetItemCount()
            self.plugins.InsertItem(num_items, plugin.hash)
            self.plugins.SetItem(num_items, 1, plugin.name)
            self.plugins.SetItem(num_items, 2, plugin.version)
        return True
        
    def updateVersionList(self, hash):
        for plugin in plugins:
            if hash == plugin.hash:
                try:
                    for index, row in enumerate(plugin.getAllVersions()):
                        self.versions.InsertItem(index, row["Name"]["href"])
                        self.versions.SetItem(index, 1, row["Name"]["Name"])
                        self.versions.SetItem(index, 2, row["Release type"])
                        self.versions.SetItem(index, 3, row["Status"])
                        self.versions.SetItem(index, 4, datetime.datetime.fromtimestamp(row["Date"]).strftime('%Y-%m-%d'))
                        try:
                            if len(row["Game version"]) >= 2:
                                self.versions.SetItem(index, 5, "{0} - {1}".format(row["Game version"][-1], row["Game version"][0]))
                            else:
                                self.versions.SetItem(index, 5, "{0}".format(row["Game version"][0]))
                        except:
                            self.versions.SetItem(index, 5, "None")
                        self.versions.SetItem(index, 6, row["Filename"])
                        self.versions.SetItem(index, 7, str(row["Downloads"]))
                    return {"sim": ratio(plugin.name.lower(), plugin.bukkitDevName.lower()), "bukkitDevName": plugin.bukkitDevName}
                except Exception as e:
                    return self.warn(str(e))
        raise Error("WTF?")

class Main(wx.App):
    def OnInit(self):
        dia = MainDialog(None, -1, 'Bukkit plugin updater v0.0.1')
        dia.ShowModal()
        dia.Destroy()
        return True

if __name__ == "__main__":
    app = Main()
    app.MainLoop()