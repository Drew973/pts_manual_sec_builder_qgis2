import os
from qgis.utils import iface




#import imp
#rte = imp.load_source('rte', 'rte.py')
#from .rte import rte
#import rte.rte
from .rte import rte



from qgis.gui import QgsFileWidget
from qgis.PyQt.QtCore import QSettings

from . import layer_functions

#need features and if feature is reversed.
#redo class for section/dummy. need feature,reversed


from . import fields_dialog

import fileWidget

class makeRteDialog(fields_dialog.fieldsDialog):    

#parent must have attribute sections
    def __init__(self,layerBox,labelBox,parent):

        #fields=['section_label','direction','section_len','start_node','end_node','start_date','end_date','function','lane_name','start_chainage','end_chainage','start_x','start_y','end_x','end_y']
        fields=['section_label','direction','section_len','start_node','end_node','start_date','end_date','function']

        super(makeRteDialog,self).__init__(fields,layerBox,parent,settings=QSettings('pts', 'makeRte'))

        self.setTooltips({'direction':'Field with direction. Values need to be one of NB,EB,SB,WB,CW,AC'})



        self.fileWidget = fileWidget.saveFileWidget(self,'*.rte;;*')
        #self.fileWidget=QgsFileWidget(self)
        #self.fileWidget.setStorageMode(QgsFileWidget.SaveFile)#qgis3
       # self.fileWidget.setStorageMode(3)#qgis2

        
        self.layout().insertRow(0,'File',self.fileWidget)

        self.labelBox=labelBox
        self.buttonBox.rejected.connect(self.hide)
        
        self.setWindowTitle('save as rte')
        
        self.labelBox=labelBox


        
    def make(self,labels,directions):
    #    fields=self.getFields()
        #p=self.fileWidget.filePath()
        p=self.fileWidget.filePath()

        if not p:
            iface.messageBar().pushMessage("manual secbuilder:no file selected",duration=4)
            return
            
        if not self.fieldsSet():
            iface.messageBar().pushMessage("manual secbuilder:fields not set",duration=4)
            return           
        
        #(self,section_label,direction,section_len,start_node,end_node,start_date,end_date,function,is_dummy=False,lane_name='Lane 1',start_chainage=0,end_chainage=None,start_x=None,start_y=None,end_x=None,end_y=None)
        rteItems=self.labelsToRteItems(labels,directions)

        with open(p,'w') as to:
            rte.write_rte(rteItems,to,os.path.basename(p))

        iface.messageBar().pushMessage("manual secbuilder:saved as %s"%(p),duration=4)
        self.hide()



#labels and directions to list of rte_items and dummys.dummys use last item. dummys at start removed.
        
    def labelsToRteItems(self,labels,directions):

        labelField=self.parent().getLabelField()
        if labelField:
            items=[]
            lastValid=None
            for i,lab in enumerate(labels):
                if lab=='D':
                    if lastValid:
                        items.append(lastValid.make_dummy())
                else:
                    item = self.rteItem(lab,rev=directions[i],labelField=labelField)
                    items.append(item)
                    lastValid = item
                    
            return items


    #section label and reversed to rteItem. will give error for 'D'
    #def rteItem(self,label:str,rev:bool,labelField:str):

    def rteItem(self,label,rev,labelField):
        
        if self.fieldsSet():
            fields = self.getFields()
            
        f=layer_functions.getFeature(layer=self.getLayer(),field=labelField,value=label)
        i=rte.rte_item(**featureToDict(f,fields))

        if rev:
            i.flip_direction()

        return i
        

    
    def getValue(self,fid,field):
        self.layerBox.currentLayer()




#roundabouts should have dummy before and after.
#do this as checks menu of main thing not in rte

def addRoundaboutDummys(sections,isRoundaboutFunction):
        new_sections=[]
        for s in sections:
            
            if isRoundaboutFunction(s):
                new_sections.append(s(dummy=True))
                new_sections.append(s)
                new_sections.append(s(dummy=True))
                
            else:
                new_sections.append(s)
        
        return new_sections


#do this as checks menu of main thing not in rte    
def remove_consecutive(sections):
    last=sections[0]
    new_sections=[last]
        
    for sec in sections:
        if sec.label!=last.label or sec.reverse!=last.reverse:
            new_sections.append(sec)
        last=sec
            
    return new_sections


#dict of field and attribute
def featureToDict(feature,fields):
    return {f:feature[fields[f]] for f in fields}

    
        
