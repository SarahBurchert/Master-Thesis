# -*- coding: utf-8 -*-
"""
@author: Sarah Burchert

"""

import csv

###################################################
############ Reading Functions ####################
###################################################

def read_betriebsstellen(betriebsstellen_datei, stops):
    with open(betriebsstellen_datei) as csvdatei:
        csv_reader_object = csv.reader(csvdatei, delimiter=',')
        zeilennummer = 1
        for row in csv_reader_object:
            if zeilennummer <= 7:
                zeilennummer += 1
            else:
                stop_abbreviation = row[0]
                stop_longname = row[2]
                stop_transfer = row[5]
                stop_x = row[3]
                stop_y = row[4]
                stops[stop_abbreviation]=[stop_longname, stop_transfer, [], {"S":{},"N":{},"W":{},"O":{}}, 'n', stop_x, stop_y]
                
                zeilennummer += 1
            
                
def read_regelfahrplan(regelfahrplan_datei, regelfahrplan, k, stops, edges, lines, fe_min, fe_max):
    with open(regelfahrplan_datei) as csvdatei:
        csv_reader_object = csv.reader(csvdatei, delimiter=',')
        zeilennummer = 1
        for row in csv_reader_object:
            if zeilennummer <= 1:
                zeilennummer += 1
                
            # here row 2
            elif zeilennummer == 2: 
                zeilennummer += 1
                
                line_nummer_2 = row[0]
                line_zuggruppe_2 = row[1]
                line_start = row[2]
                line_end = row[3]
                line_stop_2 = row[4]
                ankunft = row[5]
                direction = row[10]
                endstelle = row[11]
                
                line_2 = (line_nummer_2, line_zuggruppe_2)
                line_richtung_2 = (line_nummer_2, line_zuggruppe_2, line_start , line_end )
                
                #in stops: fill list of lines 
                if line_stop_2 not in stops:
                    print('Warning: stop ' + str(line_stop_2) + ' in line ' + str(line_nummer_2) +' is not in stops')
                if line_2 not in stops[line_stop_2][2]:
                    stops[line_stop_2][2].append(line_2)
                    
                # in stops: for corresponding direction fill list of lines
                if direction !='' and line_2 not in stops[line_stop_2][3][direction]:
                    stops[line_stop_2][3][direction][line_2] = line_richtung_2
           
                #  fill Regelfahrplan
                if line_2 not in regelfahrplan:
                    regelfahrplan[line_2]={}
                    regelfahrplan[line_2][line_richtung_2]={}
                    regelfahrplan[line_2][line_richtung_2][line_stop_2]={'arr': [], 'dep': []}
                if ankunft == '1':
                    haltezeit = row[8]
                    if haltezeit == '':
                        haltezeit = -1
                    else:
                        haltezeit = int(float(row[8])*k)
                    timetable = int(float(row[9])*k)
                    regelfahrplan[line_2][line_richtung_2][line_stop_2]['arr'] = [timetable, haltezeit]
                if ankunft == '0':
                    fahrzeit = int(float(row[7])*k)
                    timetable = int(float(row[9])*k)
                    regelfahrplan[line_2][line_richtung_2][line_stop_2]['dep'] = [timetable, fahrzeit]  
                    
                # in lines : fill direction of line with last stop
                if line_2 not in lines:
                    lines[line_2]={}
                    lines[line_2][line_richtung_2]=[1, {line_stop_2: endstelle}, []]
                    
            # here row 3 and further rows
            else:
                line_stop_1 = line_stop_2
                line_richtung_1 = line_richtung_2
          
                line_nummer_2 = row[0]
                line_zuggruppe_2 = row[1]
                line_start = row[2]
                line_end = row[3]
                line_stop_2 = row[4]
                ankunft = row[5]
                direction = row[10]
                endstelle = row[11]
                
                line_2 = (line_nummer_2, line_zuggruppe_2)
                line_richtung_2 = (line_nummer_2, line_zuggruppe_2, line_start , line_end )
               
                #in stops: fill list of lines
                if line_stop_2 not in stops:
                    print('Warning: stop ' + str(line_stop_2) + ' in line ' + str(line_nummer_2) +' is not in stops')
                if line_2 not in stops[line_stop_2][2]:
                    stops[line_stop_2][2].append(line_2)

                # in stops: for corresponding direction fill list of lines
                if direction !='' and line_2 not in stops[line_stop_2][3][direction]:
                    stops[line_stop_2][3][direction][line_2] = line_richtung_2

        
                # fill Regelfahrplan 
                if line_2 not in regelfahrplan:
                    regelfahrplan[line_2]={}
                    regelfahrplan[line_2][line_richtung_2]={}
                    regelfahrplan[line_2][line_richtung_2][line_stop_2]={'arr': [], 'dep': []}
                if line_richtung_2 not in regelfahrplan[line_2]:
                    regelfahrplan[line_2][line_richtung_2]={}
                    regelfahrplan[line_2][line_richtung_2][line_stop_2]={'arr': [], 'dep': []}
                if line_stop_2 not in regelfahrplan[line_2][line_richtung_2]:
                    regelfahrplan[line_2][line_richtung_2][line_stop_2]={'arr': [], 'dep': []}
                    
                if ankunft == '1':
                    haltezeit = row[8]
                    if haltezeit == '':
                        haltezeit = -1
                    else:
                        haltezeit = int(float(row[8])*k)
                    timetable = int(float(row[9])*k)
                    regelfahrplan[line_2][line_richtung_2][line_stop_2]['arr'] = [timetable, haltezeit]
                if ankunft == '0':
                    fahrzeit = int(float(row[7])*k)
                    timetable = int(float(row[9])*k)
                    regelfahrplan[line_2][line_richtung_2][line_stop_2]['dep'] = [timetable, fahrzeit]  
                
                # fill lines
                if line_2 not in lines:
                    lines[line_2]={}
                    lines[line_2][line_richtung_2]=[1, {line_stop_2: endstelle}, []]
                elif line_richtung_2 not in lines[line_2]:
                    lines[line_2][line_richtung_2]=[1, {line_stop_2: endstelle}, []]
                else:           
                    lines[line_2][line_richtung_2][1][line_stop_2]=endstelle
                    
                # in edges: fill driving time
                # in lines: fill list of edges
                if line_richtung_1 == line_richtung_2 and line_stop_1 != line_stop_2:
                    if ankunft != '1':
                        print('Warning: There is an error in regelfahrplan!')
                    edge = (line_stop_1, line_stop_2)
                    longname_edge=(stops[line_stop_1][0], stops[line_stop_2][0])
                    if edge not in edges:
                        edges[edge]=[longname_edge, 'n', {}, fe_min,fe_max]
                    edges[edge][2][line_richtung_2] = fahrzeit
                    lines[line_2][line_richtung_2][2].append((line_stop_1,line_stop_2))
                zeilennummer += 1
                
                
                
