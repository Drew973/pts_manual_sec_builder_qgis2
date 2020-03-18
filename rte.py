def R1_1(route_identifier,n_lanes,file_format_version='V1'):
    return'ROUTE{:<8}{:<50}{:>5}'.format(file_format_version,route_identifier,n_lanes)


def R2_1(section_label,direction,lane_name,start_chainage,end_chainage,start_reference_label,start_x,start_y):
    check_direction(direction)
    return '{:<30}{:<2}{:<20}{:>11.3f}{:>11.3f}{:<20}{:>11.3f}{:>11.3f}'.format(section_label,direction,lane_name,start_chainage,end_chainage,str(start_reference_label),start_x,start_y)


def dummy_R2_1(start_reference_label,start_x,start_y):
    return '{:<30}{:<2}{:<20}{:>11.3f}{:>11.3f}{:<20}{:>11.3f}{:>11.3f}'.format('','','',0,0,start_reference_label,start_x,start_y)


def R3_1(end_ref,end_x,end_y):
    return '{:<20}{:>11.3f}{:>11.3f}'.format(end_ref,end_x,end_y)


def R4_1(section_label,start_date,end_date,section_len,direction,function):
    check_direction(direction)
    return '{:<30}{:<11}{:<11}{:>11.3f}{:<2}{:<4}'.format(section_label,start_date,end_date,section_len,direction,function)


def check_direction(direction):
    directions=['NB','EB','SB','WB','CW','AC']
    if not direction in directions:
        raise ValueError('direction not in'+','.join(directions))
