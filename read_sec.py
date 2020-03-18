from .section import section

def sec_to_sections(p,reverse=False):
    sections=[]
    
    with open(p) as f:
        for line in f.readlines():
            label=line.strip()
            if label=='D':
                sections.append(section(dummy=True))
            else:
                sections.append(section(label=label,reverse=reverse))            
    
    return sections
        