def read_line_alternatives(linienalternativen_datei, line_alternatives, k, stops, edges, fe_min, fe_max):
    with open(linienalternativen_datei) as csvdatei:
        csv_reader_object = csv.reader(csvdatei, delimiter=',')
        zeilennummer = 1
        for row in csv_reader_object:
            if zeilennummer <= 1:
                zeilennummer += 1
                
            # here for row 2
            elif zeilennummer == 2: 
                zeilennummer += 1
                
                line_nummer_2 = row[0]
                line_zuggruppe_2 = row[1]
                line_start = row[2]
                line_end = row[3]
                line_stop_2 = row[4]
                ankunft = row[5]
                line_alternative_nummer = row[6]
                direction = row[10]
                endstelle = row[11]
                
                line_2 = (line_nummer_2, line_zuggruppe_2)
                line_richtung_2 = (line_nummer_2, line_zuggruppe_2, line_alternative_nummer, line_start , line_end )
                line_original_richtung_2 = (line_nummer_2, line_zuggruppe_2, line_start , line_end )
                linienalternative_2 = (line_nummer_2, line_zuggruppe_2, line_alternative_nummer)
                
                if ankunft == '0':
                    fahrzeit = int(float(row[7])*k)
                
                # in stops: set stop active
                stops[line_stop_2][4]='y'
                
                # in stops: fill list of lines 
                if line_2 not in stops[line_stop_2][2]:
                    stops[line_stop_2][2].append(line_2)
                    
                # in stops: for corresponding direction fill list of lines
                if direction !='' and line_2 not in stops[line_stop_2][3][direction]:
                    stops[line_stop_2][3][direction][line_2] = line_original_richtung_2
           
                # fill line_alternatives
                if line_2 not in line_alternatives:
                    line_alternatives[line_2]={}
                    line_alternatives[line_2][linienalternative_2]=[1, {}]
                    line_alternatives[line_2][linienalternative_2][1][line_richtung_2]=[{line_stop_2: endstelle}, []]
            
            # here row 3 and further rows
            else:
                line_stop_1 = line_stop_2
                linienalternative_1 = linienalternative_2
          
                line_nummer_2 = row[0]
                line_zuggruppe_2 = row[1]
                line_start = row[2]
                line_end = row[3]
                line_stop_2 = row[4]
                ankunft = row[5]
                line_alternative_nummer = row[6]
                direction = row[10]
                endstelle = row[11]
                
                line_2 = (line_nummer_2, line_zuggruppe_2)
                line_richtung_2 = (line_nummer_2, line_zuggruppe_2, line_alternative_nummer, line_start , line_end )
                line_original_richtung_2 = (line_nummer_2, line_zuggruppe_2, line_start , line_end )
                linienalternative_2 = (line_nummer_2, line_zuggruppe_2, line_alternative_nummer)
                
                if ankunft == '0':
                    fahrzeit = int(float(row[7])*k)
               
                # in stops: set stop active
                stops[line_stop_2][4]='y' 
                
                # in stops: fill list of lines
                if line_2 not in stops[line_stop_2][2]:
                    stops[line_stop_2][2].append(line_2)

                # in stops: for corresponding direction fill list of lines
                if direction !='' and line_2 not in stops[line_stop_2][3][direction]:
                    stops[line_stop_2][3][direction][line_2] = line_original_richtung_2
    
                # fill line_alternatives
                if line_2 not in line_alternatives:
                    line_alternatives[line_2]={}
                    line_alternatives[line_2][linienalternative_2]=[1, {}]
                    line_alternatives[line_2][linienalternative_2][1][line_richtung_2]=[{line_stop_2: endstelle}, []]
                elif linienalternative_2 not in line_alternatives[line_2]:
                    line_alternatives[line_2][linienalternative_2]=[1, {}]
                    line_alternatives[line_2][linienalternative_2][1][line_richtung_2]=[{line_stop_2: endstelle}, []]
                elif line_richtung_2 not in line_alternatives[line_2][linienalternative_2][1]:
                    line_alternatives[line_2][linienalternative_2][1][line_richtung_2]=[{line_stop_2: endstelle}, []]
                else:           
                    line_alternatives[line_2][linienalternative_2][1][line_richtung_2][0][line_stop_2] = endstelle
                
                # in edges: fill driving time and set edges active
                # in line_alternatives: fill edges and in line_alternatives fill list of edges
                if linienalternative_1 == linienalternative_2 and line_stop_1 != line_stop_2:
                    if ankunft != '1':
                        print('Warning: There is an error in regelfahrplan!')
                    edge = (line_stop_1, line_stop_2)
                    longname_edge=(stops[line_stop_1][0], stops[line_stop_2][0])
                    if edge not in edges:
                        edges[edge]=[longname_edge, 'y', {}, fe_min,fe_max]
                    edges[edge][1]='y'
                    edges[edge][2][line_richtung_2] = fahrzeit
                    line_alternatives[line_2][linienalternative_2][1][line_richtung_2][1].append((line_stop_1, line_stop_2))
                zeilennummer += 1
                
