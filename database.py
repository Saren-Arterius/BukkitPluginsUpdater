#!/usr/bin/python3.3
from os.path import dirname, realpath
import sqlite3

class database(object):
    def __init__(self):
        self.dbFile = dirname(realpath(__file__)) + "\\" + "database.db"
        self.conn = sqlite3.connect(self.dbFile)
        
    def createTables(self):
        try:
            cur = self.conn.cursor()
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
            
if __name__ == "__main__": #Test
    database = database()
    database.newRow("test.package", "goodName")