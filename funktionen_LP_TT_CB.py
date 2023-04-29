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

def set_up_and_solve_MP(iteration, opt_cuts, feas_cuts, T, alpha,M,M_2, h, k, events, activities, line_alternatives, edges, lines, stops, write):
    
    m_iMP = set_up_LP_TT_MP(iteration, opt_cuts, feas_cuts, T, alpha, M,M_2, h, k, events, activities, line_alternatives, edges, lines, write)
    
    ######### Optimization ##########################
       
    m_iMP.optimize()     

    ############## Print solution #################
    if m_iMP.Status == GRB.OPTIMAL:
        solution_frequencies = funktionen_sol.create_solution_frequencies(m_iMP, line_alternatives)
        print()
        print('Obj: %g' % m_iMP.objVal)       
        print()
        
        if write == True:
            funktionen_sol.write_solution_LP_TT(m_iMP, 'LP_TT_'+str(iteration)+'_MP')
            funktionen_sol.write_solution_frequencies_LP_TT(m_iMP, 'LP_TT_'+str(iteration)+'_MP', solution_frequencies)
        return(m_iMP, solution_frequencies)
    else: 
        print()
        print('Master problem is infeasible or unbounded.')
        print()

############# Set up MP ###########################

def set_up_LP_TT_MP(iteration, opt_cuts, feas_cuts, T, alpha,M,M_2, h, k, events, activities, line_alternatives, edges, lines, write):   
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
         solution_events = opt_cuts[i][0]
         solution_activities = opt_cuts[i][1]
        
         opt_cut = gp.LinExpr()
         opt_cut = 0
         
         list_of_not_fixed_events = funktionen.get_list_of_not_fixed_events(events)
         # my
         for event in list_of_not_fixed_events:
             opt_cut += (T-1)* solution_events[event]['my']
             
         #theta, lamda, chi, psi
         for activity in activities:
              event_1 = activity[0]
              event_2 = activity[1]
              event_1_ankunft = event_1[1]
              event_2_ankunft = event_2[1]
              La = activities[activity][0]
              Ua = activities[activity][1]
              stop_1 = event_1[0]
              stop_2 = event_2[0]
              edge = (stop_1, stop_2)
              line_1 = event_1[2]
              line_1_original_richtung = event_1[3]
              line_2 = event_2[2]
              line_2_original_richtung = event_2[3]
              activity_type = activities[activity][3]
         
              if activity_type == 'wait':
                 summe_frequenz_1 = 0
                 for line_alternative in line_alternatives[line_1]:
                     for line_richtung in line_alternatives[line_1][line_alternative][1]:
                         if line_1_original_richtung == (line_richtung[0], line_richtung[1], line_richtung[3], line_richtung[4]):
                             list_of_line_stops = line_alternatives[line_1][line_alternative][1][line_richtung][0]
                             for line_stop in list_of_line_stops:
                                 endstelle = line_alternatives[line_1][line_alternative][1][line_richtung][0][line_stop]
                                 if stop_1 == line_stop and endstelle == '':
                                     summe_frequenz_1 += f_line_alternative[line_1][line_alternative] 
                 opt_cut += solution_activities[activity]['theta'] * (-La * summe_frequenz_1)
                 opt_cut += solution_activities[activity]['lamda'] * (Ua+M*(1-summe_frequenz_1))
                 opt_cut += solution_activities[activity]['chi'] * M_2*(1-summe_frequenz_1)
             
              elif activity_type == 'drive':
                  summe_frequenz_1 = 0
                  for line_alternative in line_alternatives[line_1]:
                     for line_richtung in line_alternatives[line_1][line_alternative][1]:
                         if line_1_original_richtung == (line_richtung[0], line_richtung[1], line_richtung[3], line_richtung[4]):
                             list_of_line_edges = line_alternatives[line_1][line_alternative][1][line_richtung][1]
                             if edge in list_of_line_edges:
                                 summe_frequenz_1 += f_line_alternative[line_1][line_alternative]    
                  opt_cut += solution_activities[activity]['theta'] * (-La * summe_frequenz_1)
                  opt_cut += solution_activities[activity]['lamda'] * (Ua+M*(1-summe_frequenz_1))
                  opt_cut += solution_activities[activity]['chi'] * (M_2*(1-summe_frequenz_1))
             
              elif activity_type == 'wende':
                  summe_frequenz_1 = 0
                  for line_alternative in line_alternatives[line_1]:   
                     for line_richtung_1 in line_alternatives[line_1][line_alternative][1]:
                         if line_1_original_richtung == (line_richtung_1[0], line_richtung_1[1], line_richtung_1[3], line_richtung_1[4]):
                             for line_richtung_2 in line_alternatives[line_1][line_alternative][1]:
                                 if line_2_original_richtung == (line_richtung_2[0], line_richtung_2[1], line_richtung_2[3], line_richtung_2[4]):
                                     list_of_stops_1 = line_alternatives[line_1][line_alternative][1][line_richtung_1][0]
                                     list_of_stops_2 = line_alternatives[line_1][line_alternative][1][line_richtung_2][0]
                                     if stop_1 in list_of_stops_1 and stop_2 in list_of_stops_2:
                                          endstelle_1 =  line_alternatives[line_1][line_alternative][1][line_richtung_1][0][stop_1]
                                          endstelle_2 =  line_alternatives[line_1][line_alternative][1][line_richtung_2][0][stop_2]
                                          if endstelle_1 == 'end' and endstelle_2 == 'start':
                                              summe_frequenz_1 += f_line_alternative[line_1][line_alternative]   
                  opt_cut += solution_activities[activity]['theta'] * (-La * summe_frequenz_1)
                  opt_cut += solution_activities[activity]['lamda'] * (Ua+M*(1-summe_frequenz_1))
                  opt_cut += solution_activities[activity]['chi'] * (M_2*(1-summe_frequenz_1))
         
              elif activity_type == 'trans':
                 summe_frequenz_1 = 0
                 summe_frequenz_2 = 0
                 if line_1 in line_alternatives:
                     for line_alternative in line_alternatives[line_1]:    
                         for line_richtung_1 in line_alternatives[line_1][line_alternative][1]:
                             if line_1_original_richtung == (line_richtung_1[0], line_richtung_1[1], line_richtung_1[3], line_richtung_1[4]):
                                 list_of_stops_1 = line_alternatives[line_1][line_alternative][1][line_richtung_1][0]    
                                 if stop_1 in list_of_stops_1:
                                     summe_frequenz_1 += f_line_alternative[line_1][line_alternative]
                                    
                 if line_2 in line_alternatives:
                     for line_alternative in line_alternatives[line_2]:    
                         for line_richtung_2 in line_alternatives[line_2][line_alternative][1]:
                             if line_2_original_richtung == (line_richtung_2[0], line_richtung_2[1], line_richtung_2[3], line_richtung_2[4]):
                                 list_of_stops_2 = line_alternatives[line_2][line_alternative][1][line_richtung_2][0]    
                                 if stop_2 in list_of_stops_2:
                                     summe_frequenz_2 += f_line_alternative[line_2][line_alternative]
                                 
                 if line_1 in line_alternatives and line_2 in line_alternatives:
                     opt_cut += solution_activities[activity]['theta'] * (-La * (summe_frequenz_1 + summe_frequenz_2 -1))
                     opt_cut += solution_activities[activity]['lamda'] * (Ua+M*(2-summe_frequenz_1-summe_frequenz_2))
                     opt_cut += solution_activities[activity]['chi'] * (M_2*(2-summe_frequenz_1-summe_frequenz_2))
                 
                 elif line_1 not in line_alternatives:
                     opt_cut += solution_activities[activity]['theta'] *(-La * summe_frequenz_2)
                     opt_cut += solution_activities[activity]['lamda'] *(Ua+M*(1-summe_frequenz_2))
                     opt_cut += solution_activities[activity]['chi'] * (M_2*(1-summe_frequenz_2))
                 
                 elif line_2 not in line_alternatives:
                     opt_cut += solution_activities[activity]['theta'] * (-La * summe_frequenz_1)
                     opt_cut += solution_activities[activity]['lamda'] * (Ua+M*(1-summe_frequenz_1))
                     opt_cut += solution_activities[activity]['chi'] * (M_2*(1-summe_frequenz_1))
         
              elif activity_type == 'headway':
                 summe_frequenz_1 = 0
                 summe_frequenz_2 = 0
                 if line_1 in line_alternatives:
                     for line_alternative in line_alternatives[line_1]:    
                         for line_richtung_1 in line_alternatives[line_1][line_alternative][1]:
                             if line_1_original_richtung == (line_richtung_1[0], line_richtung_1[1], line_richtung_1[3], line_richtung_1[4]):
                                 list_of_stops_1 = line_alternatives[line_1][line_alternative][1][line_richtung_1][0]    
                                 if stop_1 in list_of_stops_1:
                                     stop_endstelle = line_alternatives[line_1][line_alternative][1][line_richtung_1][0][stop_1]
                                     if stop_endstelle == '':
                                         summe_frequenz_1 += f_line_alternative[line_1][line_alternative]
                                     if stop_endstelle == 'start':
                                         if event_1_ankunft == 'dep':
                                            summe_frequenz_1 += f_line_alternative[line_1][line_alternative]
                                     if stop_endstelle == 'end':
                                         if event_1_ankunft == 'arr':
                                             summe_frequenz_1 += f_line_alternative[line_1][line_alternative]
                 if line_2 in line_alternatives:
                     for line_alternative in line_alternatives[line_2]:    
                         for line_richtung_2 in line_alternatives[line_2][line_alternative][1]:
                             if line_2_original_richtung == (line_richtung_2[0], line_richtung_2[1], line_richtung_2[3], line_richtung_2[4]):
                                 list_of_stops_2 = line_alternatives[line_2][line_alternative][1][line_richtung_2][0]    
                                 if stop_2 in list_of_stops_2:
                                     stop_endstelle = line_alternatives[line_2][line_alternative][1][line_richtung_2][0][stop_2]
                                     if stop_endstelle == '':
                                         summe_frequenz_2 += f_line_alternative[line_2][line_alternative]
                                     if stop_endstelle == 'start':
                                         if event_1_ankunft == 'dep':
                                             summe_frequenz_2 += f_line_alternative[line_2][line_alternative]
                                     if stop_endstelle == 'end':
                                         if event_2_ankunft == 'arr':
                                             summe_frequenz_2 += f_line_alternative[line_2][line_alternative]
             
                 if line_1 in line_alternatives and line_2 in line_alternatives:
                     opt_cut += solution_activities[activity]['theta'] * (-La * (summe_frequenz_1 + summe_frequenz_2 -1))
                     opt_cut += solution_activities[activity]['lamda'] * (Ua+M*(2-summe_frequenz_1-summe_frequenz_2))
                     opt_cut += solution_activities[activity]['chi'] * (M_2*(2-summe_frequenz_1-summe_frequenz_2))
                 
                 elif line_1 not in line_alternatives:
                     opt_cut += solution_activities[activity]['theta'] * (-La * summe_frequenz_2)
                     opt_cut += solution_activities[activity]['lamda'] * (Ua+M*(1-summe_frequenz_2))
                     opt_cut += solution_activities[activity]['chi'] * (M_2*(1-summe_frequenz_2))
                 
                 elif line_2 not in line_alternatives:
                     opt_cut += solution_activities[activity]['theta'] * (-La * summe_frequenz_1)
                     opt_cut += solution_activities[activity]['lamda'] * (Ua+M*(1-summe_frequenz_1))
                     opt_cut += solution_activities[activity]['chi'] * (M_2*(1-summe_frequenz_1)) 
                     
         m.addConstr(opt_cut <= eta, "optimality_cut %s" %str(iteration))
         zaehler_4 += 1


    # feasibility cuts
    
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
    
    
    ######### Output number constraints ##########
    print()
    print('OPTIMIZATION:')
    print('Constraints for MP: ')
    print(' min-frequency ' + str(zaehler_1))
    print(' max frequency ' + str(zaehler_2))
    print(' frequency lines under construction ' + str(zaehler_3))
    print(' optimality cuts: ' + str(zaehler_4))
    print(' feasibility cuts: ' + str(zaehler_5))
    print()
   
    if write == True:
        m.write(r'.\LP_TT\LP-Dateien\LP_Datei_LP_TT_'+str(iteration)+'_MP.lp')
    
    return(m)