def read_linecosts(linecosts_datei, line_alternatives):
    with open(linecosts_datei) as csvdatei:
        csv_reader_object = csv.reader(csvdatei, delimiter=',')
        for row in csv_reader_object:
            line_nummer= row[0]
            line_zuggruppe=row[1]
            line_alternative_nummer = row[2]
            line_cost = row[3]
            line = (line_nummer, line_zuggruppe)
            line_alternative = (line_nummer, line_zuggruppe, line_alternative_nummer)
            line_alternatives[line][line_alternative][0]=line_cost

def read_linecost_attributes(linecosts_datei, line_alternatives, alphac, betac):
    with open(linecosts_datei) as csvdatei:
        csv_reader_object = csv.reader(csvdatei, delimiter=',')
        for row in csv_reader_object:
            line_nummer= row[0]
            line_zuggruppe=row[1]
            line_alternative_nummer = row[2]
            line_cost_w2 = float(row[3])
            line_cost_w1 = float(row[4])
            line_cost_drive_time = float(row[5])
            line = (line_nummer, line_zuggruppe)
            line_alternative = (line_nummer, line_zuggruppe, line_alternative_nummer)
            line_cost = alphac * line_cost_drive_time - betac * (2*line_cost_w2 + line_cost_w1)
            line_alternatives[line][line_alternative][0]=line_cost
                

            
###################################################
############ Creating EAN #########################
###################################################

def create_EAN(events, activities, line_alternatives, lines, stops, regelfahrplan, w_drive, edges, fahrzeit_puffer, w_wait, La_wait, Ua_wait, La_wende, Ua_wende, w_wende, La_trans, Ua_trans, w_trans, h, w_headway, T):
    create_events_line_alternatives(events, line_alternatives)
    create_events_fixed_lines(events, lines, stops, line_alternatives, regelfahrplan)
    create_driving_activities_line_alternatives(events, activities, line_alternatives, w_drive, edges, fahrzeit_puffer)
    create_waiting_activities_line_alternatives(events, activities, line_alternatives, w_wait, La_wait, Ua_wait)
    create_wende_activities_line_alternatives(events, activities, line_alternatives, La_wende, Ua_wende, w_wende)
    create_trans_activities(events, activities, line_alternatives, stops, lines, La_trans, Ua_trans, w_trans)
    create_headway_activities(events, activities, line_alternatives, stops, lines, h, w_headway, T)
    


def create_events_line_alternatives(events, line_alternatives):
    for line in line_alternatives:
        for line_alternative in line_alternatives[line]:
            for line_richtung in line_alternatives[line][line_alternative][1]:
                line_original_richtung = (line_richtung[0], line_richtung[1], line_richtung[3], line_richtung[4])
                list_of_stops = line_alternatives[line][line_alternative][1][line_richtung][0]
                for stop in list_of_stops:
                    endstelle = line_alternatives[line][line_alternative][1][line_richtung][0][stop]
                    if endstelle == '':
                        create_arr_event(events, stop, line, line_original_richtung)
                        create_dep_event(events, stop, line, line_original_richtung)
                    elif endstelle == 'start':
                        create_dep_event(events, stop, line, line_original_richtung)
                    elif endstelle == 'end':
                        create_arr_event(events, stop, line, line_original_richtung)
                    else: 
                        print('Warning: Problem with create_events_line_alternatives')

