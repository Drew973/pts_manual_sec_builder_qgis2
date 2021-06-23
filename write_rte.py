import psycopg2
import psycopg2.extras
from .section import section

from .database_dialog.database_dialog import database_dialog


class database_to_rte(database_dialog):

    def sql(self, query, sec):#sec=section object
        dirs = {'NB':'SB', 'SB':'NB', 'EB':'WB', 'WB':'EB', 'CW':'CW', 'AC':'AC'}
        self.cur.execute(query, (sec.label, ))
        r=self.cur.fetchone()
        if r:
            row = dict(r)
            if sec.reverse:
                if 'surv_dir' in row:
                    row['surv_dir'] = dirs[row['surv_dir']]
            return row
    
    #for dummys r2.1 and r3.1
    def end_x_y(self,sec):
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
        
        return self.sql(q,sec)
        
        
        #start_reference_label,start_x,start_y
        
        
        
    def surv_line(self,sec):#R2.1
        if sec.reverse:
            q="""SELECT sec, 
            direction as surv_dir,
            'Lane 1' as lname, 
            0::float as start_ch, 
            sec_l as end_ch, 
            lrp_code, 
            x, 
            y
            FROM lrp19
            WHERE lrp19.ch=sec_l and lrp19.sec=%s"""
        
        else:
            q="""SELECT sec, 
            direction as surv_dir,
            'Lane 1' as lname,
            0::float as start_ch,
            sec_l as end_ch,
            lrp_code,
            x,
            y
            FROM lrp19
            WHERE lrp19.ch=0 and lrp19.sec=%s"""
        
        s=self.sql(q,sec)
        #section_label,direction,lane_name,start_chainage,end_chainage,start_reference_label,start_x,start_y

        print(s['sec'],s['surv_dir'],s['lname'],s['start_ch'],s['end_ch'],s['lrp_code'],s['x'],s['y'])
        self.rte.R2_1(s['sec'],s['surv_dir'],s['lname'],s['start_ch'],s['end_ch'],s['lrp_code'],s['x'],s['y'])

        

        
    #is the section a roundabout?
    def is_roundabout(self, sec):#sec=section object
        sql = """SELECT funct_name 
                         FROM prog
                         WHERE sect_label = %s"""
        self.cur.execute(sql, (sec.label, ))
        try:
            row = self.cur.fetchone()[0]
        except:
            return False
        if row == 'RBT ':
            return True
        else:
            return False

    #returns true if single direction
    def is_single(self, sec):#sec=section object
        sql = """SELECT dual_name 
                         FROM prog
                         WHERE sect_label = %s"""
        self.cur.execute(sql, (sec.label, ))
        try:
            row = self.cur.fetchone()[0]
        except:
            return False
        if 'Two Way Single' in row:
            return True
        else:
            return False


#add dummys before and after roundabouts in list of sections
    def roundabout_dummys(self,sections):
        new_sections=[]
        for s in sections:
            
            if self.is_roundabout(s):
                new_sections.append(section(dummy=True))
                new_sections.append(s)
                new_sections.append(section(dummy=True))
                
            else:
                new_sections.append(s)
        
        return new_sections






    def r4_1(self,sec):
        q = """SELECT sect_label as label, 
        to_char(start_date, 'DD-Mon-YYYY') as start_date, 
        '' as end_date,
        sec_length as length, 
        direc_code as direction, 
        funct_name as function
        FROM prog
        WHERE sect_label=%s"""
        
        r=self.sql(q,sec)
        #section_label,start_date,end_date,section_len,direction,function
        self.rte.R4_1(r['label'],r['start_date'],r['end_date'],r['length'],r['direction'],r['function'])


#surveys need to start at start node and finish at end node. 

