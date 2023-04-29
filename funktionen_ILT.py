# -*- coding: utf-8 -*-
"""
@author: Sarah Burchert

"""
import gurobipy as gp
from gurobipy import GRB
import funktionen
import funktionen_sol

###################################################
######## GUROBI - MP ##############################
###################################################

def set_up_and_solve_ILT(T, alpha, beta,M, M_2, h, k, events, activities, line_alternatives, edges, lines, stops, write):
    
    ######### Set up ILT ##############################
    
    m = set_up_ILT_model(T, alpha, beta,M, M_2, h, k, events, activities, line_alternatives, edges, lines, write)
    
    ######### Optimization ############################## 

    m.optimize()     
    
            
    ############## Print solution #####################
    
    (m_solution_frequencies, m_solution_events, m_solution_z, m_solution_y) = write_solution_lists(m, alpha, beta, line_alternatives, events, activities, T, k)
  
    return (m, m_solution_frequencies, m_solution_events, m_solution_z, m_solution_y)


###################################################
######## FUNKTIONEN ###############################
###################################################




def write_solution_lists(m, alpha, beta, line_alternatives, events, activities, T, k):
    # solution_frequencies = { line: { line_alternative: frequency }}
    solution_frequencies = {}
    # solution_events = {event: timetable}
    solution_events = {}
    # solution_z = {activity: z}
    solution_z = {}
    #solution_y = {activity: y}
    solution_y = {}
    
    if m.Status == GRB.OPTIMAL:
        solution_frequencies = funktionen_sol.create_solution_frequencies(m, line_alternatives)
        solution_events = funktionen_sol.create_solution_events(m, events)    
        solution_z = funktionen_sol.create_solution_z(m, activities)
        solution_y = funktionen_sol.create_solution_y(m, activities)

        print('Obj: %g' % m.objVal)
        sol_obj_LP = funktionen_sol.get_LP_objective(alpha, line_alternatives, solution_frequencies)
        print('Obj LP: ' + str(sol_obj_LP))           
        sol_obj_TT = funktionen_sol.get_TT_objective(beta, activities, solution_y)
        print('Obj TT: ' + str(sol_obj_TT))
      
        funktionen_sol.write_solution(m, "ILT")
        funktionen_sol.write_solution_frequencies(m, 'ILT', solution_frequencies)
        funktionen_sol.write_solution_timetable_for_lines(m, 'ILT', line_alternatives, solution_frequencies, solution_events, T, k)
        #funktionen_sol.write_solution_not_active_timetable_for_lines(m, 'ILT', line_alternatives, solution_frequencies, solution_events, T, k)
    return(solution_frequencies, solution_events, solution_z, solution_y)



