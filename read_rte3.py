from .section import section

def rte_to_sections(path):
    
    lines=[]
    with open(path) as f:
        for line in f.readlines():
            lines.append(line)
            
    n=int(lines[0][63:69])#number of lanes
    lines=lines[1:n]#2.1 type records
    
    sections=[]
    for line in lines:
        sec=line[0:30].strip()#section label.
        direction=line[30:32].strip()# strip() removes whitespace from string
        if sec=='':#dummy
            sections.append(section(dummy=True))
        else:
            sections.append(section(label=sec,direction=direction))
    
    return sections
