from sys import argv
from zipfile import ZipFile, is_zipfile
from re import findall, sub
from pyquery import PyQuery as pq
import urllib.request

class bukkitPlugin(ZipFile):
    def __init__(self, path):
        self.zip = ZipFile(path)
        with self.zip.open("plugin.yml") as pluginInfo:
            self.yaml = pluginInfo.read().decode()
        self.version = findall("version: (.*)\r", self.yaml)
        self.name = findall("name: (.*)\r", self.yaml)
    
    def getGoogleResult(self):
        url = "http://www.google.com.hk/search?q={0}+files+site%3Adev.bukkit.org%2Fbukkit-plugins".format(self.name)
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        resp = opener.open(url)
        return resp.read().decode()
        
    def getFilesPage(self):
        self.googleResult = self.getGoogleResult()
        print(pq(self.googleResult)(".kv").find("cite"))

plugin = bukkitPlugin(argv[1])
plugin.getFilesPage()