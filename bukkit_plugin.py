#!/usr/bin/python3.3
from database import *
from sys import argv
from zipfile import ZipFile, is_zipfile
from re import findall, sub, split
from pyquery import PyQuery as pq
from error import Error
from hashlib import md5
from os.path import dirname, realpath
import http.cookiejar
import webbrowser
import urllib.request

class bukkitPlugin(ZipFile):
    def __init__(self, path):
        zip = ZipFile(path)
        with zip.open("plugin.yml") as pluginInfo:
            yaml = pluginInfo.read().decode()
            self.path = path
            self.origin = dirname(path)
            self.name = sub("\r|\n", "", findall("name: (.*)", yaml)[0])
            self.version = sub("\r|\n", "", findall("version: (.*)", yaml)[0])
            self.packageName = sub("\r|\n", "", findall("main: (.*)", yaml)[0])
            self.hash = md5(bytes("{0}{1}".format(self.origin, yaml), "utf-8")).hexdigest()
            self.fileHash = self.__getMD5()
            self.database = database()
        
    def __str__(self):
        return "Craftbukkit plugin: {0} {1}\nFile origin: {2}\nPackage name: {3}\nIdent hash: {4}\nFile hash: {5}\n".format(self.name, self.version, self.origin, self.packageName, self.hash, self.fileHash)
        
    def __getMD5(self):
        with open(self.path, "rb") as file:
            hash = md5()
            while True:
                piece = file.read(1024)
                if piece:
                    hash.update(piece)
                else:
                    return hash.hexdigest()
    
    def __getGoogleResult(self):
        try:
            url = "http://www.google.com.hk/search?q=\"{0}\"+files+site%3Adev.bukkit.org%2Fbukkit-plugins".format(sub(" ", "+", self.name))
            cookieFile = dirname(realpath(__file__)) + "\\" + "cookie.txt"
            cj = http.cookiejar.LWPCookieJar(cookieFile)
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            resp = opener.open(url)
            return resp.read().decode()
        except Exception as e:
            try:
                print("Failed to use google!\nProbably you used too much!\n{0}\nAttemping human captcha...".format(str(e)))
                errorPage = e.read().decode()
                imageUrl = "https://ipv4.google.com/sorry/" + pq(errorPage)("img").attr("src")
                id = pq(errorPage)("input[name='id']")
                gContinue = url
                webbrowser.open(imageUrl)
                captcha = input("Please type captcha here: ")
                payload = [urllib.parse.quote_plus(url), urllib.parse.quote_plus(id), urllib.parse.quote_plus(captcha), urllib.parse.quote_plus("Submit")]
                sorryReqUrl = "https://ipv4.google.com/sorry/CaptchaRedirect?continue={0}&id={1}&captcha={2}&submit={3}".format(payload)
                resp = opener.open(sorryReqUrl)
                return resp.read().decode()
            except Exception as e:
                raise Error("Failed to use google! Probably you used too much!\n{0}".format(str(e)))

    def __getBukkitDevName(self):
        bukkitDevName = self.database.selectRow(self.packageName)
        if bukkitDevName:
            print("{0}: bukkitDevName found!".format(self.name))
            return bukkitDevName
        else:
            print("{0}: bukkitDevName not found, using Google.".format(self.name))
            try:
                self.googleResult
                print("Using cache.")
            except:
                self.googleResult = self.__getGoogleResult()
            for elem in pq(self.googleResult)(".r").find("a"):
                bukkitDevName = findall("dev.bukkit.org/bukkit-plugins/(.+)/", pq(elem).attr("href"))
                bukkitDevName = str(split("/", bukkitDevName[0])[0])
                if bukkitDevName:
                    self.database.newRow(self.packageName, bukkitDevName)
                    print("{0}: bukkitDevName ({1}) for package ({2}) inserted!".format(self.name, bukkitDevName, self.packageName))
                    return bukkitDevName
        raise Error("Failed to get bukkit files page, or plugin is not available on bukkitdev.")

    def __getFilesPage(self):
        try:
            self.bukkitDevName
        except:
            self.bukkitDevName = self.__getBukkitDevName()
            url = "http://dev.bukkit.org/bukkit-plugins/{0}/files/".format(self.bukkitDevName)
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            resp = opener.open(url)
            return resp.read().decode()

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
            versionHash = findall("([a-f\d]{32})", downloadPage)[0]
            if not self.areHashesMatch(versionHash, downloadPageUrl):
                self.database.setVersionHash(versionHash, downloadPageUrl)
            return pq(downloadPage)(".user-action-download").find("a").attr("href")
        except KeyError:
            raise Error("Bukkit page is broken?")
            
    def areHashesMatch(self, hash, href):
        cmpHash = self.database.getVersionHash(href)
        if cmpHash == hash:
            return True
        else:
            return False

if __name__ == "__main__": #Test
    plugin = bukkitPlugin(argv[1])
    print(plugin.getVersionUrl(0))