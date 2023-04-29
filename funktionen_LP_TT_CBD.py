# -*- coding: utf-8 -*-
"""
@author: Sarah Burchert

"""
import gurobipy as gp
from gurobipy import GRB
import funktionen
import funktionen_sol


###################################################
############## Master Problem #####################
###################################################


########### Set up and solve MP ###################

def set_up_and_solve_MP(iteration, opt_cuts, feas_cuts, T, alpha,M,M_2, h, k, events, activities, line_alternatives, edges, lines, stops, L_TT):
    
    m_iMP = set_up_LP_TT_MP(iteration, opt_cuts, feas_cuts, T, alpha, M,M_2, h, k, events, activities, line_alternatives, edges, lines, L_TT)
    
    ######### Optimieren ##########################
       
    m_iMP.optimize()     

    ############## Print solution #################
    if m_iMP.Status == GRB.OPTIMAL:
        solution_frequencies = funktionen_sol.create_solution_frequencies(m_iMP, line_alternatives)
    
        print('Obj: %g' % m_iMP.objVal)       
    
        funktionen_sol.write_solution_LP_TT(m_iMP, 'LP_TT_'+str(iteration)+'_MP')
        funktionen_sol.write_solution_frequencies_LP_TT(m_iMP, 'LP_TT_'+str(iteration)+'_MP', solution_frequencies)
        return(m_iMP, solution_frequencies)
    else: 
        print('Hier ist das MP nicht optimal')


############# Set up MP ###########################

def set_up_LP_TT_MP(iteration, opt_cuts, feas_cuts, T, alpha,M,M_2, h, k, events, activities, line_alternatives, edges, lines, L_TT):   
    m = gp.Model(str(iteration)+'_MP')
    
    list_of_active_edges = funktionen.get_list_of_active_edges(edges)
    list_of_fixed_lines = funktionen.get_list_of_fixed_lines(lines, line_alternatives)
    
    ############ Create variables #####################
    
    f_line_alternative={}
    for line in line_alternatives:
        list_of_line_alternatives = line_alternatives[line]
        f_line_alternative[line]=m.addVars(list_of_line_alternatives, vtype=GRB.BINARY, name='f')
    
    eta = m.addVar(lb=-float('inf'), name="eta")
    
    ############ Create objective #####################
    obj=gp.LinExpr()
    obj_LP=gp.LinExpr()
    
    
    #line costs
    for line in line_alternatives:
        for line_alternative in line_alternatives[line]:
            line_cost = line_alternatives[line][line_alternative][0]
            obj_LP += f_line_alternative[line][line_alternative] * float(line_cost)
    if len(opt_cuts) == 0:
        obj = alpha*obj_LP
    else:
        obj = alpha * obj_LP + eta
    m.setObjective(obj, GRB.MINIMIZE)        
            
            
    ######### Create constraints ######################
    zaehler_1 = 0
    zaehler_2 = 0
    zaehler_3 = 0
    zaehler_4 = 0
    zaehler_5 = 0
    
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
                if edge in line_edge_list:
                    con += 1
        m.addConstr(con >= f_min, "min_frequency %s" %str(edge))
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
                if edge in line_edge_list:
                    con += 1
        m.addConstr(con <= f_max, "max_frequency %s" %str(edge))
        zaehler_2 += 1
        
    # frequence of line alternatives
    for line in line_alternatives:
          con=gp.LinExpr()
          for line_alternative in line_alternatives[line]:
              con += f_line_alternative[line][line_alternative]
          m.addConstr(con == 1, "choose one line alternative%s" %str(line))     
          zaehler_3 += 1
    
    # optimality cuts
    for i in opt_cuts:
        solution_objective = opt_cuts[i][0]
        solution_frequencies_cut = opt_cuts[i][1]
        
        opt_cut = gp.LinExpr()
        con=gp.LinExpr()
        for line in solution_frequencies_cut:
            for line_alternative in solution_frequencies_cut[line]:
                fixed_frequency = solution_frequencies_cut[line][line_alternative]
                if fixed_frequency == 0:
                    con+= f_line_alternative[line][line_alternative]
                elif fixed_frequency == 1: 
                    con+= (1-f_line_alternative[line][line_alternative])
        opt_cut = solution_objective  - (solution_objective - L_TT)*con           
        m.addConstr(opt_cut <= eta, "optimality_cut %s" %str(iteration))
        zaehler_4 += 1


    # feasibility cuts
    for i in feas_cuts:
        solution_frequencies_cut = feas_cuts[i]
         
        feas_cut = gp.LinExpr()
        for line in solution_frequencies_cut:
            for line_alternative in solution_frequencies_cut[line]:
                fixed_frequency = solution_frequencies_cut[line][line_alternative]
                if fixed_frequency == 0:
                    feas_cut+= f_line_alternative[line][line_alternative]
                elif fixed_frequency == 1: 
                    feas_cut+= (1-f_line_alternative[line][line_alternative])
         
        m.addConstr(feas_cut >= 1, "feasibility_cut %s" %str(iteration))
        zaehler_5 += 1
    
    
    ##### Ausgabe Anzahl Variablen/Constraints ########
    print()
    print('OPTMIERUNG:')
    print('Constraints for MP: ')
    print(' min-frequency ' + str(zaehler_1))
    print(' max frequency ' + str(zaehler_2))
    print(' frequency lines under construction ' + str(zaehler_3))
    print(' optimality cuts: ' + str(zaehler_4))
    print(' feasibility cuts: ' + str(zaehler_5))
    print()
   
    m.write(r'.\LP_TT_CBD\LP-Dateien\LP_Datei_LP_TT_CBD_'+str(iteration)+'_MP.lp')
    
    return(m)











