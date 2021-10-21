from PyQt5 import QtCore as qtc
import os
import sys
import xml.etree.ElementTree as ET

class settings:
    """Loads default settings and saves it via QSettings. """
    def __init__(self):
        self.s = qtc.QSettings("Zeeshan Z. D.", "Exero")
        self._dict = None
        self._dict = self.getSettingsDict()
    
    def reset(self):
        # Unpickle python dict containing settings
        x = self.setDefaults({})
        self.saveSettings(x)
        return x

    def getSettingsDict(self):
        
        #if self.dict.keys()
        x = {key:self.value(key,None,str) for key in self.s.allKeys() }
        print("dict ",x)
        x = self.setDefaults(x)
        print("dict after edit ",x)
        return x
        

    def saveSettings(self, settingsDict):
        for key,value in settingsDict.items():
            self.setValue(key,value)

    def value(self, key, defaultVal = None, type=None):

        if defaultVal==None and self._dict is not None:
            defaultVal = self._dict.get(key)
        if type == None:
            return self.s.value(key, defaultVal)
        return self.s.value(key, defaultVal, type=type)

    def setValue(self, key, variant):
        self.s.setValue(key, variant)

    def setDefaults(self,dict):
        #path = r"D:\zeeshan work\fyp gui\Exero\exero\defaultSettings.xml"
        if getattr(sys, 'frozen', False):
            directory = sys._MEIPASS
        else: # Not frozen
            directory = os.path.dirname(__file__)
        path = os.path.join(directory, "defaultSettings.xml")
        tree = ET.parse(path)
        root = tree.getroot()
        for child in root:
            #print(child.tag,"banana", child.text,type(child.text))
            dict.setdefault(child.tag,child.text)
        return dict



__obj = settings()

def getObj():
    return __obj