def set_up_ILT_model(T, alpha, beta,M, M_2, h, k, events, activities, line_alternatives, edges, lines, write):
    m = gp.Model('ILT')
    list_of_not_fixed_events = funktionen.get_list_of_not_fixed_events(events)
    list_of_all_activities = funktionen.get_list_of_all_activities(activities)
    list_of_wait_activities = funktionen.get_list_of_wait_activities(activities)
    list_of_drive_activities = funktionen.get_list_of_drive_activities(activities)
    list_of_wende_activities = funktionen.get_list_of_wende_activities(activities)
    list_of_trans_activities = funktionen.get_list_of_trans_activities(activities)
    list_of_headway_activities = funktionen.get_list_of_headway_activities(activities)
    list_of_active_edges = funktionen.get_list_of_active_edges(edges)
    list_of_fixed_lines = funktionen.get_list_of_fixed_lines(lines, line_alternatives)
    
    ############ Create variables #####################
    time = m.addVars(list_of_not_fixed_events, lb=0, ub = T-1, vtype=GRB.INTEGER, name="time")
    zwait=m.addVars(list_of_wait_activities,lb=-2, ub = 2, vtype=GRB.INTEGER, name="zwait")
    zdrive=m.addVars(list_of_drive_activities, lb=-2, ub = 2, vtype=GRB.INTEGER, name="zdrive")
    zwende=m.addVars(list_of_wende_activities, lb=-2, ub = 2, vtype=GRB.INTEGER, name="zwende")
    ztrans=m.addVars(list_of_trans_activities, lb=-2, ub = 2, vtype=GRB.INTEGER, name="ztrans")                 
    zhead=m.addVars(list_of_headway_activities, lb=-2, ub = 2, vtype=GRB.INTEGER, name="zhead")
    y = m.addVars(list_of_all_activities, lb =0, name="y_a")

    f_line_alternative={}
    for line in line_alternatives:
        list_of_line_alternatives = line_alternatives[line]
        f_line_alternative[line]=m.addVars(list_of_line_alternatives, vtype=GRB.BINARY, name='f')


    ############ Create objective #####################
    obj=gp.LinExpr()
    obj_LP=gp.LinExpr()
    obj_TT=gp.LinExpr()

    #line costs
    for line in line_alternatives:
        for line_alternative in line_alternatives[line]:
            line_cost = line_alternatives[line][line_alternative][0]
            obj_LP += f_line_alternative[line][line_alternative] * float(line_cost)

    #timetable costs        
    for activity in activities:
        activity_weight = activities[activity][2]  
        obj_TT += activity_weight * y[activity]
            
    obj = alpha * obj_LP + beta * obj_TT
        
    m.setObjective(obj, GRB.MINIMIZE)        
            
            
    ######### Create constraints ######################
    zaehler_1 = 0
    zaehler_2 = 0
    zaehler_3 = 0
    zaehler_4 = 0
    zaehler_5 = 0
    zaehler_6 = 0 
    zaehler_7 = 0
    zaehler_8 = 0
    zaehler_9 = 0
    zaehler_10 = 0
    zaehler_11 = 0
    zaehler_12 = 0
    zaehler_13 = 0
    zaehler_14 = 0
    zaehler_15 = 0
    zaehler_16 = 0
    zaehler_17 = 0
    zaehler_18 = 0
    zaehler_20 = 0


    # min frequency constraint
    for edge in list_of_active_edges:
        f_min = edges[edge][3]
        con=gp.LinExpr()      
        
        for line in line_alternatives: 
            for line_alternative in line_alternatives[line]:
                for line_richtung in line_alternatives[line][line_alternative][1]:
                    line_edge_list = line_alternatives[line][line_alternative][1][line_richtung][1]
                    for line_edge in line_edge_list:
                        if line_edge == edge:
                            con += f_line_alternative[line][line_alternative]
        for line in list_of_fixed_lines:
            for line_richtung in lines[line]:
                line_edge_list=lines[line][line_richtung][2]
                for line_edge in line_edge_list:
                    if line_edge == edge:
                        con += 1
        m.addConstr(con >= f_min, "min_freuquency %s" %str(edge))
        zaehler_1 += 1
        

    # max frequency constraint
    for edge in list_of_active_edges:
        f_max = edges[edge][4]
        con=gp.LinExpr()      
        
        for line in line_alternatives: 
            for line_alternative in line_alternatives[line]:
                for line_richtung in line_alternatives[line][line_alternative][1]:
                    line_edge_list = line_alternatives[line][line_alternative][1][line_richtung][1]
                    for line_edge in line_edge_list:
                        if line_edge == edge:
                            con += f_line_alternative[line][line_alternative]
        for line in list_of_fixed_lines:
            for line_richtung in lines[line]:
                line_edge_list=lines[line][line_richtung][2]
                for line_edge in line_edge_list:
                    if line_edge == edge:
                        con += 1
        m.addConstr(con <= f_max, "max_freuquency %s" %str(edge))
        zaehler_2 += 1
            
      # frequence of line alternatives
        for line in line_alternatives:
            con=gp.LinExpr()
            for line_alternative in line_alternatives[line]:
                con += f_line_alternative[line][line_alternative]
            m.addConstr(con == 1, "choose one line alternative%s" %str(line))
            zaehler_3 += 1     
    
    
    # lower and upper bound timetable, y_a bound - wait
    for activity in list_of_wait_activities:
        con = gp.LinExpr()
        
        event_1 = activity[0]
        event_2 = activity[1]
        La = activities[activity][0]
        Ua = activities[activity][1]  
        stop = event_1[0]
        line = event_1[2]
        line_original_richtung = event_1[3]
        
        for line_alternative in line_alternatives[line]:
            for line_richtung in line_alternatives[line][line_alternative][1]:
                if line_original_richtung == (line_richtung[0], line_richtung[1], line_richtung[3], line_richtung[4]):
                    list_of_line_stops = line_alternatives[line][line_alternative][1][line_richtung][0]
                    for line_stop in list_of_line_stops:
                        endstelle = line_alternatives[line][line_alternative][1][line_richtung][0][line_stop]
                        if stop == line_stop and endstelle == '':
                            con += f_line_alternative[line][line_alternative] 
        m.addConstr( time[event_2]- time[event_1] + zwait[activity]*T >= con * La, "lower_bound_timetable wait %s" %str(activity))
        m.addConstr( time[event_2]- time[event_1] + zwait[activity]*T <= Ua + M* (1 - con),  "upper_bound_timetable wait %s" %str(activity))
        m.addConstr( y[activity] >= time[event_2]- time[event_1] + zwait[activity]*T - M_2 * (1 - con),  "y_a_bound wait %s" %str(activity))
        zaehler_4 += 1
        zaehler_5 += 1
        zaehler_14 += 1
        

    # lower and upper bound timetable, y_a bound- drive
    for activity in list_of_drive_activities:
        con = gp.LinExpr()
        
        event_1 = activity[0]
        event_2 = activity[1]
        La = activities[activity][0]
        Ua = activities[activity][1]
        stop_1 = event_1[0]
        stop_2 = event_2[0]
        line = event_1[2]
        edge = (stop_1, stop_2)
        line_original_richtung = event_1[3]
        
        for line_alternative in line_alternatives[line]:
            for line_richtung in line_alternatives[line][line_alternative][1]:
                if line_original_richtung == (line_richtung[0], line_richtung[1], line_richtung[3], line_richtung[4]):
                    list_of_line_edges = line_alternatives[line][line_alternative][1][line_richtung][1]
                    if edge in list_of_line_edges:
                        con += f_line_alternative[line][line_alternative]    
        m.addConstr( time[event_2]- time[event_1] + zdrive[activity]*T >= con * La, "lower_bound_timetable drive %s" %str(activity))
        m.addConstr( time[event_2]- time[event_1] + zdrive[activity]*T <= Ua + M* (1 - con),  "upper_bound_timetable drive %s" %str(activity))
        m.addConstr( y[activity] >= time[event_2]- time[event_1] + zdrive[activity]*T - M_2 * (1 - con),  "y_a_bound drive %s" %str(activity))
        zaehler_6 += 1
        zaehler_7 += 1 
        zaehler_15 += 1

    # lower and upper bound timetable, y_a bound - wende
    for activity in list_of_wende_activities:
        con = gp.LinExpr()
        
        event_1 = activity[0]
        event_2 = activity[1]
        La = activities[activity][0]
        Ua = activities[activity][1]  
        stop = event_1[0]
        line = event_1[2]
        event_1_original_richtung = event_1[3]
        event_2_original_richtung = event_2[3]

        for line_alternative in line_alternatives[line]:   
            for line_richtung_1 in line_alternatives[line][line_alternative][1]:
                if event_1_original_richtung == (line_richtung_1[0], line_richtung_1[1], line_richtung_1[3], line_richtung_1[4]):
                    for line_richtung_2 in line_alternatives[line][line_alternative][1]:
                        if event_2_original_richtung == (line_richtung_2[0], line_richtung_2[1], line_richtung_2[3], line_richtung_2[4]):
                            list_of_stops_1 = line_alternatives[line][line_alternative][1][line_richtung_1][0]
                            list_of_stops_2 = line_alternatives[line][line_alternative][1][line_richtung_2][0]
                            if stop in list_of_stops_1 and stop in list_of_stops_2:
                                 endstelle_1 =  line_alternatives[line][line_alternative][1][line_richtung_1][0][stop]
                                 endstelle_2 =  line_alternatives[line][line_alternative][1][line_richtung_2][0][stop]
                                 if endstelle_1 == 'end' and endstelle_2 == 'start':
                                     con += f_line_alternative[line][line_alternative]   
        m.addConstr( time[event_2]- time[event_1] + zwende[activity]*T >= con * La, "lower_bound_timetable wende %s" %str(activity))
        m.addConstr( time[event_2]- time[event_1] + zwende[activity]*T <= Ua + M* (1 - con),  "upper_bound_timetable wende %s" %str(activity))
        m.addConstr( y[activity] >= time[event_2]- time[event_1] + zwende[activity]*T - M_2 * (1 - con),  "y_a_bound wende %s" %str(activity))
        zaehler_8 += 1
        zaehler_9 += 1 
        zaehler_16 += 1

    # lower and upper bound timetable, y_a bound - transfer         
    for activity in list_of_trans_activities:
        con_1 = gp.LinExpr()
        con_2 = gp.LinExpr()
        event_1 = activity[0]
        event_2 = activity[1]
        La = activities[activity][0]
        Ua = activities[activity][1]  
        stop = event_1[0]
        line_1 = event_1[2]
        line_1_original_richtung = event_1[3]
        line_2 = event_2[2]
        line_2_original_richtung = event_2[3]
        
        if line_1 in line_alternatives:
            for line_alternative in line_alternatives[line_1]:    
                for line_richtung_1 in line_alternatives[line_1][line_alternative][1]:
                    if line_1_original_richtung == (line_richtung_1[0], line_richtung_1[1], line_richtung_1[3], line_richtung_1[4]):
                        list_of_stops_1 = line_alternatives[line_1][line_alternative][1][line_richtung_1][0]    
                        if stop in list_of_stops_1:
                            con_1 += f_line_alternative[line_1][line_alternative]
                           
        if line_2 in line_alternatives:
            for line_alternative in line_alternatives[line_2]:    
                for line_richtung_2 in line_alternatives[line_2][line_alternative][1]:
                    if line_2_original_richtung == (line_richtung_2[0], line_richtung_2[1], line_richtung_2[3], line_richtung_2[4]):
                        list_of_stops_2 = line_alternatives[line_2][line_alternative][1][line_richtung_2][0]    
                        if stop in list_of_stops_2:
                            con_2 += f_line_alternative[line_2][line_alternative]
                        
        if line_1 in line_alternatives and line_2 in line_alternatives:
            m.addConstr( time[event_2] - time[event_1] + ztrans[activity]*T >= (con_1 + con_2 -1) * La, "lower_bound_timetable trans %s" %str(activity))
            m.addConstr( time[event_2] - time[event_1] + ztrans[activity]*T <= Ua + M* (2 -con_1 - con_2),  "upper_bound_timetable trans %s" %str(activity))
            m.addConstr( y[activity] >= time[event_2] - time[event_1] + ztrans[activity]*T - M_2 * (2 -con_1 - con_2),  "y_a_bound trans %s" %str(activity))
            zaehler_10 += 1
            zaehler_11 += 1   
            zaehler_17 += 1
        
        if line_1 not in line_alternatives:
            time_1 = int(events[event_1][1])
            m.addConstr( time[event_2] - time_1 + ztrans[activity]*T >=  con_2  * La, "lower_bound_timetable trans %s" %str(activity))
            m.addConstr( time[event_2] - time_1 + ztrans[activity]*T <= Ua + M* (1 - con_2),  "upper_bound_timetable trans %s" %str(activity))
            m.addConstr( y[activity] >= time[event_2] - time_1 + ztrans[activity]*T - M_2 * (1 - con_2),  "y_a_bound trans %s" %str(activity))
            zaehler_10 += 1
            zaehler_11 += 1 
            zaehler_17 += 1
        
        if line_2 not in line_alternatives:
            time_2 = int(events[event_2][1])
            m.addConstr( time_2 - time[event_1] + ztrans[activity]*T >=  con_1  * La, "lower_bound_timetable trans %s" %str(activity))
            m.addConstr( time_2 - time[event_1] + ztrans[activity]*T <= Ua + M* (1 - con_1),  "upper_bound_timetable trans %s" %str(activity))
            m.addConstr( y[activity] >= time_2 - time[event_1] + ztrans[activity]*T - M_2 * (1 - con_1),  "y_a_bound trans %s" %str(activity))
            zaehler_10 += 1
            zaehler_11 += 1 
            zaehler_17 +=1


    # lower and upper bound timetable, y_a bound - headway 
    for activity in list_of_headway_activities:
        con_1 = gp.LinExpr()
        con_2 = gp.LinExpr()


        event_1 = activity[0]
        event_2 = activity[1]
        event_1_ankunft = event_1[1]
        event_2_ankunft = event_2[1]
        line_1 = event_1[2]
        line_1_original_richtung = event_1[3]
        line_2 = event_2[2]
        line_2_original_richtung = event_2[3]
        stop = event_1[0]
        
        if line_1 in line_alternatives:
            for line_alternative in line_alternatives[line_1]:    
                for line_richtung_1 in line_alternatives[line_1][line_alternative][1]:
                    if line_1_original_richtung == (line_richtung_1[0], line_richtung_1[1], line_richtung_1[3], line_richtung_1[4]):
                        list_of_stops_1 = line_alternatives[line_1][line_alternative][1][line_richtung_1][0]    
                        if stop in list_of_stops_1:
                            stop_endstelle = line_alternatives[line_1][line_alternative][1][line_richtung_1][0][stop]
                            if stop_endstelle == '':
                                con_1 += f_line_alternative[line_1][line_alternative]
                            if stop_endstelle == 'start':
                                if event_1_ankunft == 'dep':
                                    con_1 += f_line_alternative[line_1][line_alternative]
                            if stop_endstelle == 'end':
                                if event_1_ankunft == 'arr':
                                    con_1 += f_line_alternative[line_1][line_alternative]
        if line_2 in line_alternatives:
            for line_alternative in line_alternatives[line_2]:    
                for line_richtung_2 in line_alternatives[line_2][line_alternative][1]:
                    if line_2_original_richtung == (line_richtung_2[0], line_richtung_2[1], line_richtung_2[3], line_richtung_2[4]):
                        list_of_stops_2 = line_alternatives[line_2][line_alternative][1][line_richtung_2][0]    
                        if stop in list_of_stops_2:
                            stop_endstelle = line_alternatives[line_2][line_alternative][1][line_richtung_2][0][stop]
                            if stop_endstelle == '':
                                con_2 += f_line_alternative[line_2][line_alternative]
                            if stop_endstelle == 'start':
                                if event_1_ankunft == 'dep':
                                    con_2 += f_line_alternative[line_2][line_alternative]
                            if stop_endstelle == 'end':
                                if event_2_ankunft == 'arr':
                                    con_2 += f_line_alternative[line_2][line_alternative]

        
        if line_1 in line_alternatives and line_2 in line_alternatives:
            m.addConstr( time[event_2] - time[event_1] + zhead[activity]*T >= h *(con_1 + con_2 -1), "lower_bound_ timetable headway %s" %str(activity))
            m.addConstr( time[event_2] - time[event_1] + zhead[activity]*T <= T-h + M* (2 - con_1 -con_2),  "upper_bound_timetable headway %s" %str(activity))
            m.addConstr( y[activity] >= time[event_2] - time[event_1] + zhead[activity]*T - M_2 * (2 - con_1 -con_2),  "y_a_bound headway %s" %str(activity))
            zaehler_12 += 1
            zaehler_13 += 1
            zaehler_18 += 1
        
        if line_1 not in line_alternatives:
            time_1 = int(events[event_1][1])
            m.addConstr( time[event_2] - time_1 + zhead[activity]*T >=  h * con_2, "lower_bound_ timetable headway %s" %str(activity))
            m.addConstr( time[event_2] - time_1 + zhead[activity]*T <= T-h + M*(1-con_2),  "upper_bound_timetable headway %s" %str(activity))
            m.addConstr( y[activity] >= time[event_2] - time_1 + zhead[activity]*T - M_2 *(1-con_2),  "y_a_bound headway %s" %str(activity))
            zaehler_12 += 1
            zaehler_13 += 1 
            zaehler_18 += 1
        
        if line_2 not in line_alternatives:
            time_2 = int(events[event_2][1])
            m.addConstr( time_2 - time[event_1] + zhead[activity]*T >=  h * con_1, "lower_bound_ timetable headway %s" %str(activity))
            m.addConstr( time_2 - time[event_1] + zhead[activity]*T <= T-h + M *(1-con_1),  "upper_bound_timetable headway %s" %str(activity))
            m.addConstr( y[activity] >=  time_2 - time[event_1] + zhead[activity]*T - M_2 *(1-con_1),  "y_a_bound headway %s" %str(activity))
            zaehler_12 += 1
            zaehler_13 += 1 
            zaehler_18 += 1


    # activity duration lower bound
    
    for activity in activities:
        event_1 = activity[0]
        event_2 = activity[1]
        line_1 = event_1[2]
        line_2 = event_2[2]
        activity_type = activities[activity][3]
        if activity_type == 'wait':
            m.addConstr( time[event_2] - time[event_1] + zwait[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            zaehler_20 += 1
        elif activity_type == 'drive':
            m.addConstr( time[event_2] - time[event_1] + zdrive[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            zaehler_20 += 1
        elif activity_type == 'wende':
            m.addConstr( time[event_2] - time[event_1] + zwende[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            zaehler_20 += 1
        elif activity_type == 'trans':
            if line_1 in line_alternatives and line_2 in line_alternatives:
                m.addConstr( time[event_2] - time[event_1] + ztrans[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            elif line_1 not in line_alternatives:
                time_1 = int(events[event_1][1])
                m.addConstr( time[event_2] - time_1 + ztrans[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            elif line_2 not in line_alternatives:
                time_2 = int(events[event_2][1])
                m.addConstr( time_2 - time[event_1] + ztrans[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            zaehler_20 += 1  
        elif activity_type == 'headway':
            if line_1 in line_alternatives and line_2 in line_alternatives:
                m.addConstr( time[event_2] - time[event_1] + zhead[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            elif line_1 not in line_alternatives:
                time_1 = int(events[event_1][1])
                m.addConstr( time[event_2] - time_1 + zhead[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            elif line_2 not in line_alternatives:
                time_2 = int(events[event_2][1])
                m.addConstr( time_2 - time[event_1] + zhead[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            zaehler_20 += 1
            

    
    ### print number of variables and constraints ######
    print()
    print('OPTIMIZATION:')
    print('Constraints: ')
    print(' min-frequency (1): ' + str(zaehler_1))
    print(' max frequency (2): ' + str(zaehler_2))
    print(' frequency lines under construction (3): ' + str(zaehler_3))
    print(' timetable wait (4)): ' + str(zaehler_4))
    print(' timetable wait (5): ' + str(zaehler_5))
    print(' timetable drive (4): ' + str(zaehler_6))
    print(' timetable drive (5): ' + str(zaehler_7))
    print(' timetable wende (4): ' + str(zaehler_8))
    print(' timetable wende (5): ' + str(zaehler_9))
    print(' timetable trans (4): ' + str(zaehler_10))
    print(' timetable trans (5): ' + str(zaehler_11))
    print(' timetable head (4): ' + str(zaehler_12))
    print(' timetable head (5): ' + str(zaehler_13))
    print(' y_a bounds wait (6): ' + str(zaehler_14))
    print(' y_a bounds drive (6): ' + str(zaehler_15))
    print(' y_a bounds wende (6): ' + str(zaehler_16))
    print(' y_a bounds trans (6): ' + str(zaehler_17))
    print(' y_a bounds head (6): ' + str(zaehler_18))
    print(' activity duration bounds (7): ' + str(zaehler_20))
    print()
    
    if write == True:
        m.write("write_LP_Datei_ILT.lp")
    
    return(m)