from qgis.core import QgsFeatureRequest


def selectSections(sections,layer,secField):
    a=','.join([singleQuote(s) for s in sections])
    #Field names in double quotes, string in single quotes
    e="%s IN (%s)" %(doubleQuote(secField),a)#expression looks like "Column_Name" IN ('Value_1', 'Value_2', 'Value_N')
    
    layer.selectByExpression(e)
   # iface.actionZoomToSelected().trigger()#zoom to selected


def singleQuote(s):
    return "'%s'"%(s)


def doubleQuote(s):
    return '"%s"'%(s)  



def findSection(section,layer,lab_field):
    e=doubleQuote(lab_field)+'='+singleQuote(section)
    r=QgsFeatureRequest().setFilterExpression( e)
    feats=[]
        
    for f in layer.getFeatures(r):
        feats.append(f)

    if len(feats)==1:
        return feats[0]

    if len(feats)==0:
        raise ValueError('section %s not found'%(section))
    
    
def forward_dir(section,layer,lab_field,dir_field):
    f=findSection(layer=layer,lab_field=lab_field,section=section)
    return f[dir_field]

