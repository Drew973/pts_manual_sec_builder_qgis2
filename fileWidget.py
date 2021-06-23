from PyQt4.QtGui import QLineEdit,QFileDialog,QWidget,QHBoxLayout,QPushButton
#from PyQt5.QtWidgets import QLineEdit,QFileDialog,QApplication,QWidget,QHBoxLayout,QPushButton

class saveFileWidget(QWidget):
    
    def __init__(self,parent=None,filt=''):
        super(saveFileWidget,self).__init__(parent)
        
        self.setLayout(QHBoxLayout(self))
       
        self.edit = QLineEdit(self)
        self.layout().addWidget(self.edit)
        
        self.button = QPushButton('...',self)
        self.button.clicked.connect(self.browse)

        self.layout().addWidget(self.button)
        self.filt = filt


    def filePath(self):
        return self.edit.text()

    def setFilter(self,filt):
        self.filt = filt

    def browse(self):
        #p = QFileDialog.getSaveFileName(self, 'Save File',filter=self.filt)[0]#pyqt5
        p = QFileDialog.getSaveFileName(self, 'Save File',filter=self.filt)#pyqt4

        if p:
            self.edit.setText(p)