#for roundabouts there will be a dummy between end node of last section and start node of roundabout.
#another between end node of roundabout and start node of next section.

                
    #generate rte from list of section objects
    def make(self,sections,route_id):

        self.cur = self.con.cursor(cursor_factory = psycopg2.extras.DictCursor)
        
        new_sections=remove_consecutive(self.roundabout_dummys(sections))
        self.rte=rte()
        self.rte.R1_1(route_identifier=route_id,n_lanes=len(new_sections)-1)
        
        #remove dummys from start
        while new_sections[0].dummy:
            del new_sections[0]
        
            
        last_valid=section()
        
        for sec in new_sections:
            if sec.dummy:
                r=self.end_x_y(last_valid)
                self.rte.dummy_R2_1(r['end_marker'],r['end_marker_x'],r['end_marker_y'])
                #start node of dummy = end node of last.
                
            else:
                self.surv_line(sec)#
                last_valid=sec
        
        #route end record
        r=self.end_x_y(last_valid)
        self.rte.R3_1(r['end_marker'],r['end_marker_x'],r['end_marker_y'])
        
        new_sections.sort() #sort section in alphabetical order. Code works because section has __eq__ and __lt__ methods
        
        for sec in new_sections:
            if not sec.dummy:
                self.r4_1(sec)
        
        self.con.close()
        
        return True

            
    def save(self, rte_file):
        with open(rte_file, 'w') as f:
            f.write(self.rte.output())
        


class rte():

#text should be left justified, numbers right.
    def __init__(self):
        self.rows=[]


        # write R1.1-1 of these
    def R1_1(self,route_identifier,n_lanes,file_format_version='V1'):
        self.rows.insert(0,'ROUTE{:<8}{:<50}{:>5}'.format(file_format_version,route_identifier,n_lanes))


    #1 per survey lane. survey lane=section+direction?
    #direction like NB
    def R2_1(self,section_label,direction,lane_name,start_chainage,end_chainage,start_reference_label,start_x=None,start_y=None):
        #start_x and start_y are optional.
        self.check_direction(direction)
        self.rows.append('{:<30}{:<2}{:<20}{:>11.3f}{:>11.3f}{:<20}{:>10}{:>10}'.format(section_label,direction,lane_name,start_chainage,end_chainage,str(start_reference_label),to_format(start_x,'{:>11.3f}'),to_format(start_y,'{:>11.3f}')))


    #start node,x,y
    def dummy_R2_1(self,start_reference_label,start_x=None,start_y=None):
        #start_x and start_y are optional.
        self.rows.append('{:<30}{:<2}{:<20}{:>11.3f}{:>11.3f}{:<20}{:>10}{:>10}'.format('','','',0,0,start_reference_label,to_format(start_x,'{:>11.3f}'),to_format(start_y,'{:>11.3f}')))

    #1 end of route record
    def R3_1(self,end_ref,end_x,end_y):
        self.rows.append('{:<20}{:>10}{:>10}'.format(end_ref,to_format(end_x,'{:>11.3f}'),to_format(end_y,'{:>11.3f}')))


    # 1 per non dummy section in r2.1, sorted alphabetically by section label
    def R4_1(self,section_label,start_date,end_date,section_len,direction,function):
        self.check_direction(direction)
        self.rows.append('{:<30}{:<11}{:<11}{:>11.3f}{:<2}{:<4}'.format(section_label,start_date,end_date,section_len,direction,function))
        

    def check_direction(self,direction):
        directions=['NB','EB','SB','WB','CW','AC']
        if not direction in directions:
            raise ValueError('direction not in'+','.join(directions))


    def output(self):
        s=''
        for r in self.rows:
            s+=r+'\n'#each record terminated by carriage return and line feed characters. \n in python output as \r\n
        return s
    
#converts value val into format string form
#returns space if value is None
def to_format(val,form):
    if val:
        return form.format(val)
    else:
        return ' '

    #returns list of sections without same label and direction consecutively
def remove_consecutive(sections):
    last=sections[0]
    new_sections=[last]
        
    for sec in sections:
        if sec.label!=last.label or sec.reverse!=last.reverse:
            new_sections.append(sec)
        last=sec
            
    return new_sections

    
#sections=[section('2900A1/452'),section('2900A1/445'),section('2900A1/453'),section('2900A1/453')]
#m=database_to_rte(database='pts1944-01_he',host='192.168.5.157',user='stuart')
#print m.make(sections,route_id='test3.rte')
#print m.rte.output()
#p=r'C:\Users\drew.bennett\Documents\a.rte'
#m.save(p)

