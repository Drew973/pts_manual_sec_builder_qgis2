from . import fields_dialog

from qgis.gui import QgsFileWidget
from qgis.utils import iface



class loadRteDialog(fields_dialog.fieldsDialog):    

#parent must have attribute sections
    def __init__(self,layerBox,parent):
        fields=['direction']

        super(loadRteDialog,self).__init__(fields=fields,layerBox=layerBox,parent=parent)

        self.setTooltips({'direction':'Field of layer with direction. Values need to be one of NB,EB,SB,WB,CW,AC'})

        self.fileWidget=QgsFileWidget(self)        
        self.layout().insertRow(0,'File',self.fileWidget)

        self.buttonBox.rejected.connect(self.hide)
        
        self.setWindowTitle('load rte')

        self.clearMode=True# True=insert at row,False=clear and load
        self.buttonBox.accepted.connect(self.load)

       

    def setclearMode(self,mode):
        self.clearMode=mode
        


    def show(self,clearMode):
        self.clearMode=clearMode
        super(loadRteDialog,self).show()



    def load(self):

        layer=self.parent().getLayer()

        p=self.fileWidget.filePath()
        if not p:
            iface.messageBar().pushMessage("manual secbuilder:no file selected",duration=4)
            return     


        if not self.fieldsSet():
            iface.messageBar().pushMessage("manual secbuilder:direction field not set",duration=4)
            return           
        directionField=self.getFields()['direction']

        
        labelField=self.parent().getLabelField()
        

        with open(p,'r') as f:
            self.parent().model.loadRTE(f=f,layer=layer,labelField=labelField,directionField=directionField,row=self.parent().rowBox.value(),clear=self.clearMode)

        self.hide()



            



        
