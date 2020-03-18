import psycopg2
import psycopg2.extras
from section import section
import rte


def database_to_rte(f,sections,route_id,host,database,user,password=''):
    try:
        con = psycopg2.connect(database=database,host=host,user=user,password=password)
        cur = con.cursor(cursor_factory = psycopg2.extras.DictCursor)#return the db results as dict
    except:
        return 'could not connect to database'

    bs=bad_sections(cur,sections)
    if len(bs)>0:
        return 'sections: '+','.join(bs)+' not in database'

    with open(f,'w') as to:
        new_sections=remove_consecutive(roundabout_dummys(cur,sections))
        to.write(rte.R1_1(route_identifier=route_id,n_lanes=len(new_sections)-1)+'\n')

        #remove dummys from start
        while new_sections[0].dummy:
            del new_sections[0]
        
        last_valid=section()
        
        for sec in new_sections:
            if sec.dummy:
                r=end_x_y(cur,last_valid)
                to.write(rte.dummy_R2_1(r['end_marker'],r['end_marker_x'],r['end_marker_y'])+'\n')
                #start node of dummy = end node of last.
                
            else:
                to.write(surv_line(cur,sec)+'\n')
                last_valid=sec
         
        #route end record
        r=end_x_y(cur,last_valid)
        to.write(rte.R3_1(r['end_marker'],r['end_marker_x'],r['end_marker_y'])+'\n')        
        
        new_sections.sort() #sort section in alphabetical order. works because section has __eq__ and __lt__ methods
        for sec in new_sections:
            if not sec.dummy:
                to.write(r4_1(cur,sec)+'\n')

        con.close()        
        return True
   
#returns true if sec in database
def check_section(cur,sec):
    cur.execute("select 1<=count(sect_label) as in_prog FROM prog WHERE sect_label = %s",(sec.label,))
    p = cur.fetchone()[0]
    cur.execute("select 1<=count(sec) as in_lrp19 FROM lrp19 WHERE sec = %s",(sec.label,))
    return p and cur.fetchone()[0]

def bad_sections(cur,sections):
    bad=[]
    for s in sections:
        if not check_section(cur,s) and not s.dummy:
            bad.append(s.label)
    return bad

#returns list of sections without same label and direction consecutively
def remove_consecutive(sections):
    last=sections[0]
    new_sections=[last]
    for sec in sections:
        if sec.label!=last.label or sec.reverse!=last.reverse:
            new_sections.append(sec)
        last=sec
    return new_sections


def is_roundabout(cur,sec):#sec=section object
    if sec.dummy:
        return False
    cur.execute("SELECT funct_name FROM prog WHERE sect_label = %s", (sec.label, ))
    row = cur.fetchone()[0]
    if row == 'RBT ':
        return True
    else:
        return False


def is_single(cur,sec):#sec=section object
    cur.execute("SELECT dual_name FROM prog WHERE sect_label = %s", (sec.label, ))
    try:
        row=cur.fetchone()[0]
    except:
        return False
    if 'Two Way Single' in row:
        return True
    else:
        return False


def roundabout_dummys(cur,sections):
    new_sections=[]
    for s in sections:     
        if is_roundabout(cur,s):
            new_sections.append(section(dummy=True))
            new_sections.append(s)
            new_sections.append(section(dummy=True))
        else:
            new_sections.append(s)
    return new_sections


def sql(cur, query, sec):#sec=section object
    dirs = {'NB':'SB', 'SB':'NB', 'EB':'WB', 'WB':'EB', 'CW':'CW', 'AC':'AC'}
    cur.execute(query, (sec.label, ))
    r=cur.fetchone()
    if r:
        row = dict(r)
        if sec.reverse:
            if 'surv_dir' in row:
                row['surv_dir'] = dirs[row['surv_dir']]
        return row
    else:
        raise ValueError('no result for query :\n'+str(cur.query)+' \n Are you using the right database for this area? ')


def surv_line(cur,sec):#R2.1
    if sec.reverse:
        q="""SELECT  
        direction as surv_dir,
        'Lane 1' as lname, 
        sec_l as end_ch, 
        lrp_code, 
        x, 
        y
        FROM lrp19
        WHERE lrp19.ch=sec_l and lrp19.sec=%s"""
        s=sql(cur=cur,query=q,sec=sec)
        return rte.R2_1(sec.label,s['surv_dir'],s['lname'],0,s['end_ch'],s['lrp_code'],s['x'],s['y'])
    else:
        q="""select
        direction as surv_dir,
        'Lane 1' as lname,
        sec_l as end_ch,
        lrp_code,
        x,
        y
        FROM lrp19
        WHERE lrp19.ch=0 and lrp19.sec=%s"""
        
        s=sql(cur=cur,query=q,sec=sec)
        #section_label,NB,SB etc,lane_name,start_chainage,end_chainage,start_reference_label,start_x,start_y
        return rte.R2_1(sec.label,s['surv_dir'],s['lname'],0,s['end_ch'],s['lrp_code'],s['x'],s['y'])
        
def end_x_y(cur,sec):
    if sec.reverse:
        q="""SELECT lrp_code as end_marker,
        x as end_marker_x,
        y as end_marker_y
        FROM lrp19
        WHERE lrp19.ch=0 and lrp19.sec=%s"""
       
    else:
        q="""SELECT lrp_code as end_marker,
        x as end_marker_x,
        y as end_marker_y
        FROM lrp19
        WHERE lrp19.ch=lrp19.sec_l and lrp19.sec=%s"""
        
    return sql(cur=cur,query=q,sec=sec)


def r4_1(cur,sec):
    q = """SELECT 
    to_char(start_date, 'DD-Mon-YYYY') as start_date, 
    sec_length as length, 
    direc_code as direction, 
    funct_name as function
    FROM prog
    WHERE sect_label=%s"""
        
    r=sql(cur=cur,query=q,sec=sec)
    return rte.R4_1(sec.label,r['start_date'],'',r['length'],r['direction'],r['function'])