def create_events_fixed_lines(events, lines, stops, line_alternatives, regelfahrplan):
    list_of_fixed_lines = get_list_of_fixed_lines(lines, line_alternatives)
    list_of_active_stops = get_list_of_active_stops(stops)
    for stop in list_of_active_stops:
        list_of_lines_at_stop = stops[stop][2]
        for line in list_of_lines_at_stop:
            if line in list_of_fixed_lines:
                for line_richtung in lines[line]:
                    # check if for corresponding line, there is a timetable-time for arr/dep of the stop (Example: At last stop of line is only arr or dep not both)
                    if regelfahrplan[line][line_richtung][stop]['arr'] != []:
                        arr_event = create_arr_event(events, stop, line, line_richtung)
                        set_event_fixed(events, arr_event)
                        arr_event_time = regelfahrplan[line][line_richtung][stop]['arr'][0]
                        set_event_time(events, arr_event, arr_event_time)
                    if regelfahrplan[line][line_richtung][stop]['dep'] != []:
                        dep_event = create_dep_event(events, stop, line, line_richtung)
                        set_event_fixed(events, dep_event)
                        dep_event_time = regelfahrplan[line][line_richtung][stop]['dep'][0]
                        set_event_time(events, dep_event, dep_event_time)
                        
def create_waiting_activities_line_alternatives(events, activities, line_alternatives, w_wait, La_wait, Ua_wait):
    for line in line_alternatives:
        for line_alternative in line_alternatives[line]:
            for line_richtung in line_alternatives[line][line_alternative][1]:
                line_original_richtung = (line_richtung[0], line_richtung[1], line_richtung[3], line_richtung[4])
                list_of_stops =  line_alternatives[line][line_alternative][1][line_richtung][0]
                for stop in list_of_stops:
                    stop_endstelle = line_alternatives[line][line_alternative][1][line_richtung][0][stop]
                    if stop_endstelle == '':
                        event_1 =(stop, 'arr', line, line_original_richtung)
                        event_2 = (stop, 'dep', line, line_original_richtung)
                        if event_1 not in events or event_2 not in events:
                            print('Warning: event for waiting activity does not exist')
                        create_waiting_activity(activities, event_1, event_2, La_wait, Ua_wait, w_wait)
                        
def create_driving_activities_line_alternatives(events, activities, line_alternatives, w_drive, edges, fahrzeit_puffer):
    for line in line_alternatives:
        for line_alternative in line_alternatives[line]:
            for line_richtung in line_alternatives[line][line_alternative][1]:
                line_original_richtung = (line_richtung[0], line_richtung[1], line_richtung[3], line_richtung[4])
                list_of_edges = line_alternatives[line][line_alternative][1][line_richtung][1] 
                for edge in list_of_edges:
                    stop_1 = edge[0]
                    stop_2 = edge[1]
                    event_1 = (stop_1, 'dep', line, line_original_richtung)
                    event_2 = (stop_2, 'arr', line, line_original_richtung)
                    if event_1 not in events or event_2 not in events:
                        print('Warning: event for driving activity does not exist')
                    La = edges[edge][2][line_richtung] # ist fahrzeit
                    Ua = La + fahrzeit_puffer
                    create_driving_activity(activities, event_1, event_2, La, Ua, w_drive)
                    
def create_wende_activities_line_alternatives(events, activities, line_alternatives, La_wende, Ua_wende, w_wende):
    for line in line_alternatives:
        for line_alternative in line_alternatives[line]:
            for line_richtung_1 in line_alternatives[line][line_alternative][1]:
                line_original_richtung_1 = (line_richtung_1[0], line_richtung_1[1], line_richtung_1[3], line_richtung_1[4])
                for line_richtung_2 in line_alternatives[line][line_alternative][1]:
                    line_original_richtung_2 = (line_richtung_2[0], line_richtung_2[1], line_richtung_2[3], line_richtung_2[4])
                    if line_richtung_1 != line_richtung_2:
                        list_of_stops_1 = line_alternatives[line][line_alternative][1][line_richtung_1][0]
                        list_of_stops_2 = line_alternatives[line][line_alternative][1][line_richtung_2][0]
                        start_stop_1 = ''
                        start_stop_2 = ''
                        end_stop_1 = ''
                        end_stop_2 = ''
                        for stop in list_of_stops_1:
                            stop_endstelle = line_alternatives[line][line_alternative][1][line_richtung_1][0][stop]
                            if stop_endstelle == 'start':
                                start_stop_1 = stop
                            elif stop_endstelle == 'end':
                                end_stop_1 = stop
                        for stop in list_of_stops_2:
                            stop_endstelle = line_alternatives[line][line_alternative][1][line_richtung_2][0][stop]
                            if stop_endstelle == 'start':
                                start_stop_2 = stop
                            elif stop_endstelle == 'end':
                                end_stop_2 = stop
                        event_1 = (start_stop_1, 'dep', line, line_original_richtung_1)
                        event_2 = (end_stop_2, 'arr', line, line_original_richtung_2)
                        event_3 = (start_stop_2, 'dep', line, line_original_richtung_2)
                        event_4 = (end_stop_1, 'arr', line, line_original_richtung_1)
                        if event_1 not in events or event_2 not in events or event_3 not in events or event_4 not in events:
                            print('Warning: event for wende activity does not exist')
                        create_wende_activity(activities, event_2, event_1, La_wende, Ua_wende, w_wende)
                        create_wende_activity(activities, event_4, event_3, La_wende, Ua_wende, w_wende)
                        
