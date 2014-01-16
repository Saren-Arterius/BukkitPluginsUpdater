#!/usr/bin/python
from bukkit_plugin import *
from error import Error
from Levenshtein import ratio
from time import time
from textwrap import fill
import os
import datetime
import wx
import webbrowser

plugins = []

class textEntryDialog(wx.TextEntryDialog):
    def __init__(self, obj):
        wx.Dialog.__init__(self)
        self.obj = obj
        self.Create(obj, "Input correct BukkitDev plugin name here, or leave it blank to get the name automatically.")
        
    def getInput(self):
        if self.ShowModal() == wx.ID_OK:
            self.Destroy()
            return [True, self.GetValue()]
        else:
            self.Destroy()
            return False

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
        
        self.controlPanel.Bind(wx.EVT_LEFT_DCLICK, self.onControlPanelDoubleClick, self.controlPanel)
        self.buttonPanel.Bind(wx.EVT_LEFT_DCLICK, self.onControlPanelDoubleClick, self.buttonPanel)
        
        self.textPanel.Bind(wx.EVT_LEFT_DCLICK, self.onTextPanelDoubleClick, self.textPanel)
        self.text.Bind(wx.EVT_LEFT_DCLICK, self.onTextPanelDoubleClick, self.text)
        
        self.plugins.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onPluginSelected, self.plugins)
        self.versions.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onVersionSelected, self.versions)
        self.versions.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onVersionDoubleClick, self.versions)
        self.Bind(wx.EVT_CHAR_HOOK, self.onDeleteKey)

    def changeText(self, text):
        self.text.SetForegroundColour((0,0,0))
        self.text.SetLabel(fill(text, 40))
        return True
        
    def warn(self, text):
        self.text.SetForegroundColour((255,0,0))
        self.text.SetLabel(fill(text, 40))
        return True

    def addPluginFiles(self, filenames):
        pluginsAdded = 0
        for filename in filenames:
            if os.path.isdir(filename):
                for fileInDir in os.listdir(filename):
                    fileInDir = filename + "\\" + fileInDir
                    try:
                        newPlugin = bukkitPlugin(fileInDir)
                        print(newPlugin)
                        for plugin in plugins:
                            if newPlugin.hash == plugin.hash:
                                raise Error("{0} already exists in plugin list.".format(newPlugin.name))
                        plugins.append(newPlugin)
                        pluginsAdded += 1
                    except Exception as e:
                        self.warn(str(e))
            else:
                try:
                    newPlugin = bukkitPlugin(filename)
                    print(newPlugin)
                    for plugin in plugins:
                        if newPlugin.hash == plugin.hash:
                            raise Error("{0} already exists in plugin list.".format(newPlugin.name))
                    plugins.append(newPlugin)
                    pluginsAdded += 1
                except Exception as e:
                    self.warn(str(e))
        self.changeText("{0} plugins added!".format(pluginsAdded))
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
        
    def updateRow(self, bukkitDevName, hash):
        for plugin in plugins:
            if hash == plugin.hash:
                if plugin.database.updateRow(plugin.packageName, bukkitDevName):
                    return self.reload(plugin)
                
    def deleteRow(self, hash):
        for plugin in plugins:
            if hash == plugin.hash:
                if plugin.database.deleteRow(plugin.packageName):
                    return self.reload(plugin)
                
    def getBukkitDevName(self, hash):
        for plugin in plugins:
            if hash == plugin.hash:
                return plugin.bukkitDevName
                
    def reload(self, plugin):
        path = plugin.path
        plugins.remove(plugin)
        return self.addPluginFiles([path])

    def onClose(self, event):
        self.Close()
        
    def onLazy(self, event):
        itemsCount = self.plugins.GetItemCount()
        if itemsCount > 0:
            answer = wx.MessageBox("Are you feeling lazy today?", "Let me ask you a question:", wx.YES_NO)
            if answer == wx.YES:
                process = wx.ProgressDialog("The whole world is getting even more lazier...", "Initializing...", maximum=itemsCount*1000, parent=None, 
                    style=wx.PD_AUTO_HIDE|wx.PD_APP_MODAL|wx.PD_SMOOTH|wx.PD_CAN_ABORT|wx.PD_REMAINING_TIME|wx.PD_ELAPSED_TIME|wx.PD_ESTIMATED_TIME)
                newVal = 0
                for i in range(itemsCount):
                    if not process.Update(newVal, "Getting versions info of {0}...".format(self.plugins.GetItemText(i, 1))):
                        process = ""
                        return self.changeText("You stopped being lazy.")
                    self.plugins.Select(i)
                    self.plugins.Focus(i)
                    newVal += 250
                    if not process.Update(newVal):
                        process = ""
                        return self.changeText("You stopped being lazy.")
                    self.versions.Select(0)
                    self.versions.Focus(0)
                    newVal += 250
                    if not process.Update(newVal, "Downloading latest version of {0}...".format(self.plugins.GetItemText(i, 1))):
                        process = ""
                        return self.changeText("You stopped being lazy.")
                    self.onDownload(None)
                    newVal += 500
                process = ""
                wx.MessageBox('All plugins are all downloaded.', 'Info', wx.OK | wx.ICON_INFORMATION)
                return self.changeText("You are lazy today, huh?")
            else:
                return self.changeText("Oh, you are not feeling lazy today?")
        else:
            return self.changeText("You don't have any work to do so you can't be lazy!")

    def onDownload(self, event):
        whichPlugin = self.plugins.GetFocusedItem()
        whichVersion = self.versions.GetFocusedItem()
        if whichPlugin != -1 and whichVersion != -1:
            try:
                hash = self.plugins.GetItemText(whichPlugin)
                for plugin in plugins:
                    if hash == plugin.hash:
                        return self.saveToDisk(plugin, plugin.getVersionUrl(whichVersion), whichVersion)
                raise Error("WTF?")
            except Exception as e:
                return self.warn(str(e))
        else:
            return self.changeText("You want to download something, huh?")
            
    def saveToDisk(self, plugin, downUrl, whichVersion):
        try:
            cmpUrl = plugin.versions[whichVersion]["Name"]["href"]

            self.changeText("Start downloading plugin...")
            saveDir = plugin.origin + "\\__plugindownloads__\\" + datetime.datetime.fromtimestamp(time()).strftime('%Y-%m-%d')
            saveFileName = plugin.versions[whichVersion]["Filename"]
            savePath = saveDir + "\\" + saveFileName
            
            if plugin.areHashesMatch(plugin.fileHash, cmpUrl):
                raise Error("You already own that file in plugins folder: {0}".format(plugin.path))
            elif os.path.exists(savePath):
                existingPlugin = bukkitPlugin(savePath)
                if existingPlugin.areHashesMatch(existingPlugin.fileHash, cmpUrl):
                    raise Error("You already own that file in downloads folder: {0}".format(savePath))
            elif not os.path.exists(saveDir):
                print("Making directory: {0}".format(saveDir))
                os.makedirs(saveDir)
                    
            urllib.request.urlretrieve(downUrl, savePath)
            
            downloadedPlugin = bukkitPlugin(savePath)
            if downloadedPlugin.areHashesMatch(downloadedPlugin.fileHash, cmpUrl):
                return self.changeText("Download success! File is saved at: {0}".format(savePath))
            else:
                raise Error("Downloaded file does not match hash!")
        except Exception as e:
            return self.warn(str(e))
        
    def onPluginSelected(self, event):
        self.changeText("Loading...Please wait...")
        self.versions.DeleteAllItems()
        result = self.updateVersionList(event.GetText())
        if isinstance(result, dict):
            if result["sim"] >= 0.8:
                return self.changeText("Plugin info downloaded from BukkitDev! (Similarity: {0})".format(round(result["sim"], 3)))
            else:
                return self.warn("Warning: The BukkitDev plugin name is kind of different! Use with caution. (bukkitDevName: {0}) (Similarity: {1})".format(result["bukkitDevName"], round(result["sim"], 3)))
        return False
        
    def onVersionDoubleClick(self, event):
        return webbrowser.open(event.GetText())
        
    def onVersionSelected(self, event):
        return self.changeText("Double click to open plugin update log, or click download button to download the plugin and save to disk.")
        
    def onControlPanelDoubleClick(self, event): #Add files/folders
        openFileDialog = wx.FileDialog(self, "Open Jar files", "", "", "Jar files (*.jar)|*.jar", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE)
        if openFileDialog.ShowModal() == wx.ID_OK:
            return self.addPluginFiles(openFileDialog.GetPaths())
        else:
            return False
        
    def onTextPanelDoubleClick(self, event): 
        focus = self.plugins.GetFocusedItem()
        if plugins and focus != -1:
            hash = self.plugins.GetItemText(focus)
            textEntry = textEntryDialog(self)
            oldName = self.getBukkitDevName(hash)
            textEntry.SetValue(oldName)
            result = textEntry.getInput() #[True, "abccba"], [True, ""], False
            if not result or result[1] == oldName:
                return self.changeText("Plugin's BukkitDev name is not changed.")
            elif result[1] == "":
                if self.deleteRow(hash):
                    return self.warn("I will ask Google again for it's BukkitDev name.")
            else:
                if self.updateRow(result[1], hash):
                    return self.changeText("Successfully changed plugin's BukkitDev name!")
        else:
            return self.onControlPanelDoubleClick(event)
            
    def onDeleteKey(self, event):
        key = event.GetKeyCode()
        if key == 127 or key == 385: # Delete key
            plugins.clear()
            self.changeText("Plugins list cleared!")
            return self.updatePluginList()
        else:
            return False
            
class Main(wx.App):
    def OnInit(self):
        dia = MainDialog(None, -1, 'Bukkit plugin updater v0.0.1')
        dia.ShowModal()
        dia.Destroy()
        return True

if __name__ == "__main__":
    db = os.path.dirname(os.path.realpath(__file__)) + "\\" + "database.db"
    if not os.path.exists(db): #Analytic
        url = "https://minecraft.wtako.coms.hk/analytic/{0}/".format("0.0.1") #Version
        req = urllib.request.urlopen(url, timeout=1)
    app = Main()
    app.MainLoop()