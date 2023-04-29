# -*- coding: utf-8 -*-
"""
@author: Sarah  Burchert

"""

import csv
import funktionen

###################################################          
########### Solution Functions ####################
###################################################

def create_solution_frequencies(m, line_alternatives):
    solution_frequencies = {}
    for line in line_alternatives:
        solution_frequencies[line]={}
        for line_alternative in line_alternatives[line]:
            line_nummer = line_alternative[0]
            line_zuggruppe = line_alternative[1]
            line_alternative_nummer = line_alternative[2]
            var = m.getVarByName('f['+str(line_nummer)+','+str(line_zuggruppe)+','+str(line_alternative_nummer)+']')
            var_frequency = var.x
            solution_frequencies[line][line_alternative]=var_frequency
    return(solution_frequencies)

def create_default_solution_frequencies(line_alternatives):
    solution_frequencies = {}
    for line in line_alternatives:
        solution_frequencies[line]={}
        for line_alternative in line_alternatives[line]:
            solution_frequencies[line][line_alternative]=1
    return(solution_frequencies)
            
def create_solution_events(m, events):
    solution_events = {}
    list_of_active_events = funktionen.get_list_of_not_fixed_events(events)
    for event in list_of_active_events:
        event_var_list = get_event_var_list(event)
        event_var = m.getVarByName('time['+str(event_var_list)+']')
        event_var_time = event_var.x
        solution_events[event]=event_var_time
    return(solution_events)

def create_default_solution_events(events):
    solution_events = {}
    list_of_active_events = funktionen.get_list_of_not_fixed_events(events)
    for event in list_of_active_events:
        solution_events[event]= 0
    return(solution_events)
  
def create_solution_z(m, activities):
    solution_z = {}
    list_of_wait_activities = funktionen.get_list_of_wait_activities(activities)
    for activity in list_of_wait_activities:
        activity_var_list = get_activity_var_list(activity)
        activity_var = m.getVarByName('zwait['+str(activity_var_list)+']')
        activity_z = activity_var.x
        solution_z[activity] = activity_z
    list_of_drive_activities = funktionen.get_list_of_drive_activities(activities)
    for activity in list_of_drive_activities:
        activity_var_list = get_activity_var_list(activity)
        activity_var = m.getVarByName('zdrive['+str(activity_var_list)+']')
        activity_z = activity_var.x
        solution_z[activity] = activity_z
    list_of_wende_activities = funktionen.get_list_of_wende_activities(activities)
    for activity in list_of_wende_activities:
        activity_var_list = get_activity_var_list(activity)
        activity_var = m.getVarByName('zwende['+str(activity_var_list)+']')
        activity_z = activity_var.x
        solution_z[activity] = activity_z
    list_of_trans_activities = funktionen.get_list_of_trans_activities(activities)
    for activity in list_of_trans_activities:
        activity_var_list = get_activity_var_list(activity)
        activity_var = m.getVarByName('ztrans['+str(activity_var_list)+']')
        activity_z = activity_var.x
        solution_z[activity] = activity_z
    list_of_head_activities = funktionen.get_list_of_headway_activities(activities)
    for activity in list_of_head_activities:
        activity_var_list = get_activity_var_list(activity)
        activity_var = m.getVarByName('zhead['+str(activity_var_list)+']')
        activity_z = activity_var.x
        solution_z[activity] = activity_z
    return(solution_z)

def create_solution_y(m, activities):
    solution_y = {}
    for activity in activities:
        activity_var_list = get_activity_var_list(activity)
        activity_var = m.getVarByName('y_a['+str(activity_var_list)+']')
        activity_y = activity_var.x
        solution_y[activity] = activity_y
    return(solution_y)

def create_default_solution_y(activities):
    solution_y = {}
    for activity in activities:
        solution_y[activity] = 0
    return(solution_y)
        


###################################################          
########### Get Functions #########################
###################################################

def get_event_var_list(event):
    event_stop = event[0]
    event_ankunft = event[1]
    event_line = event[2]
    event_line_richtung = event[3]
    event_var_list=str(event_stop)+','+str(event_ankunft)+','+str(event_line)+ ',' + str(event_line_richtung)    
    return(event_var_list)

def get_activity_var_list(activity):
    event_1 = activity[0]
    event_2 = activity[1]
    event_1_stop = event_1[0]
    event_1_ankunft = event_1[1]
    event_1_line = event_1[2]
    event_1_line_richtung = event_1[3]
    event_2_stop = event_2[0]
    event_2_ankunft = event_2[1]
    event_2_line = event_2[2]
    event_2_line_richtung = event_2[3]
    event_1_var_list = "'" +str(event_1_stop) + "', '" + str(event_1_ankunft)+ "', " + str(event_1_line) + ", " + str(event_1_line_richtung)
    event_2_var_list = "'" +str(event_2_stop) + "', '" + str(event_2_ankunft)+ "', " + str(event_2_line) + ", " + str(event_2_line_richtung)
    activity_var_list='('+str(event_1_var_list)+'),('+str(event_2_var_list) +')'    
    return(activity_var_list)

def get_LP_objective(alpha, line_alternatives, solution_frequencies):
    sol_obj_LP = 0
    for line in line_alternatives:
        for line_alternative in line_alternatives[line]:
            line_cost =line_alternatives[line][line_alternative][0]
            line_frequency = solution_frequencies[line][line_alternative]
            sol_obj_LP += line_frequency * float(line_cost) * alpha
    return(round(sol_obj_LP,1))

def get_TT_objective(beta, activities, solution_y):
    sol_obj_TT = 0
    for activity in activities:
        activity_weight = activities[activity][2]
        activity_y = solution_y[activity]
        sol_obj_TT += activity_weight * activity_y * beta               
    return(sol_obj_TT)

# returns list of events which are chosen by solution (events of line alternatives with frequency one)
def get_choosen_events(solution_events, solution_frequencies, line_alternatives):
    list_of_choosen_events = []
    for line in solution_frequencies:
        list_of_choosen_events_for_line = get_choosen_events_for_line(line, solution_events, solution_frequencies, line_alternatives)
        list_of_choosen_events.extend(list_of_choosen_events_for_line)
    return(list_of_choosen_events)
        
    
def get_choosen_events_for_line(line, solution_events, solution_frequencies, line_alternatives):
    list_of_choosen_events = []
    for line_alternative in solution_frequencies[line]:
        if solution_frequencies[line][line_alternative] > 0.5:
            choosen_line_alternative = line_alternative       
            for event in solution_events:
                stop = event[0]
                ankunft = event[1]
                if event[2] == line:
                    line_original_richtung = event[3]
                    line_nummer = line[0]
                    line_zuggruppe = line[1]
                    line_alternative_nummer = choosen_line_alternative[2]
                    line_start = line_original_richtung[2]
                    line_end = line_original_richtung[3]
                    line_alternative_richtung = (line_nummer, line_zuggruppe, line_alternative_nummer, line_start, line_end)
                    if stop in line_alternatives[line][choosen_line_alternative][1][line_alternative_richtung][0]:
                        stop_endstelle = line_alternatives[line][choosen_line_alternative][1][line_alternative_richtung][0][stop]
                        if stop_endstelle == 'start' and ankunft == 'dep':
                            list_of_choosen_events.append(event)
                        elif stop_endstelle == '':
                            list_of_choosen_events.append(event)
                        elif stop_endstelle == 'end' and ankunft == 'arr':
                            list_of_choosen_events.append(event)
    return(list_of_choosen_events)    