def create_trans_activities(events, activities, line_alternatives, stops, lines, La_trans, Ua_trans, w_trans):
    list_of_transfer_stops = get_list_of_transfer_stops(stops)
    for stop in list_of_transfer_stops:
        list_of_lines = stops[stop][2]
        for line_1 in list_of_lines:
            if line_1 in line_alternatives:
                line_1_nummer = line_1[0]
                for line_2 in list_of_lines:
                    line_2_nummer = line_2[0]
                    if line_1_nummer != line_2_nummer:
                        # here are two lines, line 1 is line alternative and
                        # the other line does not belong to the same line number (important for S41)
                        for line_1_richtung in lines[line_1]:
                            for line_2_richtung in lines[line_2]:
                                event_1 = (stop, 'arr', line_1, line_1_richtung)
                                event_2 = (stop, 'dep', line_2, line_2_richtung)
                                event_3 = (stop, 'arr', line_2, line_2_richtung)
                                event_4 = (stop, 'dep', line_1, line_1_richtung)
                                if event_1 in events and event_2 in events:
                                    create_transfer_activity(activities, event_1, event_2, La_trans, Ua_trans, w_trans)
                                if event_3 in events and event_4 in events:
                                    create_transfer_activity(activities, event_3, event_4, La_trans, Ua_trans, w_trans)
                                    
def create_headway_activities(events, activities, line_alternatives, stops, lines, h, w_headway, T):
    list_of_active_stops = get_list_of_active_stops(stops)
    for stop in list_of_active_stops:
        directions = ['W', 'O', 'S', 'N']
        for direction in directions:
            list_of_lines = stops[stop][3][direction]
            for line_1 in list_of_lines:
                if line_1 in line_alternatives:
                    line_1_original_richtung = list_of_lines[line_1]
                    for line_2 in list_of_lines:
                        if line_1 != line_2:
                            line_2_original_richtung = list_of_lines[line_2]
                            event_1 = (stop, 'arr', line_1, line_1_original_richtung)
                            event_2 = (stop, 'dep', line_1, line_1_original_richtung)
                            event_3 = (stop, 'arr', line_2, line_2_original_richtung)
                            event_4 = (stop, 'dep', line_2, line_2_original_richtung)
                            if event_1 in events and event_3 in events and (event_3, event_1) not in activities:
                                create_headway_activity(activities, event_1, event_3, h, T-h, w_headway)
                            if event_2 in events and event_4 in events and (event_4, event_2) not in activities:
                                create_headway_activity(activities, event_2, event_4, h, T-h, w_headway)

def create_arr_event(events, stop, line, line_richtung):
    event = (stop, 'arr', line, line_richtung)
    events[event]=['n', -1]
    return(event)
    
def create_dep_event(events, stop, line, line_richtung):
    event = (stop, 'dep', line, line_richtung)
    events[event]=['n', -1]
    return(event)

def create_waiting_activity(activities, event_1, event_2, La, Ua, wa):
    activity = (event_1, event_2)
    activities[activity]=[La, Ua, wa, 'wait']

def create_driving_activity(activities, event_1, event_2, La, Ua, wa):
    activity = (event_1, event_2)
    activities[activity]=[La, Ua, wa, 'drive']

def create_wende_activity(activities, event_1, event_2, La, Ua, wa):
    activity = (event_1, event_2)
    activities[activity]=[La, Ua, wa, 'wende']
    
def create_transfer_activity(activities, event_1, event_2, La, Ua, wa):
    activity = (event_1, event_2)
    activities[activity]=[La, Ua, wa, 'trans']

def create_headway_activity(activities, event_1, event_2, La, Ua, wa):
    activity = (event_1, event_2)
    activities[activity]=[La, Ua, wa, 'headway']




###################################################          
########### Set Functions #########################
###################################################

def set_edges_of_liste_inactive(edges, liste):
    for edge in liste:
        edges[edge][1]='n'

def set_event_fixed(events, event):
    events[event][0]='y'

def set_event_time(events, event, time):
    events[event][1]=time


###################################################          
########### Get Functions #########################
###################################################

def get_list_of_line_alternatives(line_alternatives):
    list_of_line_alternatives =[]
    for line in line_alternatives:
        for line_alternative in line_alternatives[line]:
            list_of_line_alternatives.append(line_alternative)
    return(list_of_line_alternatives)

def get_list_of_fixed_lines(lines, line_alternatives):
    list_of_fixed_lines=[]
    for line in lines:
        if line not in line_alternatives:
            list_of_fixed_lines.append(line)
    return(list_of_fixed_lines)

def get_list_of_active_edges(edges):
    list_of_active_edges=[]
    for edge in edges:
        if edges[edge][1]== 'y':
            list_of_active_edges.append(edge)
    return(list_of_active_edges)

def get_list_of_active_stops(stops):
    list_of_active_stops=[]
    for stop in stops:
        if stops[stop][4] == 'y':
            list_of_active_stops.append(stop)
    return(list_of_active_stops)

def get_list_of_transfer_stops(stops):
    list_of_transfer_stops=[]
    for stop in stops:
        if stops[stop][1] == 'y':
            list_of_transfer_stops.append(stop)
    return(list_of_transfer_stops)

def get_list_of_fixed_events(events):
    list_of_fixed_events=[]
    for event in events:
        event_active = events[event][0]
        if event_active == 'y':
            list_of_fixed_events.append(event)
    return(list_of_fixed_events)

