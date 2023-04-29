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

def set_up_and_solve_MP(iteration, opt_cuts, feas_cuts, T, beta,M, M_2, h, k, events, activities, line_alternatives, edges, lines, write):
    
    m_MP = set_up_TT_LP_MP(iteration, opt_cuts, feas_cuts, T, beta,M,M_2, h, k, events, activities, line_alternatives, edges, lines, write)    
    
    ######### Optimization ############################## 
       
    m_MP.optimize()     

    ############## Print solution #####################

    if m_MP.Status == GRB.OPTIMAL:
        solution_events = funktionen_sol.create_solution_events(m_MP, events)    
        solution_z = funktionen_sol.create_solution_z(m_MP, activities)
        solution_y = funktionen_sol.create_solution_y(m_MP, activities)
        
        print()
        print('Obj: %g' % m_MP.objVal)       
        print()
        
        if write == True:
            funktionen_sol.write_solution_TT_LP(m_MP, 'TT_LP_'+str(iteration)+'_MP')

    return(m_MP, solution_events, solution_z, solution_y)


############# Set up MP ###########################

def set_up_TT_LP_MP(iteration, opt_cuts, feas_cuts, T, beta,M,M_2, h, k, events, activities, line_alternatives, edges, lines, write):   
    m = gp.Model(str(iteration) +'_MP')
    
    list_of_not_fixed_events = funktionen.get_list_of_not_fixed_events(events)
    list_of_all_activities = funktionen.get_list_of_all_activities(activities)
    list_of_wait_activities = funktionen.get_list_of_wait_activities(activities)
    list_of_drive_activities = funktionen.get_list_of_drive_activities(activities)
    list_of_wende_activities = funktionen.get_list_of_wende_activities(activities)
    list_of_trans_activities = funktionen.get_list_of_trans_activities(activities)
    list_of_headway_activities = funktionen.get_list_of_headway_activities(activities)
    list_of_wait_drive_wende_activities = funktionen.get_list_of_wait_drive_wende_activities(activities)
    
    ############ Create variables #####################
    time = m.addVars(list_of_not_fixed_events, lb = 0, ub = T-1, vtype=GRB.INTEGER, name="time")
    zwait=m.addVars(list_of_wait_activities,lb=-2, ub = 2, vtype=GRB.INTEGER, name="zwait")
    zdrive=m.addVars(list_of_drive_activities, lb=-2, ub = 2, vtype=GRB.INTEGER, name="zdrive")
    zwende=m.addVars(list_of_wende_activities, lb=-2, ub = 2, vtype=GRB.INTEGER, name="zwende")
    ztrans=m.addVars(list_of_trans_activities, lb=-2, ub = 2, vtype=GRB.INTEGER, name="ztrans")                 
    zhead=m.addVars(list_of_headway_activities, lb=-2, ub = 2, vtype=GRB.INTEGER, name="zhead")
    y = m.addVars(list_of_all_activities,  lb=0, name="y_a")
    eta = m.addVar( lb=-float('inf'), name="eta")
    
    
    ############ Create objective #####################
    obj=gp.LinExpr()
    obj_TT=gp.LinExpr()
    
    #timetable costs        
    for activity in activities:
        activity_weight = activities[activity][2]  
        obj_TT += activity_weight * y[activity]         
            
    if len(opt_cuts) == 0:
        obj = beta * obj_TT
    else:
        obj = beta * obj_TT + eta
        
    m.setObjective(obj, GRB.MINIMIZE)        
            
            
    ######### Create constraints ######################
    zaehler_2 = 0
    zaehler_3 = 0
    zaehler_4 = 0

        
    # activity duration lower bound
    for activity in activities:
        event_1 = activity[0]
        event_2 = activity[1]
        line_1 = event_1[2]
        line_2 = event_2[2]
        activity_type = activities[activity][3]
        if activity_type == 'wait':
            m.addConstr( time[event_2] - time[event_1] + zwait[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            zaehler_2 += 1
        elif activity_type == 'drive':
            m.addConstr( time[event_2] - time[event_1] + zdrive[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            zaehler_2 += 1
        elif activity_type == 'wende':
            m.addConstr( time[event_2] - time[event_1] + zwende[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            zaehler_2 += 1
        elif activity_type == 'trans':
            if line_1 in line_alternatives and line_2 in line_alternatives:
                m.addConstr( time[event_2] - time[event_1] + ztrans[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            elif line_1 not in line_alternatives:
                time_1 = int(events[event_1][1])
                m.addConstr( time[event_2] - time_1 + ztrans[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            elif line_2 not in line_alternatives:
                time_2 = int(events[event_2][1])
                m.addConstr( time_2 - time[event_1] + ztrans[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            zaehler_2 += 1  
        elif activity_type == 'headway':
            if line_1 in line_alternatives and line_2 in line_alternatives:
                m.addConstr( time[event_2] - time[event_1] + zhead[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            elif line_1 not in line_alternatives:
                time_1 = int(events[event_1][1])
                m.addConstr( time[event_2] - time_1 + zhead[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            elif line_2 not in line_alternatives:
                time_2 = int(events[event_2][1])
                m.addConstr( time_2 - time[event_1] + zhead[activity]*T >= 0, "lower_bound_activity_duration %s" %str(activity))
            zaehler_2 += 1
    
    
    # optimality cuts
    for i in opt_cuts:
        solution_edges = opt_cuts[i][0]
        solution_lines_under_construction = opt_cuts[i][1]
        solution_activities = opt_cuts[i][2]
        
        opt_cut = gp.LinExpr()
        opt_cut = 0
        
        list_of_wait_drive_wende_activities = funktionen.get_list_of_wait_drive_wende_activities(activities)
        
        for edge in solution_edges:
            fe_min = edges[edge][3]
            fe_max = edges[edge][4]
            zaehler_fixed_lines_of_edge = 0
            for line in lines:
                if line not in line_alternatives:
                    for line_richtung in lines[line]:
                        line_edge_list = lines[line][line_richtung][2]
                        if edge in line_edge_list:
                            zaehler_fixed_lines_of_edge += 1
            opt_cut += (-fe_min + zaehler_fixed_lines_of_edge) * solution_edges[edge]['chi'] + (fe_max - zaehler_fixed_lines_of_edge)* solution_edges[edge]['psi']
        for line in solution_lines_under_construction:
            opt_cut += solution_lines_under_construction[line]['my']
            
        for activity in list_of_wait_drive_wende_activities:
            event_1 = activity[0]
            event_2 = activity[1]
            U_a = activities[activity][1]
            activity_type = activities[activity][3]
            if activity_type == 'drive':
                opt_cut += solution_activities[activity]['theta'] * ( time[event_2] - time[event_1] + zdrive[activity] * T)
                opt_cut += solution_activities[activity]['lamda'] * (- time[event_2] + time[event_1] - zdrive[activity] * T + U_a + M)
                opt_cut += solution_activities[activity]['kappa'] * (- time[event_2] + time[event_1] - zdrive[activity] * T + y[activity] + M_2)
            if activity_type == 'wait':
                 opt_cut += solution_activities[activity]['theta'] * ( time[event_2] - time[event_1] + zwait[activity] * T)
                 opt_cut += solution_activities[activity]['lamda'] * (- time[event_2] + time[event_1] - zwait[activity] * T + U_a + M)
                 opt_cut += solution_activities[activity]['kappa'] * (- time[event_2] + time[event_1] - zwait[activity] * T + y[activity] + M_2)
            if activity_type == 'wende':
                 opt_cut += solution_activities[activity]['theta'] * ( time[event_2] - time[event_1] + zwende[activity] * T)
                 opt_cut += solution_activities[activity]['lamda'] * (- time[event_2] + time[event_1] - zwende[activity] * T + U_a + M)
                 opt_cut += solution_activities[activity]['kappa'] * (- time[event_2] + time[event_1] - zwende[activity] * T + y[activity] + M_2)
                 
        for activity in activities:
            activity_type = activities[activity][3]
            
            if activity_type == 'trans':
                event_1 = activity[0]
                line_1 = event_1[2]
                event_2 = activity[1]
                line_2 = event_2[2]
                L_a = activities[activity][0]
                U_a = activities[activity][1]
                if line_1 in line_alternatives and line_2 in line_alternatives:
                    opt_cut += solution_activities[activity]['theta'] * ( time[event_2] - time[event_1] + ztrans[activity] * T + L_a)
                    opt_cut += solution_activities[activity]['lamda'] * (- time[event_2] + time[event_1] - ztrans[activity] * T + U_a + 2*M)
                    opt_cut += solution_activities[activity]['kappa'] * (- time[event_2] + time[event_1] - ztrans[activity] * T + y[activity] + 2*M_2)
                elif line_1 in line_alternatives and line_2 not in line_alternatives:
                    time_event_2 = events[event_2][1]
                    opt_cut += solution_activities[activity]['theta'] * ( time_event_2 - time[event_1] + ztrans[activity] * T)
                    opt_cut += solution_activities[activity]['lamda'] * (- time_event_2 + time[event_1] - ztrans[activity] * T + U_a + M)
                    opt_cut += solution_activities[activity]['kappa'] * (- time_event_2 + time[event_1] - ztrans[activity] * T + y[activity] + M_2)
                elif line_1 not in line_alternatives and line_2 in line_alternatives:
                    time_event_1 = events[event_1][1]
                    opt_cut += solution_activities[activity]['theta'] * ( time[event_2] - time_event_1 + ztrans[activity] * T)
                    opt_cut += solution_activities[activity]['lamda'] * (- time[event_2] + time_event_1 - ztrans[activity] * T + U_a + M)
                    opt_cut += solution_activities[activity]['kappa'] * (- time[event_2] + time_event_1 - ztrans[activity] * T + y[activity] + M_2)
            
            if activity_type == 'headway':
                event_1 = activity[0]
                line_1 = event_1[2]
                event_2 = activity[1]
                line_2 = event_2[2]
                L_a = activities[activity][0]
                U_a = activities[activity][1]
                if line_1 in line_alternatives and line_2 in line_alternatives:
                    opt_cut += solution_activities[activity]['theta'] * ( time[event_2] - time[event_1] + zhead[activity] * T + L_a)
                    opt_cut += solution_activities[activity]['lamda'] * (- time[event_2] + time[event_1] - zhead[activity] * T + U_a + 2*M)
                    opt_cut += solution_activities[activity]['kappa'] * (- time[event_2] + time[event_1] - zhead[activity] * T + y[activity] + 2*M_2)
                elif line_1 in line_alternatives and line_2 not in line_alternatives:
                    time_event_2 = events[event_2][1]
                    opt_cut += solution_activities[activity]['theta'] * ( time_event_2 - time[event_1] + zhead[activity] * T)
                    opt_cut += solution_activities[activity]['lamda'] * (- time_event_2 + time[event_1] - zhead[activity] * T + U_a + M)
                    opt_cut += solution_activities[activity]['kappa'] * (- time_event_2 + time[event_1] - zhead[activity] * T + y[activity] + M_2)
                elif line_1 not in line_alternatives and line_2 in line_alternatives:
                    time_event_1 = events[event_1][1]
                    opt_cut += solution_activities[activity]['theta'] * ( time[event_2] - time_event_1 + zhead[activity] * T)
                    opt_cut += solution_activities[activity]['lamda'] * (- time[event_2] + time_event_1 - zhead[activity] * T + U_a + M)
                    opt_cut += solution_activities[activity]['kappa'] * (- time[event_2] + time_event_1 - zhead[activity] * T + y[activity] + M_2)
            
    
        m.addConstr(opt_cut <= eta, "optimality_cut %s" %str(iteration))
        zaehler_3 += 1
        
        
    # feasibility cuts
    for i in feas_cuts:
        solution_ray=feas_cuts[i]
        
        feas_cut = gp.LinExpr()
        feas_cut = 0
        
        list_of_wait_drive_wende_activities = funktionen.get_list_of_wait_drive_wende_activities(activities)
        
        for edge in edges:
            if edge in solution_ray:
                fe_min = edges[edge][3]
                fe_max = edges[edge][4]
                zaehler_fixed_lines_of_edge = 0
                for line in lines:
                    if line not in line_alternatives:
                        for line_richtung in lines[line]:
                            line_edge_list = lines[line][line_richtung][2]
                            if edge in line_edge_list:
                                zaehler_fixed_lines_of_edge += 1
                feas_cut += (-fe_min + zaehler_fixed_lines_of_edge) * solution_ray[edge]['chi'] + (fe_max - zaehler_fixed_lines_of_edge)* solution_ray[edge]['psi']
        for line in lines:
            if line in solution_ray:
                feas_cut += solution_ray[line]['my']
            
        for activity in list_of_wait_drive_wende_activities:
            event_1 = activity[0]
            event_2 = activity[1]
            U_a = activities[activity][1]
            activity_type = activities[activity][3]
            if activity_type == 'drive':
                feas_cut += solution_ray[activity]['theta'] * ( time[event_2] - time[event_1] + zdrive[activity] * T)
                feas_cut += solution_ray[activity]['lamda'] * (- time[event_2] + time[event_1] - zdrive[activity] * T + U_a + M)
                feas_cut += solution_ray[activity]['kappa'] * (- time[event_2] + time[event_1] - zdrive[activity] * T + y[activity] + M_2)
            if activity_type == 'wait':
                 feas_cut += solution_ray[activity]['theta'] * ( time[event_2] - time[event_1] + zwait[activity] * T)
                 feas_cut += solution_ray[activity]['lamda'] * (- time[event_2] + time[event_1] - zwait[activity] * T + U_a + M)
                 feas_cut += solution_ray[activity]['kappa'] * (- time[event_2] + time[event_1] - zwait[activity] * T + y[activity] + M_2)
            if activity_type == 'wende':
                 feas_cut += solution_ray[activity]['theta'] * ( time[event_2] - time[event_1] + zwende[activity] * T)
                 feas_cut += solution_ray[activity]['lamda'] * (- time[event_2] + time[event_1] - zwende[activity] * T + U_a + M)
                 feas_cut += solution_ray[activity]['kappa'] * (- time[event_2] + time[event_1] - zwende[activity] * T + y[activity] + M_2)
                 
        for activity in activities:
            activity_type = activities[activity][3]
            
            if activity_type == 'trans':
                event_1 = activity[0]
                line_1 = event_1[2]
                event_2 = activity[1]
                line_2 = event_2[2]
                L_a = activities[activity][0]
                U_a = activities[activity][1]
                if line_1 in line_alternatives and line_2 in line_alternatives:
                    feas_cut += solution_ray[activity]['theta'] * ( time[event_2] - time[event_1] + ztrans[activity] * T + L_a)
                    feas_cut += solution_ray[activity]['lamda'] * (- time[event_2] + time[event_1] - ztrans[activity] * T + U_a + 2*M)
                    feas_cut += solution_ray[activity]['kappa'] * (- time[event_2] + time[event_1] - ztrans[activity] * T + y[activity] + 2*M_2)
                elif line_1 in line_alternatives and line_2 not in line_alternatives:
                    time_event_2 = events[event_2][1]
                    feas_cut += solution_ray[activity]['theta'] * ( time_event_2 - time[event_1] + ztrans[activity] * T)
                    feas_cut += solution_ray[activity]['lamda'] * (- time_event_2 + time[event_1] - ztrans[activity] * T + U_a + M)
                    feas_cut += solution_ray[activity]['kappa'] * (- time_event_2 + time[event_1] - ztrans[activity] * T + y[activity] + M_2)
                elif line_1 not in line_alternatives and line_2 in line_alternatives:
                    time_event_1 = events[event_1][1]
                    feas_cut += solution_ray[activity]['theta'] * ( time[event_2] - time_event_1 + ztrans[activity] * T)
                    feas_cut += solution_ray[activity]['lamda'] * (- time[event_2] + time_event_1 - ztrans[activity] * T + U_a + M)
                    feas_cut += solution_ray[activity]['kappa'] * (- time[event_2] + time_event_1 - ztrans[activity] * T + y[activity] + M_2)
            
            if activity_type == 'headway':
                event_1 = activity[0]
                line_1 = event_1[2]
                event_2 = activity[1]
                line_2 = event_2[2]
                L_a = activities[activity][0]
                U_a = activities[activity][1]
                if line_1 in line_alternatives and line_2 in line_alternatives:
                    feas_cut += solution_ray[activity]['theta'] * ( time[event_2] - time[event_1] + zhead[activity] * T + L_a)
                    feas_cut += solution_ray[activity]['lamda'] * (- time[event_2] + time[event_1] - zhead[activity] * T + U_a + 2*M)
                    feas_cut += solution_ray[activity]['kappa'] * (- time[event_2] + time[event_1] - zhead[activity] * T + y[activity] + 2*M_2)
                elif line_1 in line_alternatives and line_2 not in line_alternatives:
                    time_event_2 = events[event_2][1]
                    feas_cut += solution_ray[activity]['theta'] * ( time_event_2 - time[event_1] + zhead[activity] * T)
                    feas_cut += solution_ray[activity]['lamda'] * (- time_event_2 + time[event_1] - zhead[activity] * T + U_a + M)
                    feas_cut += solution_ray[activity]['kappa'] * (- time_event_2 + time[event_1] - zhead[activity] * T + y[activity] + M_2)
                elif line_1 not in line_alternatives and line_2 in line_alternatives:
                    time_event_1 = events[event_1][1]
                    feas_cut += solution_ray[activity]['theta'] * ( time[event_2] - time_event_1 + zhead[activity] * T)
                    feas_cut += solution_ray[activity]['lamda'] * (- time[event_2] + time_event_1 - zhead[activity] * T + U_a + M)
                    feas_cut += solution_ray[activity]['kappa'] * (- time[event_2] + time_event_1 - zhead[activity] * T + y[activity] + M_2)
        m.addConstr(feas_cut <= 0, "feasibility_cut %s" %str(iteration))
        zaehler_4 += 1
            
    ######### Output number constraints ############
    print()
    print('OPTIMIZATION:')
    print('Constraints for iMP: ')
    print(' activity duration bounds: ' + str(zaehler_2))
    print(' optimality cuts: ' + str(zaehler_3))
    print(' feasibility cuts: ' + str(zaehler_4))
    
    if write == True:
        m.write(r".\TT_LP\LP-Dateien\LP_Datei_TT_LP_"+str(iteration)+"_MP.lp")
    
    return(m)


###################################################
######## get fct. Master Problem ##################
###################################################

# get list of drive activities, which will be used definitely
def get_definitely_used_drive_activities(line_alternatives, activities):
    list_of_definitely_used_activities =[]
    for line in line_alternatives:
        # list_activities_of_line_alternatives={line_alterna/tive: list of drive activities of this line_alternative}
        list_activities_of_line_alternatives={}
        for line_alternative in line_alternatives[line]:
            list_activities_of_line_alternatives[line_alternative]=funktionen.get_list_of_drive_activities_for_line_alternative(line_alternative, activities, line_alternatives)
        # take a line alternative and one activity of its list of activities
        # look at every other line alternative 
        # if there is one, for which this activity is not used, then this activity is not taken for the definitely used activities
        for line_alt in list_activities_of_line_alternatives:
            for activity in list_activities_of_line_alternatives[line_alt]:
                act_definitely_used = True
                for line_alt_2 in list_activities_of_line_alternatives:
                    if activity not in list_activities_of_line_alternatives[line_alt_2]:
                        act_definitely_used = False
                if act_definitely_used == True and activity not in list_of_definitely_used_activities:
                    list_of_definitely_used_activities.append(activity)          
    return(list_of_definitely_used_activities)

# get list of wait activities, which will be used definitely
def get_definitely_used_wait_activities(line_alternatives, activities):
    list_of_definitely_used_activities =[]
    for line in line_alternatives:
        # list_activities_of_line_alternatives={line_alternative: list of wait activities of this line_alternative}
        list_activities_of_line_alternatives={}
        for line_alternative in line_alternatives[line]:
            list_activities_of_line_alternatives[line_alternative]=funktionen.get_list_of_wait_activities_for_line_alternative(line_alternative, activities, line_alternatives)
        # take a line alternative and one activity of its list of activities
        # look at every other line alternative 
        # if there is one, for which this activity is not used, then this activity is not taken for the definitely used activities
        for line_alt in list_activities_of_line_alternatives:
            for activity in list_activities_of_line_alternatives[line_alt]:
                act_definitely_used = True
                for line_alt_2 in list_activities_of_line_alternatives:
                    if activity not in list_activities_of_line_alternatives[line_alt_2]:
                        act_definitely_used = False
                if act_definitely_used == True and activity not in list_of_definitely_used_activities:
                    list_of_definitely_used_activities.append(activity)          
    return(list_of_definitely_used_activities)

def get_list_of_not_definitely_used_activities(line_alternatives, activities):
    list_of_not_def_used_activities = []
    list_of_definitely_used_drive_activities = get_definitely_used_drive_activities(line_alternatives, activities)
    list_of_definitely_used_wait_activities = get_definitely_used_wait_activities(line_alternatives, activities)
    
    for activity in activities:
        if activity not in list_of_definitely_used_drive_activities and activity not in list_of_definitely_used_wait_activities:
            list_of_not_def_used_activities.append(activity)
    
    return(list_of_not_def_used_activities)   
    
    








###################################################
############## Subproblem  ########################
###################################################


########### Set up and solve SP ###################

def set_up_and_solve_Subproblem(iteration, opt_cuts, feas_cuts, solution_events, solution_z, solution_y, alpha, edges, events, activities, line_alternatives, T, M,M_2, lines, write):
    
    m_SP = set_up_TT_LP_Subproblem(iteration, solution_events, solution_z, solution_y, alpha, edges, events, activities, line_alternatives, T, M,M_2, lines, write)

    ######### Optimization ############################## 
    
    print()
    m_SP.optimize()        
    print()
            
    ############## Print solution #####################
    
    if m_SP.Status == GRB.OPTIMAL:
        print()
        print('Obj: %g' % m_SP.objVal)       
        print()
        
        if write == True:
            funktionen_sol.write_solution_TT_LP(m_SP, 'TT_LP_'+str(iteration)+'_SP')
        
        solution_edges = get_solution_edges_SP(m_SP, edges)
        solution_lines_under_construction = get_solution_lines_under_construction_SP(m_SP, line_alternatives)
        solution_activities = get_solution_activities_SP(m_SP, activities)

        opt_cuts[iteration]=[solution_edges, solution_lines_under_construction, solution_activities]

    else:
        m_SP.setParam(GRB.Param.DualReductions, 0)     # to see if infeasible or unbounded
        m_SP.optimize()
        
        if m_SP.Status == GRB.INFEASIBLE:
            print()
            print('INFEASIBLE')
            print()
            m_SP.computeIIS() # Irreducible Infeasible Subsystem
            
            if write == True:
                m_SP.write(r".\TT_LP\LP-Dateien\ILP_Datei_TT_LP_"+str(iteration)+"_SP.ilp")
            
        elif m_SP.Status == GRB.UNBOUNDED:
            m_SP.setParam(GRB.Param.InfUnbdInfo, 1)
            m_SP.optimize()
            
            unbounded_ray = {}
            for v in m_SP.getVars():
                unbounded_ray[v]=v.UnbdRay
            for v in unbounded_ray:
                if unbounded_ray[v] != 0:
                    print(v, unbounded_ray[v])
            
            solution_ray={}
            get_solution_ray(m_SP, solution_ray, edges, line_alternatives, activities)
            x = calculate_feas_cut(solution_ray, edges, lines, events, activities, line_alternatives,  solution_events, solution_z, solution_y, T, M, M_2)
    
            if x > 0:
                feas_cuts[iteration]=solution_ray
            else:
                print('Warning: There is an unbounded ray with   cut <=0')
            
    iteration += 1
    return(m_SP, iteration)



######## set Up SubProblem ########################

def set_up_TT_LP_Subproblem(iteration, solution_events, solution_z, solution_y, alpha, edges, events, activities, line_alternatives, T, M,M_2, lines, write):

    m_SP = gp.Model(str(iteration)+'SP')
    
    list_of_active_edges = funktionen.get_list_of_active_edges(edges)
    
    ############ Create variables #####################
    chi = m_SP.addVars(list_of_active_edges, lb= -float('inf'), ub=0, name = "chi")
    psi = m_SP.addVars(list_of_active_edges, lb= -float('inf'), ub=0, name = "psi")
    theta = m_SP.addVars(activities, lb= -float('inf'), ub=0, name = "theta")
    lamda = m_SP.addVars(activities, lb= -float('inf'), ub=0, name = "lamda")
    kappa = m_SP.addVars(activities, lb= -float('inf'), ub=0, name = "kappa")
    my = m_SP.addVars(line_alternatives, lb= -float('inf'), name = "my")
    
    
    ############ Create objective #####################
    
    obj_SP=gp.LinExpr()
    obj_SP = 0
    
    
    for edge in list_of_active_edges:
        fe_min = edges[edge][3]
        fe_max = edges[edge][4]
        zaehler_fixed_lines_of_edge = 0
        for line in lines:
            if line not in line_alternatives:
                for line_richtung in lines[line]:
                    line_edge_list = lines[line][line_richtung][2]
                    if edge in line_edge_list:
                        zaehler_fixed_lines_of_edge += 1
        obj_SP += (-fe_min + zaehler_fixed_lines_of_edge) * chi[edge] + (fe_max - zaehler_fixed_lines_of_edge) * psi[edge]
    for line in line_alternatives:
        obj_SP += my[line]
        
    for activity in activities:  
        activity_type = activities[activity][3]
        event_1 = activity[0]
        event_2 = activity[1]
        line_1 = event_1[2]
        line_2 = event_2[2]
        z_activity = solution_z[activity]
        y_activity = solution_y[activity]
        L_a = activities[activity][0]
        U_a = activities[activity][1]
        
        if activity_type == 'wait' or activity_type == 'drive' or activity_type == 'wende':
            time_event_1 = solution_events[event_1]
            time_event_2 = solution_events[event_2]
            
            obj_SP += theta[activity] * ( time_event_2 - time_event_1 + z_activity * T)
            obj_SP += lamda[activity] * (- time_event_2 + time_event_1 - z_activity * T + U_a + M)
            obj_SP += kappa[activity] * (- time_event_2 + time_event_1 - z_activity * T + y_activity + M_2)
  
        elif activity_type == 'trans' or activity_type == 'headway':
            if line_1 in line_alternatives and line_2 in line_alternatives:
                time_event_1 = solution_events[event_1]
                time_event_2 = solution_events[event_2]
                obj_SP += theta[activity] * ( time_event_2 - time_event_1 + z_activity * T + L_a)
                obj_SP += lamda[activity] * (- time_event_2 + time_event_1 - z_activity * T + U_a + 2*M)
                obj_SP += kappa[activity] * (- time_event_2 + time_event_1 - z_activity * T + y_activity + 2*M_2)
            elif line_1 in line_alternatives and line_2 not in line_alternatives:
                time_event_1 = solution_events[event_1]
                time_event_2 = events[event_2][1]
                obj_SP += theta[activity] * ( time_event_2 - time_event_1 + z_activity * T)
                obj_SP += lamda[activity] * (- time_event_2 + time_event_1 - z_activity * T + U_a + M)
                obj_SP += kappa[activity] * (- time_event_2 + time_event_1 - z_activity * T + y_activity + M_2)
            elif line_1 not in line_alternatives and line_2 in line_alternatives:
                time_event_2 = solution_events[event_2]
                time_event_1 = events[event_1][1]
                obj_SP += theta[activity] * ( time_event_2 - time_event_1 + z_activity * T)
                obj_SP += lamda[activity] * (- time_event_2 + time_event_1 - z_activity * T + U_a + M)
                obj_SP += kappa[activity] * (- time_event_2 + time_event_1 - z_activity * T + y_activity + M_2)
         
    m_SP.setObjective(obj_SP, GRB.MAXIMIZE)        
            
            
    ######### Create constraints ######################
    
    zaehler_1 = 0
    
    for line in line_alternatives:
        for line_alternative in line_alternatives[line]:
            con = gp.LinExpr()
            cost_line = line_alternatives[line][line_alternative][0]
            list_of_activities_line_alt = funktionen.get_list_of_wait_activities_for_line_alternative(line_alternative, activities, line_alternatives)
            list_of_activities_line_alt += funktionen.get_list_of_drive_activities_for_line_alternative(line_alternative, activities, line_alternatives)
            list_of_activities_line_alt += funktionen.get_list_of_wende_activities_for_line_alternative(line_alternative, activities, line_alternatives)
            list_of_activities_line_alt += funktionen.get_list_of_trans_activities_for_line_alternative(line_alternative, activities, line_alternatives)
            list_of_activities_line_alt += funktionen.get_list_of_headway_activities_for_line_alternative(line_alternative, activities, line_alternatives)
            
            # chi und psi
            for line_richtung in line_alternatives[line][line_alternative][1]:
                list_of_edges = line_alternatives[line][line_alternative][1][line_richtung][1]
                for edge in list_of_edges:
                    con += - chi[edge] + psi[edge] 
            # theta und lamda
            for activity in list_of_activities_line_alt:
                L_a = activities[activity][0]
                con += theta[activity] * L_a + lamda[activity] * M + kappa[activity]*M_2
                        
            # my und ny
            con += my[line] 
            m_SP.addConstr( con <= float(alpha) * float(cost_line), "line_alternative %s" %str(line_alternative))
            zaehler_1 += 1
        
            
    ##### Output number of constraints ###########
    print()
    print('OPTIMIZATION:')
    print('Constraints for Subproblem: ')
    print(' line alternatives: ' + str(zaehler_1))
    print()
    
    if write == True:
        m_SP.write(r".\TT_LP\LP-Dateien\LP_Datei_TT_LP_"+str(iteration)+"_SP.lp")
    
    return(m_SP)



    
###################################################
######## Get solution SubProblem ##################
###################################################

def get_solution_edges_SP(m_SP, edges):
    solution_edges = {}
    list_active_edges = funktionen.get_list_of_active_edges(edges)
    for edge in list_active_edges:
        solution_edges[edge]={}
        stop_1 = edge[0]
        stop_2 = edge[1]
        var = m_SP.getVarByName('chi['+str(stop_1)+','+str(stop_2)+']')
        solution_edges[edge]['chi']=var.x
        var = m_SP.getVarByName('psi['+str(stop_1)+','+str(stop_2)+']')
        solution_edges[edge]['psi']=var.x
    return(solution_edges)

def get_solution_lines_under_construction_SP(m_SP, line_alternatives):
    solution_lines_under_construction = {}
    for line in line_alternatives:
        line_number = line[0]
        line_zuggruppe = line[1]
        var = m_SP.getVarByName('my['+str(line_number)+','+str(line_zuggruppe)+']')
        solution_lines_under_construction[line]={}
        solution_lines_under_construction[line]['my']=var.x
    return(solution_lines_under_construction)

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
        var = m_SP.getVarByName('kappa['+str(event_1)+','+ str(event_2)+']')
        solution_activities[activity]['kappa']=var.x
    return(solution_activities)


def get_solution_ray(m_SP, solution_ray, edges, line_alternatives, activities):
    list_active_edges = funktionen.get_list_of_active_edges(edges)
    for edge in list_active_edges:
        stop_1 = edge[0]
        stop_2 = edge[1]
        solution_ray[edge]= {}
        var = m_SP.getVarByName('chi['+str(stop_1)+','+str(stop_2)+']')
        solution_ray[edge]['chi']=var.UnbdRay
        var = m_SP.getVarByName('psi['+str(stop_1)+','+str(stop_2)+']')
        solution_ray[edge]['psi']=var.UnbdRay
    
    for line in line_alternatives:
        line_number = line[0]
        line_zuggruppe = line[1]
        solution_ray[line]={}
        var = m_SP.getVarByName('my['+str(line_number)+','+str(line_zuggruppe)+']')
        solution_ray[line]['my']=var.UnbdRay
    
    for activity in activities:
        event_1 = activity[0]
        event_2 = activity[1]
        solution_ray[activity]={}
        var = m_SP.getVarByName('theta['+str(event_1)+','+ str(event_2)+']')
        solution_ray[activity]['theta']=var.UnbdRay
        var = m_SP.getVarByName('lamda['+str(event_1)+','+ str(event_2)+']')
        solution_ray[activity]['lamda']=var.UnbdRay
        var = m_SP.getVarByName('kappa['+str(event_1)+','+ str(event_2)+']')
        solution_ray[activity]['kappa']=var.UnbdRay
    
    
###################################################
######## Feasibility Cuts SubProblem ##############
###################################################


def calculate_feas_cut(solution_ray, edges, lines, events, activities, line_alternatives,  solution_events, solution_z, solution_y, T, M, M_2):
    x = 0
    
    list_of_active_edges = funktionen.get_list_of_active_edges(edges)
    
    for edge in list_of_active_edges:
        fe_min = edges[edge][3]
        fe_max = edges[edge][4]
        zaehler_fixed_lines_of_edge = 0
        for line in lines:
            if line not in line_alternatives:
                for line_richtung in lines[line]:
                    line_edge_list = lines[line][line_richtung][2]
                    if edge in line_edge_list:
                        zaehler_fixed_lines_of_edge += 1
        x += (-fe_min + zaehler_fixed_lines_of_edge) * solution_ray[edge]['chi'] + (fe_max - zaehler_fixed_lines_of_edge) * solution_ray[edge]['psi']
    for line in line_alternatives:
        x += solution_ray[line]['my']
        
    for activity in activities:  
        activity_type = activities[activity][3]
        event_1 = activity[0]
        event_2 = activity[1]
        line_1 = event_1[2]
        line_2 = event_2[2]
        z_activity = solution_z[activity]
        y_activity = solution_y[activity]
        L_a = activities[activity][0]
        U_a = activities[activity][1]
        
        if activity_type == 'wait' or activity_type == 'drive' or activity_type == 'wende':
            time_event_1 = solution_events[event_1]
            time_event_2 = solution_events[event_2]
            
            x += solution_ray[activity]['theta'] * ( time_event_2 - time_event_1 + z_activity * T)
            x += solution_ray[activity]['lamda'] * (- time_event_2 + time_event_1 - z_activity * T + U_a + M)
            x += solution_ray[activity]['kappa'] * (- time_event_2 + time_event_1 - z_activity * T + y_activity + M_2)
  
        elif activity_type == 'trans' or activity_type == 'headway':
            if line_1 in line_alternatives and line_2 in line_alternatives:
                time_event_1 = solution_events[event_1]
                time_event_2 = solution_events[event_2]
                x += solution_ray[activity]['theta'] * ( time_event_2 - time_event_1 + z_activity * T + L_a)
                x += solution_ray[activity]['lamda'] * (- time_event_2 + time_event_1 - z_activity * T + U_a + 2*M)
                x += solution_ray[activity]['kappa'] * (- time_event_2 + time_event_1 - z_activity * T + y_activity + 2*M_2)
            elif line_1 in line_alternatives and line_2 not in line_alternatives:
                time_event_1 = solution_events[event_1]
                time_event_2 = events[event_2][1]
                x += solution_ray[activity]['theta'] * ( time_event_2 - time_event_1 + z_activity * T)
                x += solution_ray[activity]['lamda'] * (- time_event_2 + time_event_1 - z_activity * T + U_a + M)
                x += solution_ray[activity]['kappa'] * (- time_event_2 + time_event_1 - z_activity * T + y_activity + M_2)
            elif line_1 not in line_alternatives and line_2 in line_alternatives:
                time_event_2 = solution_events[event_2]
                time_event_1 = events[event_1][1]
                x += solution_ray[activity]['theta'] * ( time_event_2 - time_event_1 + z_activity * T)
                x += solution_ray[activity]['lamda'] * (- time_event_2 + time_event_1 - z_activity * T + U_a + M)
                x += solution_ray[activity]['kappa'] * (- time_event_2 + time_event_1 - z_activity * T + y_activity + M_2)
    return(x)




###################################################
####### Get Primal Values of SubProblem ###########
###################################################

def get_primal_values_of_SubProblem(m_SP, iteration, line_alternatives, write):
    solution_frequencies = funktionen_sol.create_default_solution_frequencies(line_alternatives)

    constraints = m_SP.getConstrs()
    
    for i in range(0,len(constraints)):
        constraint = constraints[i]
        pi_value = constraint.getAttr('Pi')
        
        constraint_name = constraint.getAttr('ConstrName')
        con_split_1 = constraint_name.split("'")
        
        line_nummer = con_split_1[1]
        line_zuggruppe = con_split_1[3]
        line_alternative_nummer = con_split_1[5]
        
        line = (line_nummer, line_zuggruppe)
        line_alternative = (line_nummer, line_zuggruppe, line_alternative_nummer)
        solution_frequencies[line][line_alternative] = pi_value
        
        if write == True:
            funktionen_sol.write_solution_frequencies_TT_LP('TT_LP_'+str(iteration)+'_SP', solution_frequencies)
    return (solution_frequencies)