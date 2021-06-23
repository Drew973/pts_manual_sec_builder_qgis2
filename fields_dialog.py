from qgis.PyQt.QtWidgets import QDialog,QFormLayout,QDialogButtonBox
from qgis.gui import QgsFieldComboBox




#settings=QSettings
class fieldsDialog(QDialog):

    def __init__(self,fields,layerBox,parent=None,settings=None):
        super(QDialog,self).__init__(parent)

        self.setLayout(QFormLayout(self))
        
        self.fields = {f:QgsFieldComboBox(parent=self) for f in fields}
        self.settings = settings

        for f in self.fields:
            #qformlayout.addRow(const QString &labelText, QWidget *field)
            self.layout().addRow(f,self.fields[f])
            layerBox.layerChanged.connect(self.fields[f].setLayer)
            self.fields[f].setLayer(layerBox.currentLayer())
            if settings:
                self.fields[f].fieldChanged.connect(self.saveSettings)
            
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,parent=self)

        self.layout().addRow(self.buttonBox)

        self.layerBox = layerBox
        
        if settings:
            self.loadSettings()


#return True if all fields are set
    def fieldsSet(self):
        for f in self.fields:
            if not self.fields[f].currentField():
                return False
        return True



    def saveSettings(self):
        self.settings.setValue('values',self.getFields())
        
        
    
    def getFields(self):
        return {f:self.fields[f].currentField() for f in self.fields}


    def layerSet(self):
        if self.layerBox.currentLayer():
            return True
        

    def getLayer(self):
        layer=self.layerBox.currentLayer()
        if layer:
            return layer
        else:
            raise ValueError('layer not set')

        

    def loadSettings(self):
        vals=self.settings.value('values')
        if vals:
            self.setFields(vals)


    
    #load dict of name:field
    #use in loading settings so should to fail silently
    def setFields(self,d):
        for k in d:
            if k in self.fields:
                try:
                    self.fields[k].setField(d[k])
                except:
                    pass


    def __getattr__(self, name):
        return self.fields[name].currentField()



    #dict of {field:tooltip}
    def setTooltips(self,tooltips):
        for f in tooltips:
            self.fields[f].setToolTip(tooltips[f])