def get_choosen_wait_activities(solution_events, solution_frequencies, line_alternatives, activities):
    list_of_choosen_wait_activities =  []
    list_of_wait_activities = funktionen.get_list_of_wait_activities(activities)
    list_of_choosen_events = get_choosen_events(solution_events, solution_frequencies, line_alternatives)
    
    for activity in list_of_wait_activities:
        event_1 = activity[0]
        event_2 = activity[1]
        if event_1 in list_of_choosen_events and event_2 in list_of_choosen_events:
            list_of_choosen_wait_activities.append(activity)
    return(list_of_choosen_wait_activities)
                

###################################################          
########### Writing Functions #####################
###################################################


def write_solution(m, Dateiname):
    with open('solution_'+str(Dateiname)+'.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for solution in m.getVars():
            variable = solution.varName
            sol = solution.x
            writer.writerow([variable, sol ])

def write_solution_TT_LP(m, Dateiname):
    with open(r'.\TT_LP\solutions\solution_'+str(Dateiname)+'.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for solution in m.getVars():
            variable = solution.varName
            sol = solution.x
            writer.writerow([variable, sol ])    
            
def write_solution_LP_TT(m, Dateiname):
    with open(r'.\LP_TT\solutions\solution_'+str(Dateiname)+'.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        for solution in m.getVars():
            variable = solution.varName
            sol = solution.x
            writer.writerow([variable, sol ])

def write_solution_frequencies(m, Dateiname, solution_frequencies):
    with open(r'solution_'+str(Dateiname)+'_line_frequencies.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Solution: Frequencies of line alternatives' ])
        for line in solution_frequencies:
            line_nummer = line[0]
            line_zuggruppe = line[1]
            writer.writerow([ 'Line: ' + str(line_nummer) + ' - ' + str(line_zuggruppe)])
            for line_alternative in solution_frequencies[line]:
                line_alternative_nummer = line_alternative[2]
                sol_frequency = solution_frequencies[line][line_alternative]
                writer.writerow(['', line_alternative_nummer, sol_frequency ])

def write_solution_frequencies_LP_TT(m, Dateiname, solution_frequencies):
    with open(r'.\LP_TT\solutions\solution_'+str(Dateiname)+'_line_frequencies.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Solution: Frequencies of line alternatives' ])
        for line in solution_frequencies:
            line_nummer = line[0]
            line_zuggruppe = line[1]
            writer.writerow([ 'Line: ' + str(line_nummer) + ' - ' + str(line_zuggruppe)])
            for line_alternative in solution_frequencies[line]:
                line_alternative_nummer = line_alternative[2]
                sol_frequency = solution_frequencies[line][line_alternative]
                writer.writerow(['', line_alternative_nummer, sol_frequency ])
                
def write_solution_frequencies_TT_LP(Dateiname, solution_frequencies):
    with open(r'.\TT_LP\solutions\solution_'+str(Dateiname)+'_line_frequencies.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Solution: Frequencies of line alternatives' ])
        for line in solution_frequencies:
            line_nummer = line[0]
            line_zuggruppe = line[1]
            writer.writerow([ 'Line: ' + str(line_nummer) + ' - ' + str(line_zuggruppe)])
            for line_alternative in solution_frequencies[line]:
                line_alternative_nummer = line_alternative[2]
                sol_frequency = solution_frequencies[line][line_alternative]
                writer.writerow(['', line_alternative_nummer, sol_frequency ])