###################################################
########integer Subproblem ########################
###################################################

def set_up_and_solve_integer_Subproblem(iteration, opt_cuts, feas_cuts, solution_frequencies, beta, h, edges, events, activities, line_alternatives, T, M ,M_2,  k):
    
    ######### Set up Subproblem ###################
    m_SP = set_up_LP_TT_integer_Subproblem(iteration, solution_frequencies, beta, h, edges, events, activities, line_alternatives, T, M ,M_2,  k)

    ######### Optimieren ############################## 

    m_SP.optimize()        
    print()
            
    ############## Print solution #####################
    
    if m_SP.Status == GRB.OPTIMAL:
        print('Obj: %g' % m_SP.objVal)       
    
        #funktionen_sol.write_solution_LP_TT(m_SP, 'LP_TT_'+str(iteration)+'_SP')
        
        opt_cuts[iteration]=[m_SP.objVal, solution_frequencies]
    
    else:
        m_SP.setParam(GRB.Param.DualReductions, 0)     # um zu sehen, ob infeasible or unbounded
        m_SP.optimize()
        
        if m_SP.Status == GRB.INFEASIBLE:
            print()
            print('INFEASIBLE')     
            feas_cuts[iteration]=solution_frequencies
            
        if m_SP.Status == GRB.UNBOUNDED:
            m_SP.setParam(GRB.Param.InfUnbdInfo, 1)
            m_SP.optimize()
                    
            print('UNBOUNDED')
            #unbounded_ray = {}
            #for v in m_SP.getVars():
            #     unbounded_ray[v]=v.UnbdRay
            #for v in unbounded_ray:
            #     if unbounded_ray[v] != 0:
            #         print(v, unbounded_ray[v])
             
            #solution_ray={}
            #get_solution_ray(m_SP, solution_ray, events, activities )
            #x = calculate_feas_cut(solution_ray, solution_frequencies, T, M, M_2, events, activities, line_alternatives)
            #if x > 0:
             #    feas_cuts[iteration]=solution_ray
            #else:
             #    print('Hinweis: Hier ist unbounded ray, aber ... <=0')
                    
    iteration += 1
    return(m_SP, iteration)


###################################################
######## set Up integer SubProblem ################
###################################################

