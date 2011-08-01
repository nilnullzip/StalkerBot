#!/usr/bin/python

def readKey(keyFileName):
    return open("../options-and-settings/api-keys/" + keyFileName, "r").readline().rstrip('\n').rstrip('\r')