def get_list_of_not_fixed_events(events):
    list_of_not_fixed_events=[]
    for event in events:
        event_active = events[event][0]
        if event_active == 'n':
            list_of_not_fixed_events.append(event)
    return(list_of_not_fixed_events)

def get_list_of_wait_activities(activities):
    list_of_wait_activities=[]
    for activity in activities:
        activity_type = activities[activity][3]
        if activity_type == 'wait':
            list_of_wait_activities.append(activity)
    return(list_of_wait_activities)

def get_list_of_drive_activities(activities):
    list_of_drive_activities=[]
    for activity in activities:
        activity_type = activities[activity][3]
        if activity_type == 'drive':
            list_of_drive_activities.append(activity)
    return(list_of_drive_activities)

def get_list_of_wende_activities(activities):
    list_of_wende_activities=[]
    for activity in activities:
        activity_type = activities[activity][3]
        if activity_type == 'wende':
            list_of_wende_activities.append(activity)
    return(list_of_wende_activities)

def get_list_of_trans_activities(activities):
    list_of_trans_activities=[]
    for activity in activities:
        activity_type = activities[activity][3]
        if activity_type == 'trans':
            list_of_trans_activities.append(activity)
    return(list_of_trans_activities)

def get_list_of_headway_activities(activities):
    list_of_headway_activities=[]
    for activity in activities:
        activity_type = activities[activity][3]
        if activity_type == 'headway':
            list_of_headway_activities.append(activity)
    return(list_of_headway_activities)

def get_list_of_wait_drive_wende_activities(activities):
    list_of_wdw_activities=[]
    for activity in activities:
        activity_type = activities[activity][3]
        if activity_type == 'wait' or activity_type == 'drive' or activity_type == 'wende':
            list_of_wdw_activities.append(activity)
    return(list_of_wdw_activities)

def get_list_of_all_activities(activities):
    list_of_activities=[]
    for activity in activities:
        list_of_activities.append(activity)
    return(list_of_activities)

def get_list_of_wait_activities_for_line_alternative(line_alternative, activities, line_alternatives):
    list_of_wait_activities_for_line_alternative = []
    list_of_wait_activities = get_list_of_wait_activities(activities)
    
    line = (line_alternative[0], line_alternative[1])
    
    for activity in list_of_wait_activities:
        event_1 = activity[0]
        stop_1 = event_1[0]
        activity_line = event_1[2]
        activity_line_richtung = event_1[3]
        line_richtung = (line_alternative[0], line_alternative[1], line_alternative[2], activity_line_richtung[2], activity_line_richtung[3])
        if activity_line == line:
            list_of_stops = line_alternatives[line][line_alternative][1][line_richtung][0]
            if stop_1 in list_of_stops:
                endstelle = line_alternatives[line][line_alternative][1][line_richtung][0][stop_1]
                if endstelle == '':
                    list_of_wait_activities_for_line_alternative.append(activity)
    return(list_of_wait_activities_for_line_alternative)

def get_list_of_wende_activities_for_line_alternative(line_alternative, activities, line_alternatives):
    list_of_wende_activities_for_line_alternative = []
    list_of_wende_activities = get_list_of_wende_activities(activities)
    
    line = (line_alternative[0], line_alternative[1])
    
    for activity in list_of_wende_activities:
        event_1 = activity[0]
        stop_1 = event_1[0]
        activity_line = event_1[2]
        activity_line_richtung = event_1[3]
        line_richtung = (line_alternative[0], line_alternative[1], line_alternative[2], activity_line_richtung[2], activity_line_richtung[3])
        if activity_line == line:
            list_of_stops = line_alternatives[line][line_alternative][1][line_richtung][0]
            if stop_1 in list_of_stops:
                endstelle = line_alternatives[line][line_alternative][1][line_richtung][0][stop_1]
                if endstelle == 'end':
                    list_of_wende_activities_for_line_alternative.append(activity)
    return(list_of_wende_activities_for_line_alternative)

def get_list_of_drive_activities_for_line_alternative(line_alternative, activities, line_alternatives):
    list_of_drive_activities_for_line_alternative = []
    list_of_drive_activities = get_list_of_drive_activities(activities)
    
    line = (line_alternative[0], line_alternative[1])
    
    for activity in list_of_drive_activities:
        event_1 = activity[0]
        event_2 = activity[1]
        stop_1 = event_1[0]
        stop_2 = event_2[0]
        edge = (stop_1, stop_2)
        activity_line = event_1[2]
        activity_line_richtung = event_1[3]
        line_richtung = (line_alternative[0], line_alternative[1], line_alternative[2], activity_line_richtung[2], activity_line_richtung[3])
        if activity_line == line:
            list_of_edges = line_alternatives[line][line_alternative][1][line_richtung][1]
            if edge in list_of_edges:
                list_of_drive_activities_for_line_alternative.append(activity)
    return(list_of_drive_activities_for_line_alternative)

