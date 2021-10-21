from PyQt5 import QtCore as qtc
import os.path
import numpy as np

class bookmark(qtc.QObject):

    '''
    This class is used to write and read bookmarks.
    '''

    contents = qtc.pyqtSignal(list)
    error = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__(parent= None)
        

    def read(self,path):
        
        
        l = list()
        if self._checkExist(path):
            with open(path,"r") as reader:
                tmp = list()
                counter = 1
                for line in reader:
                    if counter%4 != 0:
                        tmp.append(line)
                        counter += 1
                    else:
                        counter = 1
                        tmp.append(line)
                        l.append(tmp)
                        tmp = list()
            self.contents.emit(l)
        return l
        #else:
        #    self.error.emit("File does not exist")


    def write(self,path,timestamp,title,iconShape,iconData):
        '''
        path: string
        timestamp: float
        '''
        print("PATH",path,self._checkExist(path))
        if self._checkExist(path):
            f = open(path,"r+")
            contents = f.readlines()
            f.close()
            newContents = contents.copy()
            #print("newContents",newContents)
            count = 0
            for line in contents:
                if (count)%4 != 0:
                    #print("skipping",line,count,(count)%3)
                    count += 1
                    continue

                if timestamp<float(line):
                    #print("osn",timestamp,line,float(line))
                    newContents.insert(count,str(timestamp)+"\n")
                    newContents.insert(count+1,title+"\n")
                    newContents.insert(count+2,iconShape+"\n")
                    newContents.insert(count+3,iconData+"\n")
                    self._writeList(path,newContents)
                    return
                elif timestamp == float(line):
                    #print("popping",count,newContents[count])
                    newContents.pop(count)
                    #print("popping",count,newContents[count])
                    newContents.pop(count)
                    #print("popping",count,newContents[count])
                    newContents.pop(count)
                    #print("popping",count,newContents[count])
                    newContents.pop(count)
                    
                    newContents.insert(count,str(timestamp)+"\n")
                    newContents.insert(count+1,title+"\n")
                    newContents.insert(count+2,iconShape+"\n")
                    newContents.insert(count+3,iconData+"\n")

                    self._writeList(path,newContents)
                    return
                count += 1
                #print("askdnladp",timestamp,line,float(line))

            # if it reaches here, that means the break conditions were not met.
            
            newContents.append(str(timestamp)+"\n")
            newContents.append(title+"\n")
            newContents.append(iconShape+"\n")
            newContents.append(iconData+"\n")

            self._writeList(path,newContents)
        else:
            newContents = [str(timestamp)+"\n",title+"\n",iconShape+"\n",iconData+"\n"]
            self._writeList(path,newContents)
        

    def _writeList(self,path,newContents):
        
        #print("newContents2",newContents)
        with open(path,"w") as reader:
            reader.writelines(newContents)

    def _checkExist(self,path):
        
        return os.path.isfile(path)