###################################################
############# Subproblem ##########################
###################################################

def set_up_and_solve_Subproblem(iteration, opt_cuts, feas_cuts, solution_frequencies, beta, edges, events, activities, line_alternatives, T, M , M_2, k, h, write):
    
    ######### Set up Integer Subproblem ###########
    m_SP_int = set_up_and_solve_integer_Subproblem(iteration, opt_cuts, feas_cuts, solution_frequencies, beta, h, edges, events, activities, line_alternatives, T, M ,M_2,  k)
    
    if m_SP_int.Status == GRB.OPTIMAL:
        
        ######### Set up Subproblem ###################
        m_SP = set_up_LP_TT_Subproblem(iteration, solution_frequencies, beta, edges, events, activities, line_alternatives, T, M ,M_2,  k, write)
        
        
        ######### Optimization ############################ 
    
        m_SP.optimize()        
                
        ############## Print solution #####################
        
        if m_SP.Status == GRB.OPTIMAL:
            print()
            print('Obj: %g' % m_SP.objVal)       
            print()
            
            if write == True:
                funktionen_sol.write_solution_LP_TT(m_SP, 'LP_TT_CB_'+str(iteration)+'_SP')
            
            solution_events = get_solution_events_SP(m_SP, events)
            solution_activities = get_solution_activities_SP(m_SP, activities)
            opt_cuts[iteration]=[solution_events, solution_activities]

        iteration += 1
        return(m_SP, iteration)
    
    else:
        iteration += 1
        return(m_SP_int, iteration)