def get_list_of_trans_activities_for_line_alternative(line_alternative, activities, line_alternatives):
    list_of_trans_activities_for_line_alternative = []
    list_of_trans_activities = get_list_of_trans_activities(activities)
    
    line = (line_alternative[0], line_alternative[1])
    
    for activity in list_of_trans_activities:
        event_1 = activity[0]
        event_2 = activity[1]
        stop_1 = event_1[0]
        stop_2 = event_2[0]
        activity_line_1 = event_1[2]
        activity_line_2 = event_2[2]
        activity_line_1_richtung = event_1[3]
        activity_line_2_richtung = event_2[3]
        line_richtung_1 = (line_alternative[0], line_alternative[1], line_alternative[2], activity_line_1_richtung[2], activity_line_1_richtung[3])
        line_richtung_2 = (line_alternative[0], line_alternative[1], line_alternative[2], activity_line_2_richtung[2], activity_line_2_richtung[3])
        if activity_line_1 == line:
            list_of_stops = line_alternatives[line][line_alternative][1][line_richtung_1][0]
            if stop_1 in list_of_stops:
                endstelle = line_alternatives[line][line_alternative][1][line_richtung_1][0][stop_1]
                if endstelle != 'start':
                    list_of_trans_activities_for_line_alternative.append(activity)
        if activity_line_2 == line:
            list_of_stops = line_alternatives[line][line_alternative][1][line_richtung_2][0]
            if stop_2 in list_of_stops:
                endstelle = line_alternatives[line][line_alternative][1][line_richtung_2][0][stop_2]
                if endstelle != 'end':
                    list_of_trans_activities_for_line_alternative.append(activity)
    return(list_of_trans_activities_for_line_alternative)

def get_list_of_headway_activities_for_line_alternative(line_alternative, activities, line_alternatives):
    list_of_head_activities_for_line_alternative = []
    list_of_head_activities = get_list_of_headway_activities(activities)
    
    line = (line_alternative[0], line_alternative[1])
    
    for activity in list_of_head_activities:
          event_1 = activity[0]
          event_2 = activity[1]
          stop_1 = event_1[0]
          stop_2 = event_2[0]
          ankunft_1 = event_1[1]
          ankunft_2 = event_2[1]
          activity_line_1 = event_1[2]
          activity_line_2 = event_2[2]
          activity_line_1_richtung = event_1[3]
          activity_line_2_richtung = event_2[3]
          line_richtung_1 = (line_alternative[0], line_alternative[1], line_alternative[2], activity_line_1_richtung[2], activity_line_1_richtung[3])
          line_richtung_2 = (line_alternative[0], line_alternative[1], line_alternative[2], activity_line_2_richtung[2], activity_line_2_richtung[3])
          if activity_line_1 == line:
              list_of_stops = line_alternatives[line][line_alternative][1][line_richtung_1][0]
              if stop_1 in list_of_stops:
                  endstelle = line_alternatives[line][line_alternative][1][line_richtung_1][0][stop_1]
                  if endstelle == '':
                      list_of_head_activities_for_line_alternative.append(activity)
                  elif endstelle == 'start' and ankunft_1 == 'dep':
                      list_of_head_activities_for_line_alternative.append(activity)
                  elif endstelle == 'end' and ankunft_1 == 'arr':
                      list_of_head_activities_for_line_alternative.append(activity)
          if activity_line_2 == line:
              list_of_stops = line_alternatives[line][line_alternative][1][line_richtung_2][0]
              if stop_2 in list_of_stops:
                  endstelle = line_alternatives[line][line_alternative][1][line_richtung_2][0][stop_2]
                  if endstelle == '':
                      list_of_head_activities_for_line_alternative.append(activity)
                  elif endstelle == 'start' and ankunft_2 == 'dep':
                      list_of_head_activities_for_line_alternative.append(activity)
                  elif endstelle == 'end' and ankunft_2 == 'arr':
                      list_of_head_activities_for_line_alternative.append(activity)
    return(list_of_head_activities_for_line_alternative)

    
###################################################          
########### Writing Functions #####################
###################################################

def write_stops(stops):
    with open('write_all_stops.csv', 'w', newline='') as f:
         writer = csv.writer(f)
         for stop in stops:
             longname = stops[stop][0]
             transfer = stops[stop][1]
             line_list = stops[stop][2]
             W= stops[stop][3]['W']
             O= stops[stop][3]['O']
             N= stops[stop][3]['N']
             S= stops[stop][3]['S']
             active = stops[stop][4]
             writer.writerow([stop, longname, transfer, active, line_list,  W, O, N, S])

def write_edges(edges):
    with open('write_all_edges.csv', 'w', newline='') as f:
         writer = csv.writer(f)
         for edge in edges:
             longname_edge=edges[edge][0]
             f_min=edges[edge][3]
             f_max=edges[edge][4]
             active=edges[edge][1]
             fahrzeit=edges[edge][2]             
             writer.writerow([edge, longname_edge, active, fahrzeit,  f_min, f_max,])

