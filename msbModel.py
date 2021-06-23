from PyQt4 import QtGui

from qgis.PyQt.QtCore import Qt,pyqtSignal
from . import layer_functions



class msbModel(QtGui.QStandardItemModel):
    countChanged = pyqtSignal(int)#amount rowCount changed by. Methods that change rowCount should emit this AFTER changing count.


    def __init__(self,parent=None):
        
        super(msbModel, self).__init__(parent)
        self.headerLabels=['section','reversed']
        self.setHorizontalHeaderLabels(self.headerLabels)


        self.revs=['Yes','No','Leave Blank']
        self.bools=[True,False,None]


    def dropMimeData(self, data, action, row, col, parent):
        """
        Always move the entire row, and don't allow column "shifting"
        """
        return super(msbModel, self).dropMimeData(data, action, row, 0, parent)


#(self,row:int)
    def getRow(self,row):
        return [self.data(self.index(row,c)) for c in range(self.columnCount())]


#self,row:int
    def takeRow(self,row):
        r= super(msbModel, self).takeRow(row)
        self.countChanged.emit(-1)             
        return r


    def appendRow(self,items):
        super(msbModel, self).appendRow(items)
        self.countChanged.emit(1)


    def insertRow(self,row,items):
        super(msbModel,self).insertRow(row,items)
        self.countChanged.emit(1)

    
#returns number of rows added (1)  
    def addRow(self,label,isReversed=None,rowNumber=None):
        
        if not isinstance(rowNumber,int):
            self.appendRow([makeItem(label),makeItem(isReversed)])
        
        else:
            if rowNumber>self.rowCount():
                self.appendRow([makeItem(label),makeItem(isReversed)])
            else:
                self.insertRow(rowNumber,[makeItem(label),makeItem(isReversed)])#does nothing if rowNumber not in model



    def clear(self):
        rc=self.rowCount()
        super(msbModel, self).clear()
        self.setHorizontalHeaderLabels(self.headerLabels)
        self.countChanged.emit(-rc)



#sec is field like object with readlines() method
#returns number of rows added.
    def loadRTE(self,f,layer,labelField,directionField,row=None,clear=False):
        
        if clear:
            self.clear()
            self.setHorizontalHeaderLabels(self.headerLabels)

        lines=[line for line in f.readlines()]

        n=int(lines[0][63:69])#number of lanes is 1st line of file 63:69
        R2_1s=lines[1:n+1]#2.1 type records
                
        for line in R2_1s:
            sec = line[0:30].strip()#section label.

            if sec:
                direction = line[30:32].strip()# strip() removes whitespace from string

                forwardDirection=str(layer_functions.forward_dir(sec,layer,labelField,directionField))
                f = direction==forwardDirection#True if direction reversed. 

                self.addRow(rowNumber=row,label=sec,isReversed=not f)
                
            else:
                self.addDummy(row)

            if row:
                row+=1


    def loadSr(self,f,row=None):
        for line in f.readlines():
            r=line.strip().split(',')
            if r[0]!='section':#not header
                self.addRow(rowNumber=row,label=r[0],isReversed=self.revToBool(r[1]))
                if row:
                    row+=1        
        


    def addDummy(self,row):
        self.addRow(label='D',isReversed=None,rowNumber=row)


    def loadSec(self,f,rev,row,clear=False):
        if clear:
            self.clear()

        for line in f.readlines():

            if isDummy(line):
                self.addDummy(row)

            else:
                r=line.strip().split(',')
                label=r[0]
            
                if label!='section':#not header
                    self.addRow(rowNumber=row,label=label,isReversed=rev)
                     
            if row:
                row+=1


    def saveSec(self,f):
        f.write('\n'.join(self.sectionLabels()))#label\n



    def saveSr(self,f,header=True):
        if header:
            f.write('section,reversed')
                    
        for r in range(self.rowCount()):
            lab=str(self.item(r,0).data(Qt.EditRole))
            rev=self.boolToRev(self.item(r,1).data(Qt.EditRole))
            f.write('\n%s,%s'%(lab,rev))

  

    def sectionLabels(self):
        return [self.item(r,0).data(Qt.EditRole) for r in range(self.rowCount())]
        

    def directions(self):
        return [self.item(r,1).data(Qt.EditRole) for r in range(self.rowCount())]


    def revToBool(self,rev):
        i=self.revs.index(rev)
        return self.bools[i]


    def boolToRev(self,b):
        i=self.bools.index(b)
        return self.revs[i]
            

    #surveys need to start at start node and finish at end node. 
    #for roundabouts there will be a dummy between end node of last section and start node of roundabout.
    #another between end node of roundabout and start node of next section.
    def addRoundaboutDummys(self,layer,rbtField):
        for i in range(self.rowCount(),0):#count down to avoid problems with indexes changing.
            pass


    def remove_consecutive(self):
        lastLabel = None
        lastDirection = None
        
        for i in range(self.rowCount(),0):#count down to avoid problems with indexes changing.
            label = self.item(r,0).data(Qt.EditRole)
            direction = self.item(r,1).data(Qt.EditRole)
            if label==lastLabel and direction==lastDirection:
                self.takeRow(i)
    
            lastLabel = label
            lastDirection = direction


def isDummy(secLine):
    return secLine.strip()=='D'


def makeItem(data):
    item=QtGui.QStandardItem()
    item.setData(data,role=Qt.EditRole )
    item.setDropEnabled(False)
    #item.setText(str(data))
    return item
