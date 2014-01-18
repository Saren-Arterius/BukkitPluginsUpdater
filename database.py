#!/usr/bin/python3.3
from sys import argv
import os
import sqlite3

class database(object):
    def __init__(self):
        self.dbFile = os.path.abspath(os.path.dirname(argv[0])) + "\\" + "database.db"
        self.conn = sqlite3.connect(self.dbFile)
        
    def createTables(self):
        try:
            cur = self.conn.cursor()
            cur.execute("CREATE TABLE `version_hash` (`href` TEXT NULL, `hash` TEXT NULL, PRIMARY KEY (`href`) )")
            cur.execute("CREATE TABLE `convert_table` (`package_name` TEXT NULL, `bukkitdev_name` TEXT NULL, PRIMARY KEY (`package_name`) )")
            cur.close()
            return True
        except sqlite3.OperationalError:
            return False
            
    def areTablesExist(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM convert_table LIMIT 0")
            cur.close()
            return True
        except sqlite3.OperationalError:
            return self.createTables()
    
    def selectRow(self, packageName):
        try:
            cur = self.conn.cursor()
            data = (packageName,)
            sql = cur.execute("SELECT bukkitdev_name FROM convert_table WHERE package_name=?", data)
            self.conn.commit()
            for row in sql:
                cur.close()
                return row[0]
            return False
        except sqlite3.OperationalError:
            if self.areTablesExist():
                return self.selectRow(packageName)
    
    def newRow(self, packageName, bukkitDevName):
        try:
            cur = self.conn.cursor()
            data = (packageName, bukkitDevName)
            cur.execute("INSERT INTO convert_table VALUES (?,?)", data)
            self.conn.commit()
            return True
        except sqlite3.OperationalError:
            if self.areTablesExist():
                return self.newRow(packageName, bukkitDevName)
            
    def updateRow(self, packageName, bukkitDevName):
        try:
            cur = self.conn.cursor()
            data = (bukkitDevName, packageName)
            cur.execute("UPDATE convert_table SET bukkitdev_name=? WHERE package_name=?", data)
            self.conn.commit()
            return True
        except sqlite3.OperationalError:
            if self.areTablesExist():
                return self.updateRow(packageName, bukkitDevName)
                
    def deleteRow(self, packageName):
        try:
            cur = self.conn.cursor()
            data = (packageName,)
            cur.execute("DELETE FROM convert_table WHERE package_name=?", data)
            self.conn.commit()
            return True
        except sqlite3.OperationalError:
            if self.areTablesExist():
                return self.deleteRow(packageName)

    def getVersionHash(self, href):
        try:
            cur = self.conn.cursor()
            data = (href,)
            sql = cur.execute("SELECT hash FROM version_hash WHERE href=?", data)
            self.conn.commit()
            for row in sql:
                cur.close()
                return row[0]
            return False
        except sqlite3.OperationalError:
            if self.areTablesExist():
                return self.getVersionHash(href)
                
    def setVersionHash(self, hash, href):
        try:
            cur = self.conn.cursor()
            data = (href, hash,)
            cur.execute("INSERT INTO version_hash VALUES (?,?)", data)
            self.conn.commit()
            return True
        except sqlite3.OperationalError:
            if self.areTablesExist():
                return self.setVersionHash(hash, href)

if __name__ == "__main__": #Test
    database = database()
    database.newRow("test.package", "goodName")