###################################################
######## set Up SubProblem ########################
###################################################

def set_up_LP_TT_Subproblem(iteration, solution_frequencies, beta, edges, events, activities, line_alternatives, T, M ,M_2, k, write):

    m_SP = gp.Model(str(iteration)+'_SP')
    
    list_of_not_fixed_events = funktionen.get_list_of_not_fixed_events(events)
    
    ############ Create variables #####################

    theta = m_SP.addVars(activities, lb= -float('inf'), ub=0, name ='theta')
    lamda = m_SP.addVars(activities,lb= -float('inf'), ub=0, name ='lamda')
    chi = m_SP.addVars(activities, lb= -float('inf'), ub=0, name ='chi')
    psi = m_SP.addVars(activities, lb= -float('inf'), ub=0, name ='psi')
    my = m_SP.addVars(list_of_not_fixed_events,lb= -float('inf'), ub=0, name ='my')
    
    ############ Create objective #####################
    obj_SP=gp.LinExpr()
    
    # my
    for event in list_of_not_fixed_events:
        obj_SP += (T-1)* my[event]
        
    
    #theta, lamda, chi, psi
    for activity in activities:
         event_1 = activity[0]
         event_2 = activity[1]
         event_1_ankunft = event_1[1]
         event_2_ankunft = event_2[1]
         La = activities[activity][0]
         Ua = activities[activity][1]
         stop_1 = event_1[0]
         stop_2 = event_2[0]
         edge = (stop_1, stop_2)
         line_1 = event_1[2]
         line_1_original_richtung = event_1[3]
         line_2 = event_2[2]
         line_2_original_richtung = event_2[3]
         activity_type = activities[activity][3]
    
         if activity_type == 'wait':
            summe_frequenz_1 = 0
            for line_alternative in line_alternatives[line_1]:
                for line_richtung in line_alternatives[line_1][line_alternative][1]:
                    if line_1_original_richtung == (line_richtung[0], line_richtung[1], line_richtung[3], line_richtung[4]):
                        list_of_line_stops = line_alternatives[line_1][line_alternative][1][line_richtung][0]
                        for line_stop in list_of_line_stops:
                            endstelle = line_alternatives[line_1][line_alternative][1][line_richtung][0][line_stop]
                            if stop_1 == line_stop and endstelle == '':
                                summe_frequenz_1 += solution_frequencies[line_1][line_alternative] 
            obj_SP += theta[activity] * float(-La * summe_frequenz_1)
            obj_SP += lamda[activity] * float(Ua+M*(1-summe_frequenz_1))
            obj_SP += chi[activity] * float(M_2*(1-summe_frequenz_1))
        
         elif activity_type == 'drive':
             summe_frequenz_1 = 0
             for line_alternative in line_alternatives[line_1]:
                for line_richtung in line_alternatives[line_1][line_alternative][1]:
                    if line_1_original_richtung == (line_richtung[0], line_richtung[1], line_richtung[3], line_richtung[4]):
                        list_of_line_edges = line_alternatives[line_1][line_alternative][1][line_richtung][1]
                        if edge in list_of_line_edges:
                            summe_frequenz_1 += solution_frequencies[line_1][line_alternative]    
             obj_SP += theta[activity] * float(-La * summe_frequenz_1)
             obj_SP += lamda[activity] * float(Ua+M*(1-summe_frequenz_1))
             obj_SP += chi[activity] * float(M_2*(1-summe_frequenz_1))
        
         elif activity_type == 'wende':
             summe_frequenz_1 = 0
             for line_alternative in line_alternatives[line_1]:   
                for line_richtung_1 in line_alternatives[line_1][line_alternative][1]:
                    if line_1_original_richtung == (line_richtung_1[0], line_richtung_1[1], line_richtung_1[3], line_richtung_1[4]):
                        for line_richtung_2 in line_alternatives[line_1][line_alternative][1]:
                            if line_2_original_richtung == (line_richtung_2[0], line_richtung_2[1], line_richtung_2[3], line_richtung_2[4]):
                                list_of_stops_1 = line_alternatives[line_1][line_alternative][1][line_richtung_1][0]
                                list_of_stops_2 = line_alternatives[line_1][line_alternative][1][line_richtung_2][0]
                                if stop_1 in list_of_stops_1 and stop_2 in list_of_stops_2:
                                     endstelle_1 =  line_alternatives[line_1][line_alternative][1][line_richtung_1][0][stop_1]
                                     endstelle_2 =  line_alternatives[line_1][line_alternative][1][line_richtung_2][0][stop_2]
                                     if endstelle_1 == 'end' and endstelle_2 == 'start':
                                         summe_frequenz_1 += solution_frequencies[line_1][line_alternative]   
             obj_SP += theta[activity] * float(-La * summe_frequenz_1)
             obj_SP += lamda[activity] * float(Ua+M*(1-summe_frequenz_1))
             obj_SP += chi[activity] * float(M_2*(1-summe_frequenz_1))
    
         elif activity_type == 'trans':
            summe_frequenz_1 = 0
            summe_frequenz_2 = 0
            if line_1 in line_alternatives:
                for line_alternative in line_alternatives[line_1]:    
                    for line_richtung_1 in line_alternatives[line_1][line_alternative][1]:
                        if line_1_original_richtung == (line_richtung_1[0], line_richtung_1[1], line_richtung_1[3], line_richtung_1[4]):
                            list_of_stops_1 = line_alternatives[line_1][line_alternative][1][line_richtung_1][0]    
                            if stop_1 in list_of_stops_1:
                                summe_frequenz_1 += solution_frequencies[line_1][line_alternative]
                               
            if line_2 in line_alternatives:
                for line_alternative in line_alternatives[line_2]:    
                    for line_richtung_2 in line_alternatives[line_2][line_alternative][1]:
                        if line_2_original_richtung == (line_richtung_2[0], line_richtung_2[1], line_richtung_2[3], line_richtung_2[4]):
                            list_of_stops_2 = line_alternatives[line_2][line_alternative][1][line_richtung_2][0]    
                            if stop_2 in list_of_stops_2:
                                summe_frequenz_2 += solution_frequencies[line_2][line_alternative]
                            
            if line_1 in line_alternatives and line_2 in line_alternatives:
                obj_SP += theta[activity] * float(-La * (summe_frequenz_1 + summe_frequenz_2 -1))
                obj_SP += lamda[activity] * float(Ua+M*(2-summe_frequenz_1-summe_frequenz_2))
                obj_SP += chi[activity] * float(M_2*(2-summe_frequenz_1-summe_frequenz_2))
            
            elif line_1 not in line_alternatives:
                obj_SP += theta[activity] * float(-La * summe_frequenz_2)
                obj_SP += lamda[activity] * float(Ua+M*(1-summe_frequenz_2))
                obj_SP += chi[activity] * float(M_2*(1-summe_frequenz_2))
            
            elif line_2 not in line_alternatives:
                obj_SP += theta[activity] * float(-La * summe_frequenz_1)
                obj_SP += lamda[activity] * float(Ua+M*(1-summe_frequenz_1))
                obj_SP += chi[activity] * float(M_2*(1-summe_frequenz_1))
    
         elif activity_type == 'headway':
            summe_frequenz_1 = 0
            summe_frequenz_2 = 0
            if line_1 in line_alternatives:
                for line_alternative in line_alternatives[line_1]:    
                    for line_richtung_1 in line_alternatives[line_1][line_alternative][1]:
                        if line_1_original_richtung == (line_richtung_1[0], line_richtung_1[1], line_richtung_1[3], line_richtung_1[4]):
                            list_of_stops_1 = line_alternatives[line_1][line_alternative][1][line_richtung_1][0]    
                            if stop_1 in list_of_stops_1:
                                stop_endstelle = line_alternatives[line_1][line_alternative][1][line_richtung_1][0][stop_1]
                                if stop_endstelle == '':
                                    summe_frequenz_1 += solution_frequencies[line_1][line_alternative]
                                if stop_endstelle == 'start':
                                    if event_1_ankunft == 'dep':
                                       summe_frequenz_1 += solution_frequencies[line_1][line_alternative]
                                if stop_endstelle == 'end':
                                    if event_1_ankunft == 'arr':
                                        summe_frequenz_1 += solution_frequencies[line_1][line_alternative]
            if line_2 in line_alternatives:
                for line_alternative in line_alternatives[line_2]:    
                    for line_richtung_2 in line_alternatives[line_2][line_alternative][1]:
                        if line_2_original_richtung == (line_richtung_2[0], line_richtung_2[1], line_richtung_2[3], line_richtung_2[4]):
                            list_of_stops_2 = line_alternatives[line_2][line_alternative][1][line_richtung_2][0]    
                            if stop_2 in list_of_stops_2:
                                stop_endstelle = line_alternatives[line_2][line_alternative][1][line_richtung_2][0][stop_2]
                                if stop_endstelle == '':
                                    summe_frequenz_2 += solution_frequencies[line_2][line_alternative]
                                if stop_endstelle == 'start':
                                    if event_1_ankunft == 'dep':
                                        summe_frequenz_2 += solution_frequencies[line_2][line_alternative]
                                if stop_endstelle == 'end':
                                    if event_2_ankunft == 'arr':
                                        summe_frequenz_2 += solution_frequencies[line_2][line_alternative]
        
            if line_1 in line_alternatives and line_2 in line_alternatives:
                obj_SP += theta[activity] * float(-La * (summe_frequenz_1 + summe_frequenz_2 -1))
                obj_SP += lamda[activity] * float(Ua+M*(2-summe_frequenz_1-summe_frequenz_2))
                obj_SP += chi[activity] * float(M_2*(2-summe_frequenz_1-summe_frequenz_2))
            
            elif line_1 not in line_alternatives:
                obj_SP += theta[activity] * float(-La * summe_frequenz_2)
                obj_SP += lamda[activity] * float(Ua+M*(1-summe_frequenz_2))
                obj_SP += chi[activity] * float(M_2*(1-summe_frequenz_2))
            
            elif line_2 not in line_alternatives:
                obj_SP += theta[activity] * float(-La * summe_frequenz_1)
                obj_SP += lamda[activity] * float(Ua+M*(1-summe_frequenz_1))
                obj_SP += chi[activity] * float(M_2*(1-summe_frequenz_1))
          
    
    m_SP.setObjective(obj_SP, GRB.MAXIMIZE)        
            
            
    ######### Create constraints ######################
    zaehler_1 = 0
    zaehler_2 = 0
    zaehler_3 = 0

    
    for activity in activities:
        activity_weight = activities[activity][2]
        m_SP.addConstr(T*(- theta[activity]+ lamda[activity] + chi[activity] - psi[activity]) == 0, "act-constraint_2_D %s" %str(activity))
        # constraint for z_a
        zaehler_1 += 1
        
    for event in list_of_not_fixed_events:
        con = gp.LinExpr()
        con += my[event]

        for activity in activities:
            event_1 = activity[0]
            event_2 = activity[1]
            if event_1 == event:
                con += theta[activity] - lamda[activity] - chi[activity] + psi[activity]
            if event_2 == event:
                con += - theta[activity] + lamda[activity] + chi[activity]- psi[activity]            
        m_SP.addConstr(con <= 0, "event-constraint_3_D %s" %str(event))
        #consraint for pi_i
        zaehler_2 += 1
    
    for activity in activities:
        activity_weight = activities[activity][2]
        m_SP.addConstr(-chi[activity]  <= beta*activity_weight, "act-constraint_4_D %s" %str(activity))
        # constraint for y_a
        zaehler_3 += 1
            
    ##### Output number constraints #############
    print()
    print('OPTIMIZATION:')
    print('Constraints for Subproblem: ')
    print(' activities_2_D: ' + str(zaehler_1))
    print(' events_3_D: ' + str(zaehler_2))
    print(' activities_4_D: ' + str(zaehler_3))

    print()
   
    if write == True:
        m_SP.write(r".\LP_TT_CB\LP-Dateien\LP_Datei_LP_TT_CB_"+str(iteration)+"_SP.lp")
    
    return(m_SP)


