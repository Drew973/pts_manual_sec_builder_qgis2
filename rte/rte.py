'''
functions for writing rte
#required: direction,section length,start_node,start_date,end_date,function
#optional: x,y of start nodes (use geometry?)
'''


def check_direction(direction):
    directions=['NB','EB','SB','WB','CW','AC']
    if not direction in directions:
        raise ValueError('direction not in'+','.join(directions))



OPPOSITES={'NB':'SB','EB':'WB','SB':'NB','WB':'EB','CW':'AC','AC':'CW','':''}#origonal code did CW':'CW','AC':'AC' but specification says CW opposite at AC


def opposite_direction(direction):
    return OPPOSITES[direction]



#1 of these
#route identifier=name. get from filename.
#new sec
#n_lanes=number of survey lanes. was number of items-1 in previous. why -1?      

def R1_1(route_identifier,n_lanes,file_format_version='V1'):
    return 'ROUTE{:<8}{:<50}{:>5}\n'.format(file_format_version,route_identifier,str(n_lanes))



#1 per survey lane. survey lane=section+direction?
#direction like NB
#lane_name='Lane 1'
#start_chainage=0
#end_chainage=section length
#start_reference_label=start node
#start_x,start y = x,y of start node(crs=27700) if known

def R2_1(section_label,direction,lane_name,start_chainage,end_chainage,start_reference_label,start_x=None,start_y=None):
    check_direction(direction)
    return '{:<30}{:<2}{:<20}{:>11.3f}{:>11.3f}{:<20}{:>10}{:>10}\n'.format(section_label,direction,lane_name,start_chainage,end_chainage,str(start_reference_label),to_format(start_x,'{:>11.3f}'),to_format(start_y,'{:>11.3f}'))


#start_x and start_y are optional.
def dummy_R2_1(start_reference_label,start_x=None,start_y=None):
    return '{:<30}{:<2}{:<20}{:>11.3f}{:>11.3f}{:<20}{:>10}{:>10}\n'.format('','','',0,0,start_reference_label,to_format(start_x,'{:>11.3f}'),to_format(start_y,'{:>11.3f}'))


#end of route record. 1 of these.
#end_ref=end node,x,y (crs=27700) if known        

def R3_1(end_ref,end_x,end_y):
    return '{:<20}{:>10}{:>10}\n'.format(end_ref,to_format(end_x,'{:>11.3f}'),to_format(end_y,'{:>11.3f}'))


# 1 per non dummy section in r2.1, sorted alphabetically by section label

def R4_1(section_label,start_date,end_date,section_len,direction,function):
    check_direction(direction)
    return'{:<30}{:<11}{:<11}{:>11.3f}{:<2}{:<4}\n'.format(section_label,start_date,end_date,section_len,direction,function)
        


#one of these for each section in rte

#direction in ['N','E','S','W','CW','AC']
#start_node,end_node,direction can be used to get if in reverse direction

class rte_item:
    def __init__(self,section_label,direction,section_len,start_node,end_node,start_date,end_date,function,lane_name='Lane 1',start_chainage=0,end_chainage=None,start_x=None,start_y=None,end_x=None,end_y=None):
        self.section_label = section_label
        self.direction = direction
        self.lane_name = lane_name
        self.start_chainage = start_chainage
        
        if end_chainage:
            self.end_chainage = end_chainage
        else:
            self.end_chainage = section_len

        self.section_len = section_len
        self.start_node = start_node
        self.end_node = end_node
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.start_date = start_date
        self.end_date = end_date
        self.function = function
        

    def R2_1(self):
        return R2_1(self.section_label,self.direction,self.lane_name,self.start_chainage,self.end_chainage,self.start_node,self.start_x,self.start_y)



    def R3_1(self):
        return R3_1(self.end_node,self.end_x,self.end_y)


    def R4_1(self):
        return R4_1(self.section_label,self.start_date,self.end_date,self.section_len,self.direction,self.function)


    def flip_direction(self):
        self.start_node,self.end_node = self.end_node,self.start_node #swap values
        self.start_x,self.start_y = self.start_y,self.start_x
        self.direction=opposite_direction(self.direction)
        #self.start_chainage,self.end_chainage = self.end_chainage,self.start_chainage     #start and end chainage were not swapped in previous. Mistake?



    def is_dummy(self):
        return False


#make dummy using start_node,start_x,start_y of this item
#start node of dummy = end node of last. 
    def make_dummy(self):
        return dummy(start_node=self.end_node,start_x=self.end_x,start_y=self.end_y)



#behaves like rte_item. Not actually subclass because don't want some methods.
    
class dummy:

    def __init__(self,start_node,start_x=None,start_y=None):
        self.start_node = start_node
        self.start_x = start_x
        self.start_y = start_y
        self.section_label = 'D'

    def R2_1(self):
        return '{:<30}{:<2}{:<20}{:>11.3f}{:>11.3f}{:<20}{:>10}{:>10}\n'.format('','','',0,0,self.start_node,to_format(self.start_x,'{:>11.3f}'),to_format(self.start_y,'{:>11.3f}'))


    def is_dummy(self):
        return True


    
    
#to=something with .write method.

       
def write_rte(rte_items,to,route_identifier):

    n_lanes=len([i for i in rte_items if not i.is_dummy()])
    to.write(R1_1(route_identifier=route_identifier,n_lanes=n_lanes))

    last_non_dummy=None
    
    for i in rte_items:
        to.write(i.R2_1())

        if not i.is_dummy():
            last_non_dummy=i
    
        
    #R3_1 for last last non dummy
    if not last_non_dummy:
        raise ValueError('Error writing rte: All dummys.')


    to.write(last_non_dummy.R3_1())


    for i in sorted(rte_items, key=lambda x: x.section_label):
        if not i.is_dummy():
            to.write(i.R4_1())



#converts value val into format string form
#returns space if value is None
def to_format(val,form):
    if val:
        return form.format(val)
    else:
        return ' '

    

    