def set_up_LP_TT_integer_Subproblem(iteration, solution_frequencies, beta, h, edges, events, activities, line_alternatives, T, M ,M_2, k):

    m_SP = gp.Model(str(iteration)+'_SP')
    
    list_of_not_fixed_events = funktionen.get_list_of_not_fixed_events(events)
    list_of_all_activities = funktionen.get_list_of_all_activities(activities)
    list_of_wait_activities = funktionen.get_list_of_wait_activities(activities)
    list_of_drive_activities = funktionen.get_list_of_drive_activities(activities)
    list_of_wende_activities = funktionen.get_list_of_wende_activities(activities)
    list_of_trans_activities = funktionen.get_list_of_trans_activities(activities)
    list_of_headway_activities = funktionen.get_list_of_headway_activities(activities)
    
    ############ Create variables #####################
    time = m_SP.addVars(list_of_not_fixed_events, lb = 0, ub = T-1, vtype=GRB.INTEGER, name="time")
    zwait= m_SP.addVars(list_of_wait_activities,lb=-2, ub = 2, vtype=GRB.INTEGER, name="zwait")
    zdrive= m_SP.addVars(list_of_drive_activities, lb=-2, ub = 2, vtype=GRB.INTEGER, name="zdrive")
    zwende= m_SP.addVars(list_of_wende_activities, lb=-2, ub = 2, vtype=GRB.INTEGER, name="zwende")
    ztrans= m_SP.addVars(list_of_trans_activities, lb=-2, ub = 2, vtype=GRB.INTEGER, name="ztrans")                 
    zhead= m_SP.addVars(list_of_headway_activities, lb=-2, ub = 2, vtype=GRB.INTEGER, name="zhead")
    y = m_SP.addVars(list_of_all_activities,  lb=0, name="y_a")
     
    ############ Create objective #####################
    obj_SP=gp.LinExpr()
    obj=gp.LinExpr()
    #timetable costs        
    for activity in activities:
        activity_weight = activities[activity][2]  
        obj += activity_weight * y[activity]         
             
    obj_SP = beta * obj
         
    m_SP.setObjective(obj_SP, GRB.MINIMIZE)        
            
            
    ######### Create constraints ######################
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
                           con += solution_frequencies[line][line_alternative] 
       m_SP.addConstr( time[event_2]- time[event_1] + zwait[activity]*T >= con * La, "lower_bound_timetable wait %s" %str(activity))
       m_SP.addConstr( time[event_2]- time[event_1] + zwait[activity]*T <= Ua + M* (1 - con),  "upper_bound_timetable wait %s" %str(activity))
       m_SP.addConstr( y[activity] >= time[event_2]- time[event_1] + zwait[activity]*T - M_2 * (1 - con),  "y_a_bound wait %s" %str(activity))
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
                       con += solution_frequencies[line][line_alternative]    
       m_SP.addConstr( time[event_2]- time[event_1] + zdrive[activity]*T >= con * La, "lower_bound_timetable drive %s" %str(activity))
       m_SP.addConstr( time[event_2]- time[event_1] + zdrive[activity]*T <= Ua + M* (1 - con),  "upper_bound_timetable drive %s" %str(activity))
       m_SP.addConstr( y[activity] >= time[event_2]- time[event_1] + zdrive[activity]*T - M_2 * (1 - con),  "y_a_bound drive %s" %str(activity))
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
                                    con += solution_frequencies[line][line_alternative]   
       m_SP.addConstr( time[event_2]- time[event_1] + zwende[activity]*T >= con * La, "lower_bound_timetable wende %s" %str(activity))
       m_SP.addConstr( time[event_2]- time[event_1] + zwende[activity]*T <= Ua + M* (1 - con),  "upper_bound_timetable wende %s" %str(activity))
       m_SP.addConstr( y[activity] >= time[event_2]- time[event_1] + zwende[activity]*T - M_2 * (1 - con),  "y_a_bound wende %s" %str(activity))
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
                           con_1 += solution_frequencies[line_1][line_alternative]
                          
       if line_2 in line_alternatives:
           for line_alternative in line_alternatives[line_2]:    
               for line_richtung_2 in line_alternatives[line_2][line_alternative][1]:
                   if line_2_original_richtung == (line_richtung_2[0], line_richtung_2[1], line_richtung_2[3], line_richtung_2[4]):
                       list_of_stops_2 = line_alternatives[line_2][line_alternative][1][line_richtung_2][0]    
                       if stop in list_of_stops_2:
                           con_2 += solution_frequencies[line_2][line_alternative]
                       
       if line_1 in line_alternatives and line_2 in line_alternatives:
           m_SP.addConstr( time[event_2] - time[event_1] + ztrans[activity]*T >= (con_1 + con_2 -1) * La, "lower_bound_timetable trans %s" %str(activity))
           m_SP.addConstr( time[event_2] - time[event_1] + ztrans[activity]*T <= Ua + M* (2 -con_1 - con_2),  "upper_bound_timetable trans %s" %str(activity))
           m_SP.addConstr( y[activity] >= time[event_2] - time[event_1] + ztrans[activity]*T - M_2 * (2 -con_1 - con_2),  "y_a_bound trans %s" %str(activity))
           zaehler_10 += 1
           zaehler_11 += 1   
           zaehler_17 += 1
       
       if line_1 not in line_alternatives:
           time_1 = int(events[event_1][1])
           m_SP.addConstr( time[event_2] - time_1 + ztrans[activity]*T >=  con_2  * La, "lower_bound_timetable trans %s" %str(activity))
           m_SP.addConstr( time[event_2] - time_1 + ztrans[activity]*T <= Ua + M* (1 - con_2),  "upper_bound_timetable trans %s" %str(activity))
           m_SP.addConstr( y[activity] >= time[event_2] - time_1 + ztrans[activity]*T - M_2 * (1 - con_2),  "y_a_bound trans %s" %str(activity))
           zaehler_10 += 1
           zaehler_11 += 1 
           zaehler_17 += 1
       
       if line_2 not in line_alternatives:
           time_2 = int(events[event_2][1])
           m_SP.addConstr( time_2 - time[event_1] + ztrans[activity]*T >=  con_1  * La, "lower_bound_timetable trans %s" %str(activity))
           m_SP.addConstr( time_2 - time[event_1] + ztrans[activity]*T <= Ua + M* (1 - con_1),  "upper_bound_timetable trans %s" %str(activity))
           m_SP.addConstr( y[activity] >= time_2 - time[event_1] + ztrans[activity]*T - M_2 * (1 - con_1),  "y_a_bound trans %s" %str(activity))
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
                               con_1 += solution_frequencies[line_1][line_alternative]
                           if stop_endstelle == 'start':
                               if event_1_ankunft == 'dep':
                                   con_1 += solution_frequencies[line_1][line_alternative]
                           if stop_endstelle == 'end':
                               if event_1_ankunft == 'arr':
                                   con_1 += solution_frequencies[line_1][line_alternative]
       if line_2 in line_alternatives:
           for line_alternative in line_alternatives[line_2]:    
               for line_richtung_2 in line_alternatives[line_2][line_alternative][1]:
                   if line_2_original_richtung == (line_richtung_2[0], line_richtung_2[1], line_richtung_2[3], line_richtung_2[4]):
                       list_of_stops_2 = line_alternatives[line_2][line_alternative][1][line_richtung_2][0]    
                       if stop in list_of_stops_2:
                           stop_endstelle = line_alternatives[line_2][line_alternative][1][line_richtung_2][0][stop]
                           if stop_endstelle == '':
                               con_2 += solution_frequencies[line_2][line_alternative]
                           if stop_endstelle == 'start':
                               if event_1_ankunft == 'dep':
                                   con_2 += solution_frequencies[line_2][line_alternative]
                           if stop_endstelle == 'end':
                               if event_2_ankunft == 'arr':
                                   con_2 += solution_frequencies[line_2][line_alternative]

       
       if line_1 in line_alternatives and line_2 in line_alternatives:
           m_SP.addConstr( time[event_2] - time[event_1] + zhead[activity]*T >= h *(con_1 + con_2 -1), "lower_bound_ timetable headway %s" %str(activity))
           m_SP.addConstr( time[event_2] - time[event_1] + zhead[activity]*T <= T-h + M* (2 - con_1 -con_2),  "upper_bound_timetable headway %s" %str(activity))
           m_SP.addConstr( y[activity] >= time[event_2] - time[event_1] + zhead[activity]*T - M_2 * (2 - con_1 -con_2),  "y_a_bound headway %s" %str(activity))
           zaehler_12 += 1
           zaehler_13 += 1
           zaehler_18 += 1
       
       if line_1 not in line_alternatives:
           time_1 = int(events[event_1][1])
           m_SP.addConstr( time[event_2] - time_1 + zhead[activity]*T >=  h * con_2, "lower_bound_ timetable headway %s" %str(activity))
           m_SP.addConstr( time[event_2] - time_1 + zhead[activity]*T <= T-h + M*(1-con_2),  "upper_bound_timetable headway %s" %str(activity))
           m_SP.addConstr( y[activity] >= time[event_2] - time_1 + zhead[activity]*T - M_2 *(1-con_2),  "y_a_bound headway %s" %str(activity))
           zaehler_12 += 1
           zaehler_13 += 1 
           zaehler_18 += 1
       
       if line_2 not in line_alternatives:
           time_2 = int(events[event_2][1])
           m_SP.addConstr( time_2 - time[event_1] + zhead[activity]*T >=  h * con_1, "lower_bound_ timetable headway %s" %str(activity))
           m_SP.addConstr( time_2 - time[event_1] + zhead[activity]*T <= T-h + M *(1-con_1),  "upper_bound_timetable headway %s" %str(activity))
           m_SP.addConstr( y[activity] >=  time_2 - time[event_1] + zhead[activity]*T - M_2 *(1-con_1),  "y_a_bound headway %s" %str(activity))
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
           m_SP.addConstr( time[event_2] - time[event_1] + zwait[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
           zaehler_20 += 1
       elif activity_type == 'drive':
           m_SP.addConstr( time[event_2] - time[event_1] + zdrive[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
           zaehler_20 += 1
       elif activity_type == 'wende':
           m_SP.addConstr( time[event_2] - time[event_1] + zwende[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
           zaehler_20 += 1
       elif activity_type == 'trans':
           if line_1 in line_alternatives and line_2 in line_alternatives:
               m_SP.addConstr( time[event_2] - time[event_1] + ztrans[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
           elif line_1 not in line_alternatives:
               time_1 = int(events[event_1][1])
               m_SP.addConstr( time[event_2] - time_1 + ztrans[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
           elif line_2 not in line_alternatives:
               time_2 = int(events[event_2][1])
               m_SP.addConstr( time_2 - time[event_1] + ztrans[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
           zaehler_20 += 1  
       elif activity_type == 'headway':
           if line_1 in line_alternatives and line_2 in line_alternatives:
               m_SP.addConstr( time[event_2] - time[event_1] + zhead[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
           elif line_1 not in line_alternatives:
               time_1 = int(events[event_1][1])
               m_SP.addConstr( time[event_2] - time_1 + zhead[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
           elif line_2 not in line_alternatives:
               time_2 = int(events[event_2][1])
               m_SP.addConstr( time_2 - time[event_1] + zhead[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
           zaehler_20 += 1
            
    ##### Ausgabe Anzahl Variablen/Constraints ########
    print()
    print('OPTMIERUNG:')
    print('Constraints for integer Subproblem: ')
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
    print(' activity duration bounds: ' + str(zaehler_20))
    print()
   
    m_SP.write(r".\LP_TT_CB\LP-Dateien\LP_Datei_LP_TT_CB_"+str(iteration)+"_SP.lp")
    
    return(m_SP)


###################################################
########### Get Values of SubProblem ##############
###################################################


def get_values_of_SubProblem(m_SP, events, activities):
    solution_events = funktionen_sol.create_solution_events(m_SP, events)
    solution_y = funktionen_sol.create_solution_y(m_SP, activities)
    solution_z = funktionen_sol.create_solution_z(m_SP, activities)
        
    return(solution_events, solution_y, solution_z)