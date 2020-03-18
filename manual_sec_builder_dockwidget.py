import os
from os import path

#from PyQt4 import QtGui, uic
from  qgis.PyQt import uic

#from PyQt4.QtCore import pyqtSignal,QSettings
from qgis.PyQt.QtCore import pyqtSignal,QSettings

from qgis.utils import iface
#from qgis.gui import QgsFieldProxyModel
from qgis.gui import QgsFieldProxyModel
#from reading import RTESections,secSections
from .write_rte5 import database_to_rte

from qgis.PyQt.QtWidgets import QDockWidget,QFileDialog,QMessageBox,QShortcut
from qgis.PyQt.QtGui import QKeySequence

from sections import sections
from section import section
from read_rte3 import rte_to_sections
from read_sec import sec_to_sections

from layer_functions import selectSections,forward_dir
from secs_to_sr import secsToSR
from sr_to_secs import SRToSecs

def fixHeaders(path):
    with open(path) as f:
        t=f.read()

    r={'qgsfieldcombobox.h':'qgis.gui','qgsmaplayercombobox.h':'qgis.gui'}
    for i in r:
        t=t.replace(i,r[i])

    with open(path, "w") as f:
        f.write(t)


uiPath=os.path.join(os.path.dirname(__file__), 'manual_sec_builder_dockwidget_base.ui')
fixHeaders(uiPath)
FORM_CLASS, _ = uic.loadUiType(uiPath)


