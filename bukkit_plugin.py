#!/usr/bin/python3.3
from sys import argv
from zipfile import ZipFile, is_zipfile
from re import findall, sub
from pyquery import PyQuery as pq
from error import Error
from hashlib import sha256
from os.path import dirname
import urllib.request

class bukkitPlugin(ZipFile):
    def __init__(self, path):
        zip = ZipFile(path)
        with zip.open("plugin.yml") as pluginInfo:
            yaml = pluginInfo.read().decode()
            self.origin = dirname(path)
            self.name = sub("\r|\n", "", findall("name: (.*)", yaml)[0])
            self.version = sub("\r|\n", "", findall("version: (.*)", yaml)[0])
            try:
                self.author = sub("\r|\n", "", findall("author: (.*)", yaml)[0])
            except:
                self.author = ""
            self.hash = sha256(bytes("{0}{1}{2}{3}".format(self.origin, self.name, self.version, yaml), "utf-8")).hexdigest()
        
    def __str__(self):
        return "Craftbukkit plugin: {0} {1}\nFile origin: {2}\nHash: {3}\n".format(self.name, self.version, self.origin, self.hash)

    def __getGoogleResult(self):
        try:
            url = "http://www.google.com.hk/search?q=\"{0}\"+\"{1}\"+files+site%3Adev.bukkit.org%2Fbukkit-plugins".format(sub(" ", "+", self.name), sub(" ", "+", self.author))
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            resp = opener.open(url)
            return resp.read().decode()
        except:
            raise Error("Failed to use google!")
        
    def __getFilesPage(self):
        try:
            self.googleResult
        except:
            self.googleResult = self.__getGoogleResult()
        finally:
            for elem in pq(self.googleResult)(".kv").find("cite"):
                bukkitDevName = findall("dev.bukkit.org/bukkit-plugins/(.+)/.+", sub("<[^>]*>", "", pq(elem).html()))
                if bukkitDevName:
                    url = "http://dev.bukkit.org/bukkit-plugins/{0}/files/".format(bukkitDevName[0])
                    print(bukkitDevName)
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                    resp = opener.open(url)
                    return resp.read().decode()
            raise Error("Failed to get bukkit files page, \nor plugin is not available on bukkitdev.")
        
    def getAllVersions(self):
        try:
            return self.versions
        except:
            self.filesPage = self.__getFilesPage()
            table = []
            for index, column in enumerate(pq(self.filesPage)("tbody").find("tr")):
                table.append({})
                for cell in pq(column).find("td"):
                    if pq(cell).attr("class") == "col-file":
                        table[index]["Name"] = {"Name": pq(cell)("a").html(), "href": "http://dev.bukkit.org" + pq(cell)("a").attr("href")}
                    elif pq(cell).attr("class") == "col-type":
                        table[index]["Release type"] = pq(cell)("span").html()
                    elif pq(cell).attr("class") == "col-status":
                        table[index]["Status"] = pq(cell)("span").html()
                    elif pq(cell).attr("class") == "col-date":
                        table[index]["Date"] = int(pq(cell)("span").attr("data-epoch"))
                    elif pq(cell).attr("class") == "col-game-version":
                        try:
                            table[index]["Game version"] = [findall("(\d\.\d\.\d)", pq(li).html())[0] for li in pq(cell).find("li")]
                        except:
                            table[index]["Game version"] = [pq(li).html() for li in pq(cell).find("li")]
                    elif pq(cell).attr("class") == "col-filename":
                        table[index]["Filename"] = sub(" +|\r|\n", "", pq(cell).html())
                    elif pq(cell).attr("class") == "col-downloads":
                        table[index]["Downloads"] = int(pq(cell)("span").attr("data-value"))
            self.versions = table
            return self.versions
        
    def getVersionUrl(self, index):
        try:
            downloadPageUrl = self.versions[index]["Name"]["href"]
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            resp = opener.open(downloadPageUrl)
            downloadPage = resp.read().decode()
            return pq(downloadPage)(".user-action-download").find("a").attr("href")
        except KeyError:
            raise Error("Bukkit page is broken?")
        except:
            raise Error("Failed to get plugin download link!")

if __name__ == "__main__": #Test
    plugin = bukkitPlugin(argv[1])
    print(plugin.getVersionUrl(0))