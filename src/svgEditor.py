import xml.etree.ElementTree as ET


class svgEditor():

    def __init__(self,path,bboxColorHex,progressBarColorHex):
        self.path = path
        self.bboxColorHex = bboxColorHex
        self.progressBarColorHex = progressBarColorHex

        #colorHex = "#1fa544"
        #colorHex2 = "#1fa544"
        #path = "D:/splashScreen2-01.svg"
    def process(self):
        tree = ET.parse(self.path)
        root = tree.getroot()
        #print(root.tag)
        if self.progressBarColorHex is not None:
            root.find("{http://www.w3.org/2000/svg}rect").set("fill",self.progressBarColorHex)
        #root.find()

        for child in root.findall("{http://www.w3.org/2000/svg}g"):
            #print(child.tag,"banana", child.attrib)
            #print(child.find("{http://www.w3.org/2000/svg}rect").tag,"banana", child.find("{http://www.w3.org/2000/svg}rect").attrib)
            if child.find("{http://www.w3.org/2000/svg}rect") is not None and child.find("{http://www.w3.org/2000/svg}rect").attrib["x"] == "2.5":
                child.find("{http://www.w3.org/2000/svg}path").set("fill",self.bboxColorHex)

        #for child in root:
        #    print(child.tag,"apple", child.attrib)

        tree.write(self.path)