def write_lines(lines):
    for line in lines:
        with open('write_line_'+str(line)+'.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for line_richtung in lines[line]:
                cost_line = lines[line][line_richtung][0]
                list_of_stops = lines[line][line_richtung][1]
                list_of_edges = lines[line][line_richtung][2]
                writer.writerow([line, line_richtung, cost_line, list_of_stops, list_of_edges])

def write_regelfahrplan(regelfahrplan):
    for line in regelfahrplan:
        for line_richtung in regelfahrplan[line]:
            with open('write_Timetable_'+str(line_richtung)+'.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                for stop in regelfahrplan[line][line_richtung]:
                    if regelfahrplan[line][line_richtung][stop]['arr'] != []:
                        timetable_arr = regelfahrplan[line][line_richtung][stop]['arr'][0]
                        if regelfahrplan[line][line_richtung][stop]['arr'][1] != -1:
                            haltezeit = regelfahrplan[line][line_richtung][stop]['arr'][1]
                        else: 
                            haltezeit = ""
                    else:
                        timetable_arr = ""
                        haltezeit = ""
                    if regelfahrplan[line][line_richtung][stop]['dep'] != []:
                        timetable_dep = regelfahrplan[line][line_richtung][stop]['dep'][0]
                        fahrzeit = regelfahrplan[line][line_richtung][stop]['dep'][1]
                    else:
                        timetable_dep = ""
                        fahrzeit = ""
                    writer.writerow([stop, 'arr', timetable_arr, haltezeit, 'dep', timetable_dep, fahrzeit])
 
def write_line_alternatives(line_alternatives):
    for line in line_alternatives:
        with open('write_linealternatives_for_line_'+str(line)+'.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for line_alternative in line_alternatives[line]:
                for line_richtung in line_alternatives[line][line_alternative][1]:
                    cost_line = line_alternatives[line][line_alternative][0]
                    list_of_stops = line_alternatives[line][line_alternative][1][line_richtung][0]
                    list_of_edges = line_alternatives[line][line_alternative][1][line_richtung][1]
                    writer.writerow([line, line_alternative, line_richtung, cost_line, list_of_stops, list_of_edges])            

def write_list_of_line_alternatives(line_alternatives):
    list_of_line_alternatives = get_list_of_line_alternatives(line_alternatives)
    with open('write_linealternatives.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for line_alternative in list_of_line_alternatives:
            line_nummer = line_alternative[0]
            line_zuggruppe = line_alternative[1]
            line_alternative_nummer = line_alternative[2]
            writer.writerow([line_nummer, line_zuggruppe, line_alternative_nummer])  
    
def write_events_for_lines(events, lines):
    for line in lines:
        with open('write_z_events_for_line_'+str(line)+'.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for event in events:
                event_line = event[2]
                if event_line == line:
                    writer.writerow([event])  

def write_wait_drive_wende_activities_for_lines(activities, lines):
    for line in lines:
        with open('write_z_wdw_activities_for_line_'+str(line)+'.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for activity in activities:
                event_1 = activity[0]
                event_2 = activity[1]
                line_1 = event_1[2]
                line_2 = event_2[2]
                activity_type = activities[activity][3]
                if line_1 == line:
                    if activity_type == 'wait' or activity_type == 'drive' or activity_type == 'wende':
                        writer.writerow([activity, activity_type])
                        if line_1 != line_2:
                            print('Warning: there is an error at wait, drive or wende activities')

def write_transfer_activities_for_lines(activities, lines):
    for line in lines:
        with open('write_z_trans_activities_for_line_'+str(line)+'.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for activity in activities:
                event_1 = activity[0]
                event_2 = activity[1]
                line_1 = event_1[2]
                line_2 = event_2[2]
                activity_type = activities[activity][3]
                if line_1 == line:
                    if activity_type == 'trans':
                        writer.writerow([activity, activity_type])
                        if line_1 == line_2:
                            print('Warning: there is an error at transfer activities')
            
def write_trans_activities_for_stops(activities, stops):
    list_of_transfer_stops = get_list_of_transfer_stops(stops)
    list_of_trans_activities = get_list_of_trans_activities(activities)
    for stop in list_of_transfer_stops:
        with open('write_z_trans_activities_for_stop_'+str(stop)+'.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for activity in list_of_trans_activities:
                event_1 = activity[0]
                event_2 = activity[1]
                stop_1 = event_1[0]
                stop_2 = event_2[0]
                activity_type = activities[activity][3]
                if stop_1 == stop:
                    writer.writerow([activity, activity_type])
                    if stop_1 != stop_2:
                        print('Warning: there is an error at transfer activities')

def write_headway_activities_for_stops(activities, stops):
    list_of_active_stops = get_list_of_active_stops(stops)
    list_of_headway_activities = get_list_of_headway_activities(activities)
    for stop in list_of_active_stops:
        with open('write_z_headway_activities_for_stop_'+str(stop)+'.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for activity in list_of_headway_activities:
                event_1 = activity[0]
                event_2 = activity[1]
                stop_1 = event_1[0]
                stop_2 = event_2[0]
                activity_type = activities[activity][3]
                if stop_1 == stop:
                    writer.writerow([activity, activity_type])
                    if stop_1 != stop_2:
                        print('Warning: there is an error at headway activities')
        
    

def write_headway_activities_for_lines(activities, lines):
    for line in lines:
        with open('write_z_headway_activities_for_line_'+str(line)+'.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            for activity in activities:
                event_1 = activity[0]
                event_2 = activity[1]
                line_1 = event_1[2]
                line_2 = event_2[2]
                activity_type = activities[activity][3]
                if line_1 == line:
                    if activity_type == 'headway':
                        writer.writerow([activity, activity_type])
                        if line_1 == line_2:
                            print('Warning: there is an error at headway activities')
                            

            
            
