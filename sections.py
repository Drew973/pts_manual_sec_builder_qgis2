#from qgis.PyQt.QtGui import QTableWidgetItem,QTableWidgetSelectionRange
from qgis.PyQt.QtWidgets import QTableWidgetItem,QTableWidgetSelectionRange
from qgis.PyQt.QtCore import Qt

class sections():
    
    def __init__(self,table=False,spinbox=False):
        self.secs=[]
        self.table=table
        self.spinbox=spinbox
        
        if self.table:
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(['section','reversed?'])
            self.table.cellDoubleClicked.connect(self.change_direction)        

        if self.spinbox:
            self.spinbox.setMaximum(1)

    def add_section(self,section,i=-1):
        if i<0:
            i=len(self.secs)+i+1
        if self.spinbox:
            i=self.spinbox.value()-1
        self.secs.insert(i,section)
        self.refresh_table()
        if self.spinbox:
            self.spinbox.setMaximum(len(self.secs)+1)
            self.spinbox.setValue(self.spinbox.value()+1)

    def remove_selected(self):
        rows=[]
        for i in self.table.selectedIndexes():
            if i.column()==0:
                rows.append(i.row())#indexes to be deleted
        #deleting item reindexes list, deleting in decending order avoids this causing problem
        for r in sorted(rows, reverse=True):
            del self.secs[r]
                
        self.refresh_table()
        
        if self.spinbox:
            self.spinbox.setMaximum(len(self.secs)+1)


    def refresh_table(self):
        if self.table:
            self.table.setRowCount(0)
            for i,sec in enumerate(self.secs):
                self.table.insertRow(i)
                self.table.setItem(i,0, QTableWidgetItem(sec.label))
                t=''
                if sec.reverse:
                    t='Yes'
                if sec.reverse==False:
                    t='No'
                self.table.setItem(i,1, QTableWidgetItem(t))
            
            

    #None->not_reversed->reversed->None
    def change_direction(self,row,col):
        if col==1:
            r=self.secs[row].reverse
            if r is None:
                self.secs[row].reverse=False
            if r==False:
                self.secs[row].reverse=True
            if r:
                self.secs[row].reverse=None
            self.table.setItem(row,col, QTableWidgetItem(self.secs[row].reverse_to_text()))
            

    def clear(self):
        self.secs=[]
        self.refresh_table()
        if self.spinbox:
            self.spinbox.setMaximum(1)
            
            
    def to_sec(self,path):
        with open(path,'w') as f:
            for sec in self.secs:
                f.write(sec.label+'\n')
   
    def list_sections(self):
        return [sec.label for sec in self.secs]
    
    
    def list_selected(self):
        rows=[]
        for i in self.table.selectedIndexes():
            if i.column()==0:
                rows.append(i.row())#indexes of sections
        return [self.secs[i].label for i in rows]


    def set_selected(self,sections):
        secs=self.list_sections()

        for sec in secs:
            item=self.table.findItems(sec,Qt.MatchExactly)[0]#item containing section
            
            if sec in sections:
                item.setSelected(True)
                self.table.item(item.row(),item.column()+1).setSelected(True)#item in reversed? col
                
            else:
                item.setSelected(False)
                self.table.item(item.row(),item.column()+1).setSelected(False)#item in reversed? col

     

                
