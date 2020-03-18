class section():
    def __init__(self,label='',dummy=False,reverse=None,direction=''):
        self.dummy=dummy#True if dummy
        self.reverse=reverse#True if in CL1
        self.direction=direction#direction code like NB,EB...
        
        if dummy:
            self.label='D'
            self.reverse=None
        else:
            self.label=label

        
    def flip_direction(self):
        if not self.reverse is None:
            self.reverse= not self.reverse


    def xsp(self):
        if self.reverse is None:
            return ''
        
        if self.reverse:
            return 'CR1'
        else:
            return 'CL1'


    def opposite_direction(self):
        if self.direction is None:
            return
        else:
            d={'NB':'SB','EB':'WB','SB':'NB','WB':'EB','CW':'CW','AC':'AC','':''}#origonal code did CW':'CW','AC':'AC'. 
            #specification says CW oposite at AC
            return d[self.direction]
    
    
    #what self==other should return. Needed for sorting.
    def __eq__(self, other):
        return self.label==other.label and self.reverse==other.reverse
    
    
    #less than. True if self<other
    #needed for sorting
    def __lt__(self, other):
        return self.label < other.label
    
    
    def reverse_to_text(self):
        t=''
        if self.reverse:
            t='Yes'
        if self.reverse==False:
            t='No'
        return t