###################################################
######## Get solution SubProblem ##################
###################################################


def get_solution_events_SP(m_SP, events):
    solution_events = {}
    for event in events:
        if events[event][0] == 'n':
            solution_events[event]={}
            event_var_list = funktionen_sol.get_event_var_list(event)
            var = m_SP.getVarByName('my['+str(event_var_list)+']')
            solution_events[event]['my']=var.x
    return(solution_events)


def get_solution_activities_SP(m_SP, activities):
    solution_activities = {}
    for activity in activities:
        solution_activities[activity] = {}
        event_1 = activity[0]
        event_2 = activity[1]
        var = m_SP.getVarByName('theta['+str(event_1)+','+ str(event_2)+']')
        solution_activities[activity]['theta']=var.x
        var = m_SP.getVarByName('lamda['+str(event_1)+','+ str(event_2)+']')
        solution_activities[activity]['lamda']=var.x
        var = m_SP.getVarByName('chi['+str(event_1)+','+ str(event_2)+']')
        solution_activities[activity]['chi']=var.x
        var = m_SP.getVarByName('psi['+str(event_1)+','+ str(event_2)+']')
        solution_activities[activity]['psi']=var.x    
    return(solution_activities)


def get_solution_ray(m_SP, solution_ray, events, activities):
    for event in events:
        if events[event][0] == 'n':
            solution_ray[event]={}
            event_var_list = funktionen_sol.get_event_var_list(event)
            var = m_SP.getVarByName('my['+str(event_var_list)+']')
            solution_ray[event]['my']=var.UnbdRay
    
    for activity in activities:
        solution_ray[activity] = {}
        event_1 = activity[0]
        event_2 = activity[1]
        var = m_SP.getVarByName('theta['+str(event_1)+','+ str(event_2)+']')
        solution_ray[activity]['theta']=var.UnbdRay
        var = m_SP.getVarByName('lamda['+str(event_1)+','+ str(event_2)+']')
        solution_ray[activity]['lamda']=var.UnbdRay
        var = m_SP.getVarByName('chi['+str(event_1)+','+ str(event_2)+']')
        solution_ray[activity]['chi']=var.UnbdRay
        var = m_SP.getVarByName('psi['+str(event_1)+','+ str(event_2)+']')
        solution_ray[activity]['psi']=var.UnbdRay 
        


