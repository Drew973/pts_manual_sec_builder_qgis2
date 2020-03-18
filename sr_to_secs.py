from section import section

def SRToSecs(sd):
    sections=[]
    
    with open(sd) as f:
        for line in f.readlines():
            row=line.strip().split(',')
            if row[0]!='section':#header
                if row[0]=='D':
                    sections.append(section(dummy=True))            
                else:
                    if row[1]=='No':
                        sections.append(section(label=row[0],reverse=False))
                    else:
                        sections.append(section(label=row[0],reverse=True))                
    return sections