class manual_sec_builderDockWidget(QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        super(manual_sec_builderDockWidget, self).__init__(parent)
        self.setupUi(self)
        
        self.addButton.released.connect(self.add)
        self.selectButton.released.connect(self.select)
        self.setSelectedButton.released.connect(self.setSelected)
        self.removeButton.released.connect(self.remove)
        self.saveAsSecButton.released.connect(self.saveAsSec)
        self.saveAsRTEButton.released.connect(self.saveAsRTE)
        self.saveAsSRButton.clicked.connect(self.saveAsSR)
        
        self.addDummyButton.released.connect(self.addDummy)
        self.removeAllButton.clicked.connect(self.removeAll)
        self.loadRTEButton.released.connect(self.loadRTE)
        self.loadSecButton.released.connect(self.loadSec)
        self.loadSRButton.clicked.connect(self.loadSR)
        self.sectionBox.setFilters(QgsFieldProxyModel.String)
        self.sectionBox.activated.connect(self.secFieldSet)

        self.directionBox.setFilters(QgsFieldProxyModel.String)
        self.directionBox.activated.connect(self.dirFieldSet)
        
        self.s=QShortcut(QKeySequence('Ctrl+1'), self)
        self.s.activated.connect(self.add)

        self.loadSecBox.addItems(['No','Yes','Leave blank'])

        self.sections=sections(table=self.secTable,spinbox=self.rowBox)

        self.layerBox.layerChanged.connect(self.layerChange)
        layer=QSettings('pts', 'msb').value('layer','',str)
        self.layerBox.setCurrentIndex(self.layerBox.findText(layer))#try to set to last value 
        self.layerBox.activated.connect(self.layerSet)
        self.layerChange(self.layerBox.currentLayer())

        
                        
    def layerChange(self,layer):
        self.sectionBox.setLayer(layer)
        sf=QSettings('pts', 'msb').value('sectionField','',str)
        self.sectionBox.setCurrentIndex(self.sectionBox.findText(sf))

        self.directionBox.setLayer(layer)
        sd=QSettings('pts', 'msb').value('directionField','',str)
        self.directionBox.setCurrentIndex(self.directionBox.findText(sd))



    def secFieldSet(self):
        sf=self.sectionBox.currentField()
        if sf!='':
            QSettings('pts', 'msb').setValue('sectionField',sf)


    def dirFieldSet(self):
        sf=self.directionBox.currentField()
        if sf!='':
            QSettings('pts', 'msb').setValue('directionField',sf)        

        
    def layerSet(self):
        layer=self.layerBox.currentLayer().name()
        QSettings('pts', 'msb').setValue('layer',layer)
    
    
    def add(self):
        if self.checkLayerSet() and self.checkSectionFieldSet():
        
            sl=self.layerBox.currentLayer()
            secField=self.sectionBox.currentField()
          
            sf=sl.selectedFeatures()
            
            if len(sf)>1:
                iface.messageBar().pushMessage("manual sec builder: >1 feature selected",duration=4)
                return

            if len(sf)<1:
                iface.messageBar().pushMessage("manual secbuilder: no features selected.",duration=4)
                return

            sec=sf[0][secField]
            s=section(label=sec,reverse=self.reverseBox.isChecked())
            
            self.sections.add_section(s)
        
       
    def addDummy(self):
        self.sections.add_section(section(dummy=True,reverse=False))


    def loadRTE(self):
        if self.checkLayerSet() and self.checkSectionFieldSet() and self.checkDirectionFieldSet():
            p=QFileDialog.getOpenFileName(caption='load .rte',filter='*.rte;;*',directory=self.lastFolder())

            if p!='':
                self.setFolder(p)
                secs=rte_to_sections(p)#list of section objects

                for sec in secs:
                    if not sec.dummy:
                        try:
                            fd=forward_dir(sec.label,self.layerBox.currentLayer(),self.sectionBox.currentField(),self.directionBox.currentField())
                           
                            if fd==sec.direction:
                                sec.reverse=False

                            if fd==sec.opposite_direction():
                                sec.reverse=True

                        except:
                            iface.messageBar().pushMessage("manual secbuilder: could not find section %s in layer. reversed? not set. "%(sec.label),duration=4)
                                                    
                    self.sections.add_section(sec)  
                
                
    def lastFolder(self):
        folder=QSettings('pts', 'msb').value('folder','',str)
        if folder!='':
            return folder
        else:
            return path.expanduser('~\\Documents')


    def setFolder(self,p):
        print(p)
        f=path.dirname(p)
        QSettings('pts', 'msb').setValue('folder',f)

        
    def loadSec(self):
        p=QFileDialog.getOpenFileName(caption='load .rte',filter='*.sec;;*',directory=self.lastFolder())
        if p!='':
            self.setFolder(p)

            t=self.loadSecBox.currentText()
            if t=='Yes':
                rev=True
            if t=='No':
                rev=False
            if t=='Leave blank':
                rev=None
            
            for s in sec_to_sections(p,rev):
                self.sections.add_section(s)
        
    def loadSR(self):
        p=QFileDialog.getOpenFileName(caption='load .rte',filter='*.sr;;*',directory=self.lastFolder())
        if p!='':
            self.setFolder(p)
            for s in SRToSecs(p):
                self.sections.add_section(s)


    def remove(self):
        self.sections.remove_selected()
        


    def removeAll(self):
        response = QMessageBox.question(self,'remove all','remove all sections from table?',QMessageBox.Yes | QMessageBox.No)
        if response== QMessageBox.Yes:
            self.sections.clear()


    
    def saveAsSec(self):
        p=QFileDialog.getSaveFileName(self, 'Save File',filter='*.sec;;*',directory=self.lastFolder())
        if p!='':
            if len(self.sections.secs)>0:
                self.setFolder(p)
                self.sections.to_sec(p)
                iface.messageBar().pushMessage("manual secbuilder:saved sec:"+p,duration=4)
            else:
                iface.messageBar().pushMessage("manual secbuilder:no sections to save:",duration=4)



    def saveAsRTE(self):
        p=QFileDialog.getSaveFileName(self, 'Save File',filter='*.rte;;*',directory=self.lastFolder())
        print p
        if p!='':
            if len(self.sections.secs)>0:
                self.setFolder(p)
                f,route_id = os.path.split(p)
                m=database_to_rte(f=p,route_id=route_id,sections=self.sections.secs,database=self.database.text(),host=self.host.text(),user=self.user.text(),password=self.password.text)

                if m==True:            
                    iface.messageBar().pushMessage("manual secbuilder:saved rte:"+p,duration=4)
                else:
                    iface.messageBar().pushMessage("manual secbuilder error:error in making .rte "+m,duration=8)
            else:
                    iface.messageBar().pushMessage("manual secbuilder:no sections to save.",duration=4)
 

    def saveAsSR(self):
        p=QFileDialog.getSaveFileName(self, 'Save File',filter='*.sr;;*',directory=self.lastFolder())
        if p!='':
            if len(self.sections.secs)>0:
                self.setFolder(p)
                secsToSR(self.sections.secs,p)
                iface.messageBar().pushMessage("manual secbuilder:saved .sr:"+p,duration=4)
            else:
                iface.messageBar().pushMessage("manual secbuilder:no sections to save:",duration=4)

        
    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()


    #checks layer is set
    def checkLayerSet(self):
        layer = self.layerBox.currentLayer()
        if not layer is None:
            return True
        else:
            iface.messageBar().pushMessage("manual secbuilder error: no layer selected (under layer tab).",duration=4)
            return False


    #checks section field is set
    def checkSectionFieldSet(self):
        if self.sectionBox.currentField()=='':
            iface.messageBar().pushMessage("manual secbuilder: section field not set (check layer tab).",duration=4)
            return False        
        else:
            return True


    #checks direction field is set
    def checkDirectionFieldSet(self):
        if self.directionBox.currentField()=='':
            iface.messageBar().pushMessage("manual secbuilder: direction field not set (check layer tab).",duration=4)
            return False
        else:
            return True
        
    
    def select(self):
        if self.checkLayerSet() and self.checkSectionFieldSet():
            selected=self.sections.list_selected()
            if len(selected)==0:
                selected=self.sections.list_sections()
            selectSections(selected,self.layerBox.currentLayer(),self.sectionBox.currentField())
            
    
    def setSelected(self):
        if self.checkLayerSet() and self.checkSectionFieldSet():
            feats=self.layerBox.currentLayer().selectedFeatures()
            secs=[f[self.sectionBox.currentField()] for f in feats]
            self.sections.set_selected(secs)
