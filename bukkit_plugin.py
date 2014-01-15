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
        self.version = sub("\r|\n", "", findall("version: (.*)", self.yaml)[0])
        self.name = sub("\r|\n", "", findall("name: (.*)", self.yaml)[0])

    def getGoogleResult(self):
        url = "http://www.google.com.hk/search?q={0}+files+site%3Adev.bukkit.org%2Fbukkit-plugins".format(sub(" ", "+", self.name))
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        resp = opener.open(url)
        return resp.read().decode()
        
    def getFilesPage(self):
        self.googleResult = self.getGoogleResult()
        url = "http://" + sub("<[^>]*>", "", pq(self.googleResult)(".kv").find("cite").html())
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        resp = opener.open(url)
        return resp.read().decode()
        
    def getAllVersions(self):
        self.filesPage = self.getFilesPage()
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
        return table
        
    def getVersionUrl(self, index):
        try:
            self.versions
        except:
            self.versions = plugin.getAllVersions()
        finally:
            downloadPageUrl = self.versions[index]["Name"]["href"]
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            resp = opener.open(downloadPageUrl)
            downloadPage = resp.read().decode()
            return pq(downloadPage)(".user-action-download").find("a").attr("href")

plugin = bukkitPlugin(argv[1])
print(plugin.getVersionUrl(0))