###################################################
####### Get Primal Values of SubProblem ###########
###################################################

def get_primal_values_of_SubProblem(m_SP, events, activities):
    solution_events = funktionen_sol.create_default_solution_events(events)
    solution_y = funktionen_sol.create_default_solution_y(activities)
    solution_z = funktionen_sol.create_default_solution_y(activities)
    
    constraints = m_SP.getConstrs()
    
    for i in range(0,len(constraints)):
        constraint = constraints[i]
        pi_value = constraint.getAttr('Pi')
        
        constraint_name = constraint.getAttr('ConstrName')
        con_split_1 = constraint_name.split('-')
        
        if con_split_1[0] == 'act':
            con_split_3 = con_split_1[1].split("_")
            con_number = con_split_3[1]

            con_split_2 = con_split_1[1].split("'")
            stop_1 = con_split_2[1]
            ankunft_1 = con_split_2[3]
            line_1_nr = con_split_2[5]
            line_1_zuggruppe = con_split_2[7]
            line_1_start = con_split_2[13]
            line_1_stop = con_split_2[15]
            stop_2 = con_split_2[17]
            ankunft_2 = con_split_2[19]
            line_2_nr = con_split_2[21]
            line_2_zuggruppe = con_split_2[23]
            line_2_start = con_split_2[29]
            line_2_stop = con_split_2[31]
            
            event_1 = (stop_1, ankunft_1, (line_1_nr, line_1_zuggruppe), (line_1_nr, line_1_zuggruppe, line_1_start, line_1_stop))
            event_2 = (stop_2, ankunft_2, (line_2_nr, line_2_zuggruppe), (line_2_nr, line_2_zuggruppe, line_2_start, line_2_stop))
            activity = (event_1, event_2)

            if con_number == '4':
                solution_y[activity]= pi_value
            elif con_number == '2':
                solution_z[activity] = pi_value
        
        elif con_split_1[0] == 'event':
            con_split_2 = con_split_1[1].split("'")
            stop_1 = con_split_2[1]
            ankunft_1 = con_split_2[3]
            line_1_nr = con_split_2[5]
            line_1_zuggruppe = con_split_2[7]
            line_1_start = con_split_2[13]
            line_1_stop = con_split_2[15]
            event = (stop_1, ankunft_1, (line_1_nr, line_1_zuggruppe), (line_1_nr, line_1_zuggruppe, line_1_start, line_1_stop))
            
            solution_events[event] = pi_value
                       
    return (solution_events, solution_y, solution_z)













###################################################
########integer Subproblem ########################
###################################################

def set_up_and_solve_integer_Subproblem(iteration, opt_cuts, feas_cuts, solution_frequencies, beta, h, edges, events, activities, line_alternatives, T, M ,M_2,  k):
    
    ######### Set up Subproblem ###################
    m_SP = set_up_LP_TT_integer_Subproblem(iteration, solution_frequencies, beta, h, edges, events, activities, line_alternatives, T, M ,M_2,  k)

    ######### Optimieren ############################## 
    gap = 0.9
    
          
    m_SP.setParam(GRB.Param.MIPGap, gap)
    m_SP.setParam(GRB.Param.DualReductions, 0)
    m_SP.optimize()        
    print()
            
    ############## Print solution #####################
    
    if m_SP.Status == GRB.INFEASIBLE:
            print()
            print('INFEASIBLE')     
            print()
            feas_cuts[iteration]=solution_frequencies
           
    return(m_SP)


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