def write_solution_timetable_for_lines(m, Dateiname, line_alternatives, solution_frequencies, solution_events, T, k):
     for line in solution_frequencies:
            for line_alternative in solution_frequencies[line]:
                if solution_frequencies[line][line_alternative] == 1:
                    for line_richtung in line_alternatives[line][line_alternative][1]:
                        line_alternative_nummer = line_alternative[2]
                        list_of_stops = line_alternatives[line][line_alternative][1][line_richtung][0]
                        list_of_edges = line_alternatives[line][line_alternative][1][line_richtung][1]
                        line_original_richtung = (line_richtung[0], line_richtung[1], line_richtung[3], line_richtung[4])
                        for stop in list_of_stops:
                            endstelle = line_alternatives[line][line_alternative][1][line_richtung][0][stop]
                            if endstelle == 'start':
                                start_stop = stop
                            if endstelle == 'end':
                                end_stop = stop
                        with open('solution_'+str(Dateiname)+'_Timetable_'+str(line_richtung)+'.csv', 'w', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(['Timetable for: ', line, line_alternative_nummer, start_stop, end_stop])
                            writer.writerow([])
                            writer.writerow(['stop','', 'Arrival', 'waiting time', '', 'Departure', 'driving time'])
                            for edge in list_of_edges:
                                stop_1 = edge[0]
                                stop_2 = edge[1]
                                stop_1_arr_event = (stop_1, 'arr', line, line_original_richtung)
                                stop_1_dep_event = (stop_1, 'dep', line, line_original_richtung)
                                stop_2_arr_event = (stop_2, 'arr', line, line_original_richtung)
                                time_dep_stop_1 = solution_events[stop_1_dep_event]
                                time_arr_stop_2 = solution_events[stop_2_arr_event]
                                fahrzeit = time_arr_stop_2 - time_dep_stop_1
                                if fahrzeit < 0:
                                    fahrzeit = fahrzeit + T
                                if stop_1 == start_stop:                                                    
                                    writer.writerow([stop_1, '', '', '', '', time_dep_stop_1/k, fahrzeit/k])
                                if stop_1 != start_stop and stop_1 != end_stop:
                                    time_arr_stop_1 = solution_events[stop_1_arr_event]
                                    haltezeit = time_dep_stop_1 - time_arr_stop_1
                                    if haltezeit < 0:
                                        haltezeit = haltezeit + T
                                    writer.writerow([stop_1, '', time_arr_stop_1/k, haltezeit/k, '', time_dep_stop_1/k, fahrzeit/k])
                                if stop_2 == end_stop:
                                    writer.writerow([stop_2, '', time_arr_stop_2/k, '', '', '', ''])
                                    
                                    
def write_solution_not_active_timetable_for_lines(m, Dateiname, line_alternatives, solution_frequencies, solution_events, T, k):
    for line in solution_frequencies:
            for line_alternative in solution_frequencies[line]:
                if solution_frequencies[line][line_alternative] == 0:
                    for line_richtung in line_alternatives[line][line_alternative][1]:
                        line_alternative_nummer = line_alternative[2]
                        list_of_stops = line_alternatives[line][line_alternative][1][line_richtung][0]
                        list_of_edges = line_alternatives[line][line_alternative][1][line_richtung][1]
                        line_original_richtung = (line_richtung[0], line_richtung[1], line_richtung[3], line_richtung[4])
                        for stop in list_of_stops:
                            endstelle = line_alternatives[line][line_alternative][1][line_richtung][0][stop]
                            if endstelle == 'start':
                                start_stop = stop
                            if endstelle == 'end':
                                end_stop = stop
                        with open('solution_'+str(Dateiname)+'_not_active_Timetable_'+str(line_richtung)+'.csv', 'w', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow(['Timetable for: ', line, line_alternative_nummer, start_stop, end_stop])
                            writer.writerow([])
                            writer.writerow(['stop','', 'Arrival', 'waiting time', '', 'Departure', 'driving time'])
                            for edge in list_of_edges:
                                stop_1 = edge[0]
                                stop_2 = edge[1]
                                stop_1_arr_event = (stop_1, 'arr', line, line_original_richtung)
                                stop_1_dep_event = (stop_1, 'dep', line, line_original_richtung)
                                stop_2_arr_event = (stop_2, 'arr', line, line_original_richtung)
                                time_dep_stop_1 = solution_events[stop_1_dep_event]
                                time_arr_stop_2 = solution_events[stop_2_arr_event]
                                fahrzeit = time_arr_stop_2 - time_dep_stop_1
                                if fahrzeit < 0:
                                    fahrzeit = fahrzeit + T
                                if stop_1 == start_stop:                                                    
                                    writer.writerow([stop_1, '', '', '', '', time_dep_stop_1/k, fahrzeit/k])
                                if stop_1 != start_stop and stop_1 != end_stop:
                                    time_arr_stop_1 = solution_events[stop_1_arr_event]
                                    haltezeit = time_dep_stop_1 - time_arr_stop_1
                                    if haltezeit < 0:
                                        haltezeit = haltezeit + T
                                    writer.writerow([stop_1, '', time_arr_stop_1/k, haltezeit/k, '', time_dep_stop_1/k, fahrzeit/k])
                                if stop_2 == end_stop:
                                    writer.writerow([stop_2, '', time_arr_stop_2/k, '', '', '', ''])    


def write_solution_objective_and_line_frequencies_TT_LP_A(obj_MP, obj_eta, obj_SP, it_solution_frequencies):
    with open('solution_Benders_TT_LP_A.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['iteration', 'MP Objective', 'eta', 'SP Objective', 'Cut type', 'line frequencies'])
        writer.writerow(['','', '', '', '', '', 'S41-A1', 'S41-A2', 'S41-A3', 'S41-A4', '', 'S41I-A1', 'S41I-A2', 'S41I-A3', 'S41I-A4','',  'S45-A1', 'S45-A2', 'S45-A3', '', 'S46-A1', 'S46-A2', 'S46-A3', 'S46-A4', '', 'S47-A1', 'S47-A2', 'S47-A3', 'S47-A4'])
        
        for it in obj_MP:
            objMP = obj_MP[it]
            eta = obj_eta[it]
            if it in obj_SP:
                objSP = obj_SP[it]
                if objSP != '':
                    cut_type = 'opt'
                else:
                    cut_type = 'feas'
            else:
                objSP = ''
                cut_type = 'feas'
                
            try:
                solution_frequencies = it_solution_frequencies[it]
                for line in solution_frequencies:
                    line_nummer = line[0]
                    for line_alternative in solution_frequencies[line]:
                        line_alternative_nummer = line_alternative[2]
                        line_frequency = solution_frequencies[line][line_alternative]
                        if line == ('S41', 'A'):
                            if line_alternative_nummer == 'A1':
                                S41A1 = line_frequency
                            elif line_alternative_nummer == 'A2':
                                S41A2 = line_frequency
                            elif line_alternative_nummer == 'A3':
                                S41A3 = line_frequency
                            elif line_alternative_nummer == 'A4':
                                S41A4 = line_frequency
                        elif line == ('S41', 'AI'):
                             if line_alternative_nummer == 'A1':
                                 S41IA1 = line_frequency
                             elif line_alternative_nummer == 'A2':
                                 S41IA2 = line_frequency
                             elif line_alternative_nummer == 'A3':
                                 S41IA3 = line_frequency
                             elif line_alternative_nummer == 'A4':
                                 S41IA4 = line_frequency
                        elif line_nummer == 'S45':
                              if line_alternative_nummer == 'A1':
                                  S45A1 = line_frequency
                              elif line_alternative_nummer == 'A2':
                                  S45A2 = line_frequency
                              elif line_alternative_nummer == 'A3':
                                  S45A3 = line_frequency
                        elif line_nummer == 'S46':
                              if line_alternative_nummer == 'A1':
                                  S46A1 = line_frequency
                              elif line_alternative_nummer == 'A2':
                                  S46A2 = line_frequency
                              elif line_alternative_nummer == 'A3':
                                  S46A3 = line_frequency
                              elif line_alternative_nummer == 'A4':
                                  S46A4 = line_frequency
                        elif line_nummer == 'S47':
                              if line_alternative_nummer == 'A1':
                                  S47A1 = line_frequency
                              elif line_alternative_nummer == 'A2':
                                  S47A2 = line_frequency
                              elif line_alternative_nummer == 'A3':
                                  S47A3 = line_frequency
                              elif line_alternative_nummer == 'A4':
                                  S47A4 = line_frequency
                  
                writer.writerow([it, objMP, eta, objSP, cut_type, '', S41A1, S41A2, S41A3, S41A4, '',  S41IA1, S41IA2, S41IA3, S41IA4,'',  S45A1, S45A2, S45A3, '', S46A1, S46A2, S46A3, S46A4,'', S47A1, S47A2, S47A3, S47A4])
            except: 
                writer.writerow([it, objMP, eta, objSP, cut_type])
    
    
def write_solution_objective_and_line_frequencies_TT_LP_B(obj_MP, obj_eta, obj_SP, it_solution_frequencies):
    with open('solution_Benders_TT_LP_B.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['iteration', 'MP Objective', 'eta', 'SP Objective', 'Cut type', 'line frequencies'])
        writer.writerow(['','', '', '', '', '', 'S41-A1', 'S41-A2', 'S41-A5', 'S41-A6', '', 'S41I-A1', 'S41I-A2', 'S41I-A5', 'S41I-A6','',  'S45-A1', 'S45-A4', 'S45-A5', '', 'S46-A1', 'S46-A2', 'S46-A5', 'S46-A6', '', 'S47-A1', 'S47-A5', 'S47-A6'])
       
        for it in obj_MP:
           objMP = obj_MP[it]
           eta = obj_eta[it]
           if it in obj_SP:
               objSP = obj_SP[it]
               cut_type = 'opt'
           else:
               objSP = ''
               cut_type = 'feas'
           
           try: 
               solution_frequencies = it_solution_frequencies[it]
   
               for line in solution_frequencies:
                   line_nummer = line[0]
                   for line_alternative in solution_frequencies[line]:
                       line_alternative_nummer = line_alternative[2]
                       line_frequency = solution_frequencies[line][line_alternative]
                       if line == ('S41', 'A'):
                           if line_alternative_nummer == 'A1':
                               S41A1 = line_frequency
                           elif line_alternative_nummer == 'A2':
                               S41A2 = line_frequency
                           elif line_alternative_nummer == 'A5':
                               S41A5 = line_frequency
                           elif line_alternative_nummer == 'A6':
                               S41A6 = line_frequency
                       elif line == ('S41', 'AI'):
                            if line_alternative_nummer == 'A1':
                                S41IA1 = line_frequency
                            elif line_alternative_nummer == 'A2':
                                S41IA2 = line_frequency
                            elif line_alternative_nummer == 'A5':
                                S41IA5 = line_frequency
                            elif line_alternative_nummer == 'A6':
                                S41IA6 = line_frequency
                       elif line_nummer == 'S45':
                             if line_alternative_nummer == 'A1':
                                 S45A1 = line_frequency
                             elif line_alternative_nummer == 'A4':
                                 S45A4 = line_frequency
                             elif line_alternative_nummer == 'A5':
                                 S45A5 = line_frequency
                       elif line_nummer == 'S46':
                             if line_alternative_nummer == 'A1':
                                 S46A1 = line_frequency
                             elif line_alternative_nummer == 'A2':
                                 S46A2 = line_frequency
                             elif line_alternative_nummer == 'A5':
                                 S46A5 = line_frequency
                             elif line_alternative_nummer == 'A6':
                                 S46A6 = line_frequency
                       elif line_nummer == 'S47':
                             if line_alternative_nummer == 'A1':
                                 S47A1 = line_frequency
                             elif line_alternative_nummer == 'A5':
                                 S47A5 = line_frequency
                             elif line_alternative_nummer == 'A6':
                                 S47A6 = line_frequency
                 
               writer.writerow([it, objMP, eta, objSP, cut_type, '', S41A1, S41A2, S41A5, S41A6, '',  S41IA1, S41IA2, S41IA5, S41IA6,'',  S45A1, S45A4, S45A5, '', S46A1, S46A2, S46A5, S46A6,'', S47A1, S47A5, S47A6])
           except:
               writer.writerow([it, objMP, eta, objSP, cut_type])  
    
    
    
    
    
def write_solution_objective_and_line_frequencies_LP_TT_A(obj_MP, obj_eta, obj_SP, it_solution_frequencies):
    with open('solution_Benders_LP_TT_A.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['iteration', 'MP Objective', 'eta', 'SP Objective', 'Cut type', 'line frequencies'])
        writer.writerow(['','', '', '', '', '', 'S41-A1', 'S41-A2', 'S41-A3', 'S41-A4', '', 'S41I-A1', 'S41I-A2', 'S41I-A3', 'S41I-A4','',  'S45-A1', 'S45-A2', 'S45-A3', '', 'S46-A1', 'S46-A2', 'S46-A3', 'S46-A4', '', 'S47-A1', 'S47-A2', 'S47-A3', 'S47-A4'])
        
        for it in obj_MP:
            objMP = obj_MP[it]
            eta = obj_eta[it]
            if it in obj_SP:
                objSP = obj_SP[it]
                cut_type = 'opt'
            else:
                objSP = ''
                cut_type = 'feas'
            
            try: 
                solution_frequencies = it_solution_frequencies[it]
    
                for line in solution_frequencies:
                    line_nummer = line[0]
                    for line_alternative in solution_frequencies[line]:
                        line_alternative_nummer = line_alternative[2]
                        line_frequency = solution_frequencies[line][line_alternative]
                        if line == ('S41', 'A'):
                            if line_alternative_nummer == 'A1':
                                S41A1 = line_frequency
                            elif line_alternative_nummer == 'A2':
                                S41A2 = line_frequency
                            elif line_alternative_nummer == 'A3':
                                S41A3 = line_frequency
                            elif line_alternative_nummer == 'A4':
                                S41A4 = line_frequency
                        elif line == ('S41', 'AI'):
                             if line_alternative_nummer == 'A1':
                                 S41IA1 = line_frequency
                             elif line_alternative_nummer == 'A2':
                                 S41IA2 = line_frequency
                             elif line_alternative_nummer == 'A3':
                                 S41IA3 = line_frequency
                             elif line_alternative_nummer == 'A4':
                                 S41IA4 = line_frequency
                        elif line_nummer == 'S45':
                              if line_alternative_nummer == 'A1':
                                  S45A1 = line_frequency
                              elif line_alternative_nummer == 'A2':
                                  S45A2 = line_frequency
                              elif line_alternative_nummer == 'A3':
                                  S45A3 = line_frequency
                        elif line_nummer == 'S46':
                              if line_alternative_nummer == 'A1':
                                  S46A1 = line_frequency
                              elif line_alternative_nummer == 'A2':
                                  S46A2 = line_frequency
                              elif line_alternative_nummer == 'A3':
                                  S46A3 = line_frequency
                              elif line_alternative_nummer == 'A4':
                                  S46A4 = line_frequency
                        elif line_nummer == 'S47':
                              if line_alternative_nummer == 'A1':
                                  S47A1 = line_frequency
                              elif line_alternative_nummer == 'A2':
                                  S47A2 = line_frequency
                              elif line_alternative_nummer == 'A3':
                                  S47A3 = line_frequency
                              elif line_alternative_nummer == 'A4':
                                  S47A4 = line_frequency
                  
                writer.writerow([it, objMP, eta, objSP, cut_type, '', S41A1, S41A2, S41A3, S41A4, '',  S41IA1, S41IA2, S41IA3, S41IA4,'',  S45A1, S45A2, S45A3, '', S46A1, S46A2, S46A3, S46A4,'', S47A1, S47A2, S47A3, S47A4])
            except:
                writer.writerow([it, objMP, eta, objSP, cut_type])
                
                
                

def write_solution_objective_and_line_frequencies_LP_TT_B(obj_MP, obj_eta, obj_SP, it_solution_frequencies):
    with open('solution_Benders_LP_TT_B.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['iteration', 'MP Objective', 'eta', 'SP Objective', 'Cut type', 'line frequencies'])
        writer.writerow(['','', '', '', '', '', 'S41-A1', 'S41-A2', 'S41-A5', 'S41-A6', '', 'S41I-A1', 'S41I-A2', 'S41I-A5', 'S41I-A6','',  'S45-A1', 'S45-A4', 'S45-A5', '', 'S46-A1', 'S46-A2', 'S46-A5', 'S46-A6', '', 'S47-A1', 'S47-A5', 'S47-A6'])
        
        for it in obj_MP:
            objMP = obj_MP[it]
            eta = obj_eta[it]
            if it in obj_SP:
                objSP = obj_SP[it]
                cut_type = 'opt'
            else:
                objSP = ''
                cut_type = 'feas'
            
            try: 
                solution_frequencies = it_solution_frequencies[it]
    
                for line in solution_frequencies:
                    line_nummer = line[0]
                    for line_alternative in solution_frequencies[line]:
                        line_alternative_nummer = line_alternative[2]
                        line_frequency = solution_frequencies[line][line_alternative]
                        if line == ('S41', 'A'):
                            if line_alternative_nummer == 'A1':
                                S41A1 = line_frequency
                            elif line_alternative_nummer == 'A2':
                                S41A2 = line_frequency
                            elif line_alternative_nummer == 'A5':
                                S41A5 = line_frequency
                            elif line_alternative_nummer == 'A6':
                                S41A6 = line_frequency
                        elif line == ('S41', 'AI'):
                             if line_alternative_nummer == 'A1':
                                 S41IA1 = line_frequency
                             elif line_alternative_nummer == 'A2':
                                 S41IA2 = line_frequency
                             elif line_alternative_nummer == 'A5':
                                 S41IA5 = line_frequency
                             elif line_alternative_nummer == 'A6':
                                 S41IA6 = line_frequency
                        elif line_nummer == 'S45':
                              if line_alternative_nummer == 'A1':
                                  S45A1 = line_frequency
                              elif line_alternative_nummer == 'A4':
                                  S45A4 = line_frequency
                              elif line_alternative_nummer == 'A5':
                                  S45A5 = line_frequency
                        elif line_nummer == 'S46':
                              if line_alternative_nummer == 'A1':
                                  S46A1 = line_frequency
                              elif line_alternative_nummer == 'A2':
                                  S46A2 = line_frequency
                              elif line_alternative_nummer == 'A5':
                                  S46A5 = line_frequency
                              elif line_alternative_nummer == 'A6':
                                  S46A6 = line_frequency
                        elif line_nummer == 'S47':
                              if line_alternative_nummer == 'A1':
                                  S47A1 = line_frequency
                              elif line_alternative_nummer == 'A5':
                                  S47A5 = line_frequency
                              elif line_alternative_nummer == 'A6':
                                  S47A6 = line_frequency
                  
                writer.writerow([it, objMP, eta, objSP, cut_type, '', S41A1, S41A2, S41A5, S41A6, '',  S41IA1, S41IA2, S41IA5, S41IA6,'',  S45A1, S45A4, S45A5, '', S46A1, S46A2, S46A5, S46A6,'', S47A1, S47A5, S47A6])
            except:
                writer.writerow([it, objMP, eta, objSP, cut_type])
                
                

###################################################          
########### Opt Cuts TT - LP ######################
###################################################

def write_opt_cuts_TT_LP(m_MP, m_SP, opt_cuts, it):
    with open(r'.\TT_LP\cuts\cut_'+str(it)+'_opt_LP_TT.csv', 'w', newline='') as f:
        eta_var = m_MP.getVarByName('eta')
        eta = eta_var.x
        writer = csv.writer(f)
        writer.writerow(['MP_Obj:', m_MP.objVal, 'eta:', eta, 'SP_Obj:', m_SP.objVal])
        writer.writerow(['opt_cut iteration','kind of parameter', 'parameter', 'variable', 'value'])
        solution_edges = opt_cuts[it][0]
        para_kind = 'edge'
        for edge in solution_edges:
            for variable in opt_cuts[it][0][edge]:
                value = opt_cuts[it][0][edge][variable]
            writer.writerow([it,para_kind, edge, variable, value])
            
        solution_lines_under_construction = opt_cuts[it][1]
        para_kind = 'line'
        for line in solution_lines_under_construction:
            for variable in opt_cuts[it][1][line]:
                value = opt_cuts[it][1][line][variable]
            writer.writerow([it,para_kind, line, variable, value])
           
        solution_line_alternatives = opt_cuts[it][2]
        para_kind ='line_alternative'
        for line_alternative in solution_line_alternatives:
            for variable in opt_cuts[it][2][line_alternative]:
                value = opt_cuts[it][2][line_alternative][variable]
            writer.writerow([it,para_kind, line, variable, value])
        
        solution_activities = opt_cuts[it][3]
        para_kind = 'activity'
        for activity in solution_activities:
            for variable in opt_cuts[it][3][activity]:
                value = opt_cuts[it][3][activity][variable]
                writer.writerow([it,para_kind, activity, variable, value])
                                   
                                    
                    
def read_opt_cuts_TT_LP(opt_cuts, opt_cut_Datei, obj_MP, obj_SP, obj_eta):
    with open("./LP_TT/cuts/"+str(opt_cut_Datei)) as csvdatei:
        solution_edges = {}
        solution_lines_under_construction = {}
        solution_line_alternatives = {}
        solution_activities= {}
        print('Reading Data ' + str(opt_cut_Datei))
        csv_reader_object = csv.reader(csvdatei, delimiter=',')
        zeilennummer = 0
        for row in csv_reader_object:
            if zeilennummer == 0:
                mp_obj = row[1]
                eta_obj = row[3]
                sp_obj = row[5]
                zeilennummer += 1
            elif zeilennummer == 1:
                zeilennummer += 1
            else:
                it = int(row[0])
                para_kind = row[1]
                para = row[2]
                variable = row[3]
                value = float(row[4])
                if para_kind == 'edge':
                    para_list = para.split("'")
                    stop_1 = para_list[1]
                    stop_2 = para_list[3]
                    para = (stop_1, stop_2)
                elif para_kind == 'line':
                    para_list = para.split("'")
                    line_nr = para_list[1]
                    line_zuggruppe = para_list[3]
                    para = (line_nr, line_zuggruppe)
                elif para_kind == 'line_alternative':
                    para_list = para.split("'")
                    line_nr = para_list[1]
                    line_zuggruppe = para_list[3]
                    line_alternative_nummer = para_list[5]
                    para = (line_nr, line_zuggruppe, line_alternative_nummer)
                elif para_kind == 'activity':
                    para_list = para.split("'")
                    stop_1 = para_list[1]
                    ankunft_1 = para_list[3]
                    line_1_nr = para_list[5]
                    line_1_zuggruppe = para_list[7]
                    line_1_start = para_list[13]
                    line_1_stop = para_list[15]
                    
                    stop_2 = para_list[17]
                    ankunft_2 = para_list[19]
                    line_2_nr = para_list[21]
                    line_2_zuggruppe = para_list[23]
                    line_2_start = para_list[29]
                    line_2_stop = para_list[31]
                    
                    event_1 = (stop_1, ankunft_1, (line_1_nr, line_1_zuggruppe), (line_1_nr, line_1_zuggruppe, line_1_start, line_1_stop))
                    event_2 = (stop_2, ankunft_2, (line_2_nr, line_2_zuggruppe), (line_2_nr, line_2_zuggruppe, line_2_start, line_2_stop))
                    para = (event_1, event_2)                     
                    
                if it not in opt_cuts:
                    opt_cuts[it]={}
                if para not in opt_cuts[it]:
                    opt_cuts[it][para]={}
                    
                opt_cuts[it][para][variable] = value
                zeilennummer += 1
        
        obj_MP[it] = float(mp_obj)
        obj_SP[it] = float(sp_obj)
        obj_eta[it] = float(eta_obj)
        opt_cuts[it]=[solution_edges, solution_lines_under_construction, solution_line_alternatives ,solution_activities]
                                

###################################################          
########### Feas Cuts TT - LP #####################
###################################################
 
def write_feas_cuts_TT_LP(feas_cuts, it, m_MP):
    with open(r'.\TT_LP\cuts\cut_'+str(it)+'_feas_TT_LP.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        eta_var = m_MP.getVarByName('eta')
        eta = eta_var.x
        writer.writerow(['MP_Obj:', m_MP.objVal, 'eta:', eta])
        writer.writerow([it,'kind of parameter', 'parameter', 'variable', 'value'])
        for para in feas_cuts[it]:
            for variable in feas_cuts[it][para]:
                value = feas_cuts[it][para][variable]
                if variable == 'chi' or variable == 'psi':
                    para_kind = 'edge'
                elif variable == 'my':
                    para_kind = 'line'
                elif variable == 'ny':
                    para_kind = 'line_alternative'
                elif variable == 'theta' or variable == 'lamda' or variable == 'kappa':
                    para_kind = 'activity'
                writer.writerow([it,para_kind, para, variable, value])

                                   
                                    
                    
def read_feas_cuts_TT_LP(feas_cuts, feas_cut_Datei, obj_MP, obj_SP, obj_eta):
    with open("./TT_LP/cuts/"+str(feas_cut_Datei)) as csvdatei:
        print('Reading Data ' + str(feas_cut_Datei))
        csv_reader_object = csv.reader(csvdatei, delimiter=',')
        zeilennummer = 0
        for row in csv_reader_object:
            if zeilennummer == 0:
                mp_obj = row[1]
                eta_obj = row[3]
                zeilennummer += 1
            elif zeilennummer == 1:
                zeilennummer += 1
            else:
                it = int(row[0])
                para_kind = row[1]
                para = row[2]
                variable = row[3]
                value = float(row[4])
                if para_kind == 'edge':
                    para_list = para.split("'")
                    stop_1 = para_list[1]
                    stop_2 = para_list[3]
                    para = (stop_1, stop_2)
                elif para_kind == 'line':
                    para_list = para.split("'")
                    line_nr = para_list[1]
                    line_zuggruppe = para_list[3]
                    para = (line_nr, line_zuggruppe)
                elif para_kind == 'line_alternative':
                    para_list = para.split("'")
                    line_nr = para_list[1]
                    line_zuggruppe = para_list[3]
                    line_alternative_nummer = para_list[5]
                    para = (line_nr, line_zuggruppe, line_alternative_nummer)
                elif para_kind == 'activity':
                    para_list = para.split("'")
                    stop_1 = para_list[1]
                    ankunft_1 = para_list[3]
                    line_1_nr = para_list[5]
                    line_1_zuggruppe = para_list[7]
                    line_1_start = para_list[13]
                    line_1_stop = para_list[15]
                    
                    stop_2 = para_list[17]
                    ankunft_2 = para_list[19]
                    line_2_nr = para_list[21]
                    line_2_zuggruppe = para_list[23]
                    line_2_start = para_list[29]
                    line_2_stop = para_list[31]
                    
                    event_1 = (stop_1, ankunft_1, (line_1_nr, line_1_zuggruppe), (line_1_nr, line_1_zuggruppe, line_1_start, line_1_stop))
                    event_2 = (stop_2, ankunft_2, (line_2_nr, line_2_zuggruppe), (line_2_nr, line_2_zuggruppe, line_2_start, line_2_stop))
                    para = (event_1, event_2)                     
                    
                if it not in feas_cuts:
                    feas_cuts[it]={}
                if para not in feas_cuts[it]:
                    feas_cuts[it][para]={}
                    
                feas_cuts[it][para][variable] = value
                zeilennummer += 1

        obj_MP[it] = float(mp_obj)
        obj_eta[it] = float(eta_obj)
        obj_SP[it] = ''


###################################################          
########### Opt Cuts LP - TT ######################
###################################################

def write_opt_cuts_LP_TT(m_MP, m_SP, opt_cuts, it):
    with open(r'.\LP_TT\cuts\cut_'+str(it)+'_opt_LP_TT.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        eta_var = m_MP.getVarByName('eta')
        eta = eta_var.x
        writer.writerow(['MP_Obj:', m_MP.objVal,'eta:', eta, 'SP_Obj:', m_SP.objVal])
        writer.writerow(['opt_cut iteration','kind of parameter', 'parameter', 'variable', 'value'])
        solution_events = opt_cuts[it][0]
        para_kind = 'event'
        for event in solution_events:
            variable = 'my'
            value = opt_cuts[it][0][event][variable]
            writer.writerow([it,para_kind, event, variable, value])
        
        solution_activities = opt_cuts[it][1]
        para_kind = 'activity'
        for activity in solution_activities:
            for variable in opt_cuts[it][1][activity]:
                value = opt_cuts[it][1][activity][variable]
                writer.writerow([it,para_kind, activity, variable, value])
                                   
                                    
                    
def read_opt_cuts_LP_TT(opt_cuts, opt_cut_Datei, obj_MP, obj_SP, obj_eta):
    with open("./LP_TT/cuts/"+str(opt_cut_Datei)) as csvdatei:
        solution_events = {}
        solution_activities= {}
        print('Reading Data ' + str(opt_cut_Datei))
        csv_reader_object = csv.reader(csvdatei, delimiter=',')
        zeilennummer = 0
        for row in csv_reader_object:
            if zeilennummer == 0:
                mp_obj = row[1]
                eta_obj = row[3]
                sp_obj = row[5]
                zeilennummer += 1
            elif zeilennummer == 1:
                zeilennummer += 1
            else:
                it = int(row[0])
                para_kind = row[1]
                para = row[2]
                variable = row[3]
                value = float(row[4])
                if para_kind == 'event':
                    para_list = para.split("'")
                    stop_1 = para_list[1]
                    ankunft_1 = para_list[3]
                    line_1_nr = para_list[5]
                    line_1_zuggruppe = para_list[7]
                    line_1_start = para_list[13]
                    line_1_stop = para_list[15]
                    
                    event = (stop_1, ankunft_1, (line_1_nr, line_1_zuggruppe), (line_1_nr, line_1_zuggruppe, line_1_start, line_1_stop))
            
                    if event not in solution_events:
                        solution_events[event]={}
                    solution_events[event][variable] = value
                    
                elif para_kind == 'activity':
                    para_list = para.split("'")
                    stop_1 = para_list[1]
                    ankunft_1 = para_list[3]
                    line_1_nr = para_list[5]
                    line_1_zuggruppe = para_list[7]
                    line_1_start = para_list[13]
                    line_1_stop = para_list[15]
                    
                    stop_2 = para_list[17]
                    ankunft_2 = para_list[19]
                    line_2_nr = para_list[21]
                    line_2_zuggruppe = para_list[23]
                    line_2_start = para_list[29]
                    line_2_stop = para_list[31]
                    
                    event_1 = (stop_1, ankunft_1, (line_1_nr, line_1_zuggruppe), (line_1_nr, line_1_zuggruppe, line_1_start, line_1_stop))
                    event_2 = (stop_2, ankunft_2, (line_2_nr, line_2_zuggruppe), (line_2_nr, line_2_zuggruppe, line_2_start, line_2_stop))
                    para = (event_1, event_2)   
                    
                    if para not in solution_activities:
                        solution_activities[para]={}
                    solution_activities[para][variable]=value
                    
                zeilennummer += 1
        
        obj_MP[it] = float(mp_obj)
        obj_eta[it] = float(eta_obj)
        obj_SP[it] = float(sp_obj)
        opt_cuts[it]=[solution_events, solution_activities]


###################################################          
########### Feas Cuts LP - TT #####################
###################################################

 
def write_feas_cuts_LP_TT(feas_cuts, it, m_MP):
    with open(r'.\LP_TT\cuts\cut_'+str(it)+'_feas_LP_TT.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        eta_var = m_MP.getVarByName('eta')
        eta = eta_var.x
        writer.writerow(['MP_Obj:', m_MP.objVal, 'eta:', eta])
        writer.writerow([it,'kind of parameter', 'parameter', 'variable', 'value'])
        for para in feas_cuts[it]:
            for variable in feas_cuts[it][para]:
                value = feas_cuts[it][para][variable]
                if variable == 'my':
                    para_kind = 'event'
                else:
                    para_kind = 'activity'
                writer.writerow([it,para_kind, para, variable, value])
    


def read_feas_cuts_LP_TT(feas_cuts, feas_cut_Datei, obj_MP, obj_SP, obj_eta):
    with open("./LP_TT/cuts/"+str(feas_cut_Datei)) as csvdatei:
        print('Reading Data ' + str(feas_cut_Datei))
        csv_reader_object = csv.reader(csvdatei, delimiter=',')
        zeilennummer = 0
        for row in csv_reader_object:
            if zeilennummer == 0:
                mp_obj = row[1]
                eta_obj = row[3]
                zeilennummer += 1
            elif zeilennummer == 1:
                zeilennummer += 1
            else:
                it = int(row[0])
                para_kind = row[1]
                para = row[2]
                variable = row[3]
                value = float(row[4])
                if para_kind == 'event':
                    para_list = para.split("'")
                    stop_1 = para_list[1]
                    ankunft_1 = para_list[3]
                    line_1_nr = para_list[5]
                    line_1_zuggruppe = para_list[7]
                    line_1_start = para_list[13]
                    line_1_stop = para_list[15]
                        
                    para = (stop_1, ankunft_1, (line_1_nr, line_1_zuggruppe), (line_1_nr, line_1_zuggruppe, line_1_start, line_1_stop))
                   
                elif para_kind == 'activity':
                    para_list = para.split("'")
                    stop_1 = para_list[1]
                    ankunft_1 = para_list[3]
                    line_1_nr = para_list[5]
                    line_1_zuggruppe = para_list[7]
                    line_1_start = para_list[13]
                    line_1_stop = para_list[15]
                    
                    stop_2 = para_list[17]
                    ankunft_2 = para_list[19]
                    line_2_nr = para_list[21]
                    line_2_zuggruppe = para_list[23]
                    line_2_start = para_list[29]
                    line_2_stop = para_list[31]
                    
                    event_1 = (stop_1, ankunft_1, (line_1_nr, line_1_zuggruppe), (line_1_nr, line_1_zuggruppe, line_1_start, line_1_stop))
                    event_2 = (stop_2, ankunft_2, (line_2_nr, line_2_zuggruppe), (line_2_nr, line_2_zuggruppe, line_2_start, line_2_stop))
                    para = (event_1, event_2)                     
                    
                if it not in feas_cuts:
                    feas_cuts[it]={}
                if para not in feas_cuts[it]:
                    feas_cuts[it][para]={}
                    
                feas_cuts[it][para][variable] = value
                zeilennummer += 1

        obj_MP[it] = float(mp_obj)    
        obj_eta[it] = float(eta_obj)
        obj_SP[it] = ''
        
        
        
        
        
        
        
        
        
###################################################          
###########  LP - TT    CBD  ######################
###################################################        

def write_solution_objective_and_line_frequencies_LP_TT_CBD_A(obj_MP, obj_eta, obj_SP, it_solution_frequencies):
    with open('solution_Benders_LP_TT_CBD_A.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['iteration', 'MP Objective', 'eta', 'SP Objective', 'Cut type', 'line frequencies'])
        writer.writerow(['','', '', '', '', '', 'S41-A1', 'S41-A2', 'S41-A3', 'S41-A4', '', 'S41I-A1', 'S41I-A2', 'S41I-A3', 'S41I-A4','',  'S45-A1', 'S45-A2', 'S45-A3', '', 'S46-A1', 'S46-A2', 'S46-A3', 'S46-A4', '', 'S47-A1', 'S47-A2', 'S47-A3', 'S47-A4'])
       
        for it in obj_MP:
           objMP = obj_MP[it]
           eta = obj_eta[it]
           if it in obj_SP:
               objSP = obj_SP[it]
               cut_type = 'opt'
           else:
               objSP = ''
               cut_type = 'feas'
           
           try: 
               solution_frequencies = it_solution_frequencies[it]
   
               for line in solution_frequencies:
                   line_nummer = line[0]
                   for line_alternative in solution_frequencies[line]:
                       line_alternative_nummer = line_alternative[2]
                       line_frequency = solution_frequencies[line][line_alternative]
                       if line == ('S41', 'A'):
                           if line_alternative_nummer == 'A1':
                               S41A1 = line_frequency
                           elif line_alternative_nummer == 'A2':
                               S41A2 = line_frequency
                           elif line_alternative_nummer == 'A3':
                               S41A3 = line_frequency
                           elif line_alternative_nummer == 'A4':
                               S41A4 = line_frequency
                       elif line == ('S41', 'AI'):
                            if line_alternative_nummer == 'A1':
                                S41IA1 = line_frequency
                            elif line_alternative_nummer == 'A2':
                                S41IA2 = line_frequency
                            elif line_alternative_nummer == 'A3':
                                S41IA3 = line_frequency
                            elif line_alternative_nummer == 'A4':
                                S41IA4 = line_frequency
                       elif line_nummer == 'S45':
                             if line_alternative_nummer == 'A1':
                                 S45A1 = line_frequency
                             elif line_alternative_nummer == 'A2':
                                 S45A2 = line_frequency
                             elif line_alternative_nummer == 'A3':
                                 S45A3 = line_frequency
                       elif line_nummer == 'S46':
                             if line_alternative_nummer == 'A1':
                                 S46A1 = line_frequency
                             elif line_alternative_nummer == 'A2':
                                 S46A2 = line_frequency
                             elif line_alternative_nummer == 'A3':
                                 S46A3 = line_frequency
                             elif line_alternative_nummer == 'A4':
                                 S46A4 = line_frequency
                       elif line_nummer == 'S47':
                             if line_alternative_nummer == 'A1':
                                 S47A1 = line_frequency
                             elif line_alternative_nummer == 'A2':
                                 S47A2 = line_frequency
                             elif line_alternative_nummer == 'A3':
                                 S47A3 = line_frequency
                             elif line_alternative_nummer == 'A4':
                                 S47A4 = line_frequency
                 
               writer.writerow([it, objMP, eta, objSP, cut_type, '', S41A1, S41A2, S41A3, S41A4, '',  S41IA1, S41IA2, S41IA3, S41IA4,'',  S45A1, S45A2, S45A3, '', S46A1, S46A2, S46A3, S46A4,'', S47A1, S47A2, S47A3, S47A4])
           except:
               writer.writerow([it, objMP, eta, objSP, cut_type])       

        
def write_solution_objective_and_line_frequencies_LP_TT_CBD_B(obj_MP, obj_eta, obj_SP, it_solution_frequencies):
    with open('solution_Benders_LP_TT_CBD_B.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['iteration', 'MP Objective', 'eta', 'SP Objective', 'Cut type', 'line frequencies'])
        writer.writerow(['','', '', '', '', '', 'S41-A1', 'S41-A2', 'S41-A5', 'S41-A6', '', 'S41I-A1', 'S41I-A2', 'S41I-A5', 'S41I-A6','',  'S45-A1', 'S45-A4', 'S45-A5', '', 'S46-A1', 'S46-A2', 'S46-A5', 'S46-A6', '', 'S47-A1', 'S47-A5', 'S47-A6'])
        
        for it in obj_MP:
            objMP = obj_MP[it]
            eta = obj_eta[it]
            if it in obj_SP:
                objSP = obj_SP[it]
                cut_type = 'opt'
            else:
                objSP = ''
                cut_type = 'feas'
            
            try: 
                solution_frequencies = it_solution_frequencies[it]
    
                for line in solution_frequencies:
                    line_nummer = line[0]
                    for line_alternative in solution_frequencies[line]:
                        line_alternative_nummer = line_alternative[2]
                        line_frequency = solution_frequencies[line][line_alternative]
                        if line == ('S41', 'A'):
                            if line_alternative_nummer == 'A1':
                                S41A1 = line_frequency
                            elif line_alternative_nummer == 'A2':
                                S41A2 = line_frequency
                            elif line_alternative_nummer == 'A5':
                                S41A5 = line_frequency
                            elif line_alternative_nummer == 'A6':
                                S41A6 = line_frequency
                        elif line == ('S41', 'AI'):
                             if line_alternative_nummer == 'A1':
                                 S41IA1 = line_frequency
                             elif line_alternative_nummer == 'A2':
                                 S41IA2 = line_frequency
                             elif line_alternative_nummer == 'A5':
                                 S41IA5 = line_frequency
                             elif line_alternative_nummer == 'A6':
                                 S41IA6 = line_frequency
                        elif line_nummer == 'S45':
                              if line_alternative_nummer == 'A1':
                                  S45A1 = line_frequency
                              elif line_alternative_nummer == 'A4':
                                  S45A4 = line_frequency
                              elif line_alternative_nummer == 'A5':
                                  S45A5 = line_frequency
                        elif line_nummer == 'S46':
                              if line_alternative_nummer == 'A1':
                                  S46A1 = line_frequency
                              elif line_alternative_nummer == 'A2':
                                  S46A2 = line_frequency
                              elif line_alternative_nummer == 'A5':
                                  S46A5 = line_frequency
                              elif line_alternative_nummer == 'A6':
                                  S46A6 = line_frequency
                        elif line_nummer == 'S47':
                              if line_alternative_nummer == 'A1':
                                  S47A1 = line_frequency
                              elif line_alternative_nummer == 'A5':
                                  S47A5 = line_frequency
                              elif line_alternative_nummer == 'A6':
                                  S47A6 = line_frequency
                  
                writer.writerow([it, objMP, eta, objSP, cut_type, '', S41A1, S41A2, S41A5, S41A6, '',  S41IA1, S41IA2, S41IA5, S41IA6,'',  S45A1, S45A4, S45A5, '', S46A1, S46A2, S46A5, S46A6,'', S47A1, S47A5, S47A6])
            except:
                writer.writerow([it, objMP, eta, objSP, cut_type])        
                
                
                
                
                
        
        
###################################################          
###########  LP - TT    CB  ######################
###################################################        

def write_solution_objective_and_line_frequencies_LP_TT_CB_A(obj_MP, obj_eta, obj_SP, it_solution_frequencies):
    with open('solution_Benders_LP_TT_CB_A.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['iteration', 'MP Objective', 'eta', 'SP Objective', 'Cut type', 'line frequencies'])
        writer.writerow(['','', '', '', '', '', 'S41-A1', 'S41-A2', 'S41-A3', 'S41-A4', '', 'S41I-A1', 'S41I-A2', 'S41I-A3', 'S41I-A4','',  'S45-A1', 'S45-A2', 'S45-A3', '', 'S46-A1', 'S46-A2', 'S46-A3', 'S46-A4', '', 'S47-A1', 'S47-A2', 'S47-A3', 'S47-A4'])
       
        for it in obj_MP:
           objMP = obj_MP[it]
           eta = obj_eta[it]
           if it in obj_SP:
               objSP = obj_SP[it]
               cut_type = 'opt'
           else:
               objSP = ''
               cut_type = 'feas'
           
           try: 
               solution_frequencies = it_solution_frequencies[it]
   
               for line in solution_frequencies:
                   line_nummer = line[0]
                   for line_alternative in solution_frequencies[line]:
                       line_alternative_nummer = line_alternative[2]
                       line_frequency = solution_frequencies[line][line_alternative]
                       if line == ('S41', 'A'):
                           if line_alternative_nummer == 'A1':
                               S41A1 = line_frequency
                           elif line_alternative_nummer == 'A2':
                               S41A2 = line_frequency
                           elif line_alternative_nummer == 'A3':
                               S41A3 = line_frequency
                           elif line_alternative_nummer == 'A4':
                               S41A4 = line_frequency
                       elif line == ('S41', 'AI'):
                            if line_alternative_nummer == 'A1':
                                S41IA1 = line_frequency
                            elif line_alternative_nummer == 'A2':
                                S41IA2 = line_frequency
                            elif line_alternative_nummer == 'A3':
                                S41IA3 = line_frequency
                            elif line_alternative_nummer == 'A4':
                                S41IA4 = line_frequency
                       elif line_nummer == 'S45':
                             if line_alternative_nummer == 'A1':
                                 S45A1 = line_frequency
                             elif line_alternative_nummer == 'A2':
                                 S45A2 = line_frequency
                             elif line_alternative_nummer == 'A3':
                                 S45A3 = line_frequency
                       elif line_nummer == 'S46':
                             if line_alternative_nummer == 'A1':
                                 S46A1 = line_frequency
                             elif line_alternative_nummer == 'A2':
                                 S46A2 = line_frequency
                             elif line_alternative_nummer == 'A3':
                                 S46A3 = line_frequency
                             elif line_alternative_nummer == 'A4':
                                 S46A4 = line_frequency
                       elif line_nummer == 'S47':
                             if line_alternative_nummer == 'A1':
                                 S47A1 = line_frequency
                             elif line_alternative_nummer == 'A2':
                                 S47A2 = line_frequency
                             elif line_alternative_nummer == 'A3':
                                 S47A3 = line_frequency
                             elif line_alternative_nummer == 'A4':
                                 S47A4 = line_frequency
                 
               writer.writerow([it, objMP, eta, objSP, cut_type, '', S41A1, S41A2, S41A3, S41A4, '',  S41IA1, S41IA2, S41IA3, S41IA4,'',  S45A1, S45A2, S45A3, '', S46A1, S46A2, S46A3, S46A4,'', S47A1, S47A2, S47A3, S47A4])
           except:
               writer.writerow([it, objMP, eta, objSP, cut_type])       

        
def write_solution_objective_and_line_frequencies_LP_TT_CB_B(obj_MP, obj_eta, obj_SP, it_solution_frequencies):
    with open('solution_Benders_LP_TT_CB_B.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['iteration', 'MP Objective', 'eta', 'SP Objective', 'Cut type', 'line frequencies'])
        writer.writerow(['','', '', '', '', '', 'S41-A1', 'S41-A2', 'S41-A5', 'S41-A6', '', 'S41I-A1', 'S41I-A2', 'S41I-A5', 'S41I-A6','',  'S45-A1', 'S45-A4', 'S45-A5', '', 'S46-A1', 'S46-A2', 'S46-A5', 'S46-A6', '', 'S47-A1', 'S47-A5', 'S47-A6'])
        
        for it in obj_MP:
            objMP = obj_MP[it]
            eta = obj_eta[it]
            if it in obj_SP:
                objSP = obj_SP[it]
                cut_type = 'opt'
            else:
                objSP = ''
                cut_type = 'feas'
            
            try: 
                solution_frequencies = it_solution_frequencies[it]
    
                for line in solution_frequencies:
                    line_nummer = line[0]
                    for line_alternative in solution_frequencies[line]:
                        line_alternative_nummer = line_alternative[2]
                        line_frequency = solution_frequencies[line][line_alternative]
                        if line == ('S41', 'A'):
                            if line_alternative_nummer == 'A1':
                                S41A1 = line_frequency
                            elif line_alternative_nummer == 'A2':
                                S41A2 = line_frequency
                            elif line_alternative_nummer == 'A5':
                                S41A5 = line_frequency
                            elif line_alternative_nummer == 'A6':
                                S41A6 = line_frequency
                        elif line == ('S41', 'AI'):
                             if line_alternative_nummer == 'A1':
                                 S41IA1 = line_frequency
                             elif line_alternative_nummer == 'A2':
                                 S41IA2 = line_frequency
                             elif line_alternative_nummer == 'A5':
                                 S41IA5 = line_frequency
                             elif line_alternative_nummer == 'A6':
                                 S41IA6 = line_frequency
                        elif line_nummer == 'S45':
                              if line_alternative_nummer == 'A1':
                                  S45A1 = line_frequency
                              elif line_alternative_nummer == 'A4':
                                  S45A4 = line_frequency
                              elif line_alternative_nummer == 'A5':
                                  S45A5 = line_frequency
                        elif line_nummer == 'S46':
                              if line_alternative_nummer == 'A1':
                                  S46A1 = line_frequency
                              elif line_alternative_nummer == 'A2':
                                  S46A2 = line_frequency
                              elif line_alternative_nummer == 'A5':
                                  S46A5 = line_frequency
                              elif line_alternative_nummer == 'A6':
                                  S46A6 = line_frequency
                        elif line_nummer == 'S47':
                              if line_alternative_nummer == 'A1':
                                  S47A1 = line_frequency
                              elif line_alternative_nummer == 'A5':
                                  S47A5 = line_frequency
                              elif line_alternative_nummer == 'A6':
                                  S47A6 = line_frequency
                  
                writer.writerow([it, objMP, eta, objSP, cut_type, '', S41A1, S41A2, S41A5, S41A6, '',  S41IA1, S41IA2, S41IA5, S41IA6,'',  S45A1, S45A4, S45A5, '', S46A1, S46A2, S46A5, S46A6,'', S47A1, S47A5, S47A6])
            except:
                writer.writerow([it, objMP, eta, objSP, cut_type])        