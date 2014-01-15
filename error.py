#!/usr/bin/python3.3
class Error(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "[ERROR] %s\n" % str(self.message)