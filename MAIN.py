# -*- coding: utf-8 -*-
"""
Created on 04. November 2022
Last Update on 29. April 2023

@author: Sarah Burchert

Integrated Model for Alternative Based Line Planning and Periodic Timetabling
- Benders Decomposition Approaches
- S-Bahn Berlin Scenario

"""

import gurobipy as gp
from gurobipy import GRB
import funktionen
import funktionen_sol
import funktionen_vis_net
import funktionen_ILT
import funktionen_TT_LP
import funktionen_LP_TT
import funktionen_LP_TT_CB
import funktionen_LP_TT_CBD
import time


start = time.time()
###################################################
############# Set Up Parameters ###################
###################################################
way_1 = 'ILT'
way_2 = 'TT-LP'
way_3 = 'LP-TT'
way_4 = 'LP_TT_CBD'
way_5 = 'LP_TT_CBD2'

# choose optimization approach
way_of_opt = way_1

# choose set of line alternatives: A  or B
set_LA = 'A'

# number of maximal iteration steps
max_iter = 1000

# choose objective weights: alpha for line planning, beta for timetabling
alpha = 1
beta = 1

# choose line cost weight
alphac = 1
betac = 1

# set if you want some more data written: false or true
write = False

# set if you want to draw visualization_ false or true
draw = False

###################################################    
############# network data and parameter ##########
###################################################

k=10  # timetable variables have to be integer, but have 1 decimal place in readingdata

T = 20*k  
M = 25*k
M_2= 50*k  # M_2 is M' from integrated model in thesis

h=2.5*k   # headwaytime

# lower and upper bounds of edges/activities
La_wait= 0.4*k
Ua_wait = h-0.1*k
La_trans = 2.9*k
Ua_trans = T+2.8*k
   # wende activities are special cases of waiting activities, it's the turnaround time of lines which go back and forth
La_wende = 3*k              
Ua_wende = T+2.9*k
fahrzeit_puffer = 0*k

fe_min = 1
fe_max = 8

# activity weights
w_drive=1
w_wait=3
w_trans=5
w_wende=0
w_headway=0

# Input Data
betriebsstellen_datei="read_betriebsstellen.csv"
strecken_datei="read_strecken.csv"
regelfahrplan_datei="read_regelfahrplan.csv"

if set_LA =='A':
    line_costs_data="read_linecost_attributes_A.csv"
    line_alternatives_data = "read_Alternativlinien_A.csv"
elif set_LA =='B':
    line_costs_data="read_linecost_attributes_B.csv"
    line_alternatives_data = "read_Alternativlinien_B.csv"


# list of stops and edges blocked by construction site
construction_stops = ['BJUN','BBEU','BWH','BWED']
construction_edges = [('BWES','BJUN'),('BJUN','BBEU'),('BBEU','BWH'),('BWH','BWED'),('BWED','BGB'), 
                      ('BJUN','BWES'),('BBEU','BJUN'),('BWH','BBEU'),('BWED','BWH'),('BGB','BWED')]

# list of stops for visualisation
list_of_stops = ['BSKR', 'BTHF', 'BHER', 'BNK', 'BKHD', 'BBMW', 'BSW']

# Lower Bound TT Objective Part (computed with setting alpha = 0)
L_TT_B=253489
L_TT_A=296700

if set_LA == 'A':   
    L_TT = L_TT_A
elif set_LA == 'B':
    L_TT = L_TT_B

###################################################    
############# Declaration of variables ############
###################################################
#stops : { abbreviation: 
    # longname, transfer? y/n, list of lines, directions {W: {line: linienrichtung} , O: , N: , S: }, active? y/n, x-Koord, y_Koord
stops= {}

# edges : {( 'stop',stop') : 
    # longname, active? y/n, {Linie: Fahrzeit}, f_min, f_max
edges ={}

# lines : { Line : 
    # {Linienrichtung :
        # cost of line, {stop:  'start', 'end' ''}, list of edges
lines = {}

# regelfahrplan : { Linienname :
    # { Linienrichtung:
        # { stop:
            # { 'arr': timetable, haltezeit
            # { 'dep': timetable, fahrzeit 
regelfahrplan={} 
        

# line_alternatives : { Line :
    # { Line_alternative : 
        # c_l, {Linienrichtung : {stop:  'start', 'end' ''}, list of edges }
line_alternatives = {}

# events: { event = (stop, 'arr'/'dep', line, line_richtung) :
    # fixed? y/n, time
events=gp.tupledict()

# activities:  { activity = (event_1, event_2): 
    # La_activity, Ua_activity, w_a, 'drive'/'wait'/'trans'/'wende'/'headway'
activities=gp.tupledict()


## Line = (Liniennummer, Zuggruppe) Bsp: ('S1', 'P')
## Linienrichtung = (Liniennummer, Zuggruppe, Start, Ende) Bsp: ('S1', 'P', 'BORB', 'BWSS')
## Linienalternative = (Liniennummer, Zuggruppe, Linienalternativennummer) Bsp: ('S45', 'U', 'A1')
## Linienalternativenrichtung = (Liniennummer, Zuggruppe, Linienalternativennummer, Start, Ende) Bsp: ('S45', 'U', 'A1', 'BFBB', 'BSKR')


###################################################
############# MAIN ################################
###################################################


########### Reading Data ##########################
funktionen.read_betriebsstellen(betriebsstellen_datei, stops)
# -> stops gets filled with stops[stop_abbreviation]=[stop_longname, stop_transfer, [], {"S":[],"N":[],"W":[],"O":[]}]

funktionen.read_regelfahrplan(regelfahrplan_datei, regelfahrplan, k, stops, edges, lines, fe_min, fe_max)
# -> stops gets filled with list of lines and corresponding directions with list of lines
# -> regelfahrplan gets filled with regelfahrplan[line][line_richtung][line_stop]={'arr': [timetable, haltezeit]}
#                                   regelfahrplan[line][line_richtung][line_stop]={'dep': [timetable, fahrzeit]} 
# -> edges gets filled with edges[edge]=[longname_edge, 'y', {Linie: Fahrzeit}, fe_min,fe_max]
# -> lines gets filled with lines[line] = {Linienrichtung : cost of line, {stop:  'start', 'end' ''}, list of edges
 
funktionen.read_line_alternatives(line_alternatives_data, line_alternatives, k, stops, edges, fe_min, fe_max)
# -> line_alternatives wird gefüllt mit line_alternatives[line][linienalternative][c_l, {Linienrichtung : [{stop:  'start', 'end' ''}, list of edges]}]  

funktionen.read_linecost_attributes(line_costs_data, line_alternatives, alphac, betac)
# -> in line_alternatives: setting line costs

# Writing data
if write == True:
    funktionen.write_stops(stops)
    funktionen.write_edges(edges)
    funktionen.write_lines(lines)
    funktionen.write_regelfahrplan(regelfahrplan)
    funktionen.write_line_alternatives(line_alternatives)
    funktionen.write_list_of_line_alternatives(line_alternatives)


list_of_line_alternatives = funktionen.get_list_of_line_alternatives(line_alternatives)
list_of_fixed_lines = funktionen.get_list_of_fixed_lines(lines, line_alternatives)
list_of_active_edges = funktionen.get_list_of_active_edges(edges)
list_of_active_stops = funktionen.get_list_of_active_stops(stops)
number_of_lines_under_construction = len(line_alternatives)
number_of_line_alternatives = len(list_of_line_alternatives)
number_of_fixed_lines = len(list_of_fixed_lines)
number_of_active_edges = len(list_of_active_edges)
number_of_active_stops = len(list_of_active_stops)


print('Network')
print('Number of active edges: ' + str(number_of_active_edges))
print('Number of active/transfer stops: ' + str(number_of_active_stops))
print('Number of lines under construction: ' + str(number_of_lines_under_construction))
print('Number of line alternatives: '+str(number_of_line_alternatives))
print('Number of fixed lines: '+str(number_of_fixed_lines))
print()

############ Set Up EAN ##########################

funktionen.create_EAN(events, activities, line_alternatives, lines, stops, regelfahrplan, w_drive, edges, fahrzeit_puffer, w_wait, La_wait, Ua_wait, La_wende, Ua_wende, w_wende, La_trans, Ua_trans, w_trans, h, w_headway, T)

if write == True:
    funktionen.write_events_for_lines(events, lines)
    funktionen.write_wait_drive_wende_activities_for_lines(activities, lines)
    funktionen.write_trans_activities_for_stops(activities, stops)
    funktionen.write_headway_activities_for_stops(activities, stops)

list_of_fixed_events = funktionen.get_list_of_fixed_events(events)
list_of_not_fixed_events = funktionen.get_list_of_not_fixed_events(events)
list_of_wait_activities = funktionen.get_list_of_wait_activities(activities)
list_of_drive_activities = funktionen.get_list_of_drive_activities(activities)
list_of_wende_activities = funktionen.get_list_of_wende_activities(activities)
list_of_trans_activities = funktionen.get_list_of_trans_activities(activities)
list_of_headway_activities = funktionen.get_list_of_headway_activities(activities)
list_of_wait_drive_wende_activities = funktionen.get_list_of_wait_drive_wende_activities(activities)

number_of_events = len(events)
number_of_fixed_events = len(list_of_fixed_events)
number_of_not_fixed_events = len(list_of_not_fixed_events)
number_of_activities = len(activities)
number_of_wait_activities = len(list_of_wait_activities)
number_of_drive_activities = len(list_of_drive_activities)
number_of_wende_activities = len(list_of_wende_activities)
number_of_trans_activities = len(list_of_trans_activities)
number_of_headway_activities = len(list_of_headway_activities)

print('EAN')
print('Number of events: ' + str(number_of_events))
print('-> events of fixed lines: ' + str(number_of_fixed_events)) 
print('-> events of line alternatives: ' + str(number_of_not_fixed_events))
print('Number of activities: ' + str(number_of_activities))
print('-> wait activities: ' + str(number_of_wait_activities)) 
print('-> drive activities: ' + str(number_of_drive_activities))
print('-> wende activities: ' + str(number_of_wende_activities))
print('-> transfer activities: ' + str(number_of_trans_activities))
print('-> headway activities: ' + str(number_of_headway_activities))
print()






###################################################
######## GUROBI - ILT #############################
###################################################

if way_of_opt == way_1:

    (m, m_solution_frequencies, m_solution_events, m_solution_z, m_solution_y) = funktionen_ILT.set_up_and_solve_ILT(T, alpha, beta,M, M_2, h, k, events, activities, line_alternatives, edges, lines, stops, write)
    
    end = time.time()
    print('Computing time is: ' + str(end-start))
    if draw == True:
        G_net_1 = funktionen_vis_net.draw_graph_of_network('ILT', list_of_stops, T, k, m_solution_events, m_solution_frequencies,m_solution_y, activities, events, stops, edges, line_alternatives, lines)






###################################################
##### GUROBI - TT  LP (Approach 1) ################
###################################################
elif way_of_opt == way_2:
    iteration = 0
    opt_cuts = {}
    feas_cuts = {}
    optimal = False
    
    obj_MP = {}
    obj_eta = {}
    obj_SP = {}
    it_solution_frequencies = {}
     
    
    while iteration < max_iter and optimal == False:
        print()
        print('Iteration: '+str(iteration))
        print()
        
        # set up and solve master problem (timetabling)
        (m_MP, m_MP_solution_events, m_MP_solution_z, m_MP_solution_y) = funktionen_TT_LP.set_up_and_solve_MP(iteration, opt_cuts, feas_cuts, T, beta,M,M_2, h, k, events, activities, line_alternatives, edges, lines, write)
        
        # get objective of master problem and value eta
        obj_MP[iteration] = m_MP.objVal
        eta_var = m_MP.getVarByName('eta')
        obj_eta[iteration] = eta_var.x
        
        # set up and solve subproblem (line planning)
        (m_SP, iteration) = funktionen_TT_LP.set_up_and_solve_Subproblem(iteration, opt_cuts, feas_cuts,  m_MP_solution_events,  m_MP_solution_z, m_MP_solution_y, alpha, edges, events, activities, line_alternatives, T, M,M_2, lines, write)
        
        # it_draw is iteration for further evaluations and drawing since iteration is increased by 1 in function before
        it_draw = int(iteration)-1
        
        # Subproblem Obj und Optimality Cuts
        if m_SP.Status == GRB.OPTIMAL:
    		  # Subproblem Primal Values
              m_MP_solution_frequencies = funktionen_TT_LP.get_primal_values_of_SubProblem(m_SP,it_draw, line_alternatives, write)
              it_solution_frequencies[it_draw] = m_MP_solution_frequencies
              obj_SP[it_draw]=m_SP.objVal
              if m_SP.objVal == obj_eta[it_draw]:
                  optimal = True
              if write == True:
                  funktionen_sol.write_opt_cuts_TT_LP(m_MP, m_SP, opt_cuts, it_draw)
              #Visualization
              if draw == True:
                  G_TT_LP_MP = funktionen_vis_net.draw_graph_of_network('TT_LP_'+str(it_draw), list_of_stops, T, k, m_MP_solution_events, m_MP_solution_frequencies, m_MP_solution_y, activities, events, stops, edges, line_alternatives, lines) 
        # Subproblem Feasibility Cuts      
        elif m_SP.Status == GRB.UNBOUNDED and write == True:            
            funktionen_sol.write_feas_cuts_TT_LP(feas_cuts, it_draw, m_MP) 
            
        if set_LA == 'A':
            funktionen_sol.write_solution_objective_and_line_frequencies_TT_LP_A(obj_MP, obj_eta, obj_SP, it_solution_frequencies)                      
        elif set_LA == 'B':
            funktionen_sol.write_solution_objective_and_line_frequencies_TT_LP_B(obj_MP, obj_eta, obj_SP, it_solution_frequencies)
    
    end = time.time()
    print('Computing time is: ' + str(end-start))
    if set_LA == 'A':
        funktionen_sol.write_solution_objective_and_line_frequencies_TT_LP_A(obj_MP, obj_eta, obj_SP, it_solution_frequencies)                      
    elif set_LA == 'B':
        funktionen_sol.write_solution_objective_and_line_frequencies_TT_LP_B(obj_MP, obj_eta, obj_SP, it_solution_frequencies)                      
    
    
    
    
    
    
###################################################
######## GUROBI - LP  TT (Approach 2) #############
###################################################
elif way_of_opt == way_3:
    iteration = 0
    opt_cuts = {}
    feas_cuts = {}
    optimal = False    
    obj_MP = {}
    obj_eta = {}
    obj_SP = {}
    it_solution_frequencies = {}
     
    while iteration < max_iter and optimal == False: 
        print()
        print('Iteration: '+str(iteration))
        print()
        
        # set up and solve master problem (line planning)
        (m_MP, m_MP_solution_frequencies) = funktionen_LP_TT.set_up_and_solve_MP(iteration, opt_cuts, feas_cuts, T, alpha,M,M_2, h, k, events, activities, line_alternatives, edges, lines, stops, write)
        
        # get objective of master problem and value eta
        obj_MP[iteration] = m_MP.objVal
        eta_var = m_MP.getVarByName('eta')
        obj_eta[iteration] = eta_var.x
        
        # set up and solve subproblem (timetabling)
        (m_SP, iteration) = funktionen_LP_TT.set_up_and_solve_Subproblem(iteration, opt_cuts, feas_cuts, m_MP_solution_frequencies, beta, edges, events, activities, line_alternatives, T, M ,M_2, k, write)
        
        #it_draw is iteration for further evaluations and drawing since iteration is increased by 1 in function before
        it_draw = int(iteration)-1
        it_solution_frequencies[it_draw] = m_MP_solution_frequencies
        
        # Subproblem Obj und Optimality Cuts
        if m_SP.Status == GRB.OPTIMAL:
		    # Subproblem Primal Values
            (m_MP_solution_events, m_MP_solution_y, m_MP_solution_z) = funktionen_LP_TT.get_primal_values_of_SubProblem(m_SP, events, activities)
		
            obj_SP[it_draw]=m_SP.objVal
            if m_SP.objVal == obj_eta[it_draw]:
                optimal = True
                
            if write == True:
                funktionen_sol.write_opt_cuts_LP_TT(m_MP, m_SP, opt_cuts, it_draw)
            #Visualization
            if draw == True:
                G_LP_TT_MP = funktionen_vis_net.draw_graph_of_network('LP_TT_'+str(it_draw), list_of_stops, T, k, m_MP_solution_events, m_MP_solution_frequencies, m_MP_solution_y, activities, events, stops, edges, line_alternatives, lines) 
        # Subproblem Feasibility Cuts     
        elif m_SP.Status == GRB.UNBOUNDED and write == True:
            funktionen_sol.write_feas_cuts_LP_TT(feas_cuts, it_draw, m_MP)
            
    end = time.time()
    print('Computing time is: ' + str(end-start))     
    if draw == True:
        G_LP_TT_MP = funktionen_vis_net.draw_graph_of_network('LP_TT_'+str(it_draw)+'_optimal', list_of_stops, T, k, m_MP_solution_events, m_MP_solution_frequencies, m_MP_solution_y, activities, events, stops, edges, line_alternatives, lines) 
    if set_LA == 'A':
        funktionen_sol.write_solution_objective_and_line_frequencies_LP_TT_A(obj_MP, obj_eta, obj_SP, it_solution_frequencies)        
    elif set_LA == 'B':
        funktionen_sol.write_solution_objective_and_line_frequencies_LP_TT_B(obj_MP, obj_eta, obj_SP, it_solution_frequencies)        
    
    
    
###################################################
### GUROBI - LP  TT (Approach 3) ##################
###################################################
elif way_of_opt == way_4:
    iteration = 0
    opt_cuts = {}
    feas_cuts = {}
    optimal = False
    
    obj_MP = {}
    obj_eta = {}
    obj_SP = {}
    it_solution_frequencies = {}
     
    while iteration < max_iter and optimal == False: 
        print()
        print('Iteration: '+str(iteration))
        print()
        
        # set up and solve master problem (line planning)
        (m_MP, m_MP_solution_frequencies) = funktionen_LP_TT_CBD.set_up_and_solve_MP(iteration, opt_cuts, feas_cuts, T, alpha,M,M_2, h, k, events, activities, line_alternatives, edges, lines, stops, L_TT)
        
        # get objective of master problem and value eta
        obj_MP[iteration] = m_MP.objVal
        eta_var = m_MP.getVarByName('eta')
        obj_eta[iteration] = eta_var.x
        
        # set up and solve subproblem (timetabling)
        (m_SP, iteration) = funktionen_LP_TT_CBD.set_up_and_solve_integer_Subproblem(iteration, opt_cuts, feas_cuts, m_MP_solution_frequencies, beta, h, edges, events, activities, line_alternatives, T, M ,M_2, k)
        
        #it_draw is iteration for further evaluations and drawing since iteration is increased by 1 in function before
        it_draw = int(iteration)-1
        it_solution_frequencies[it_draw] = m_MP_solution_frequencies
        
        # Subproblem Obj
        if m_SP.Status == GRB.OPTIMAL:
            obj_SP[it_draw]=m_SP.objVal
            
            # Subproblem Solution Values
            (m_MP_solution_events, m_MP_solution_y, m_MP_solution_z) = funktionen_LP_TT_CBD.get_values_of_SubProblem(m_SP, events, activities)

            if m_SP.objVal == obj_eta[it_draw]:
                optimal = True
                
            #Visualization
            if draw == True:
                G_LP_TT_MP = funktionen_vis_net.draw_graph_of_network('LP_TT_CBD_'+str(it_draw), list_of_stops, T, k, m_MP_solution_events, m_MP_solution_frequencies, m_MP_solution_y, activities, events, stops, edges, line_alternatives, lines) 

    end = time.time()
    print('Computing time is: ' + str(end-start))        
    if set_LA == 'A':    
        funktionen_sol.write_solution_objective_and_line_frequencies_LP_TT_CBD_A(obj_MP, obj_eta, obj_SP, it_solution_frequencies)        
    elif set_LA == 'B':    
        funktionen_sol.write_solution_objective_and_line_frequencies_LP_TT_CBD_B(obj_MP, obj_eta, obj_SP, it_solution_frequencies)        




###################################################
### GUROBI - LP  TT (Approach 4) ##################
###################################################
elif way_of_opt == way_5:
    iteration = 0
    optimal = False
    opt_cuts = {}
    feas_cuts = {}
    
    obj_MP = {}
    obj_eta = {}
    obj_SP = {}
    it_solution_frequencies = {}
     
    while iteration < max_iter and optimal == False: 
        print()
        print('Iteration: '+str(iteration))
        print()
        
        # set up and solve master problem (line planning)
        (m_MP, m_MP_solution_frequencies) = funktionen_LP_TT_CB.set_up_and_solve_MP(iteration, opt_cuts, feas_cuts, T, alpha,M,M_2, h, k, events, activities, line_alternatives, edges, lines, stops, L_TT)
        
        # get objective of master problem and value eta
        obj_MP[iteration] = m_MP.objVal
        eta_var = m_MP.getVarByName('eta')
        obj_eta[iteration] = eta_var.x
        
        # set up and solve subproblem (timetabling)
        (m_SP, iteration) = funktionen_LP_TT_CB.set_up_and_solve_Subproblem(iteration, opt_cuts, feas_cuts, m_MP_solution_frequencies, beta, edges, events, activities, line_alternatives, T, M ,M_2, k,h, write)
        
        #it_draw is iteration for further evaluations and drawing since iteration is increased by 1 in function before
        it_draw = int(iteration)-1
        it_solution_frequencies[it_draw] = m_MP_solution_frequencies
        
        # Subproblem Obj und Optimality Cuts
        if m_SP.Status == GRB.OPTIMAL:
		    # Subproblem Primal Values
            (m_MP_solution_events, m_MP_solution_y, m_MP_solution_z) = funktionen_LP_TT.get_primal_values_of_SubProblem(m_SP, events, activities)
		
            obj_SP[it_draw]=m_SP.objVal
            
            if m_SP.objVal == obj_eta[it_draw]:
                optimal = True
            
            #Visualization
            if draw == True:
                G_LP_TT_MP = funktionen_vis_net.draw_graph_of_network('LP_TT_CB_'+str(it_draw), list_of_stops, T, k, m_MP_solution_events, m_MP_solution_frequencies, m_MP_solution_y, activities, events, stops, edges, line_alternatives, lines) 
                
        if set_LA == 'A':    
               funktionen_sol.write_solution_objective_and_line_frequencies_LP_TT_CB_A(obj_MP, obj_eta, obj_SP, it_solution_frequencies)        
        elif set_LA == 'B':    
               funktionen_sol.write_solution_objective_and_line_frequencies_LP_TT_CB_B(obj_MP, obj_eta, obj_SP, it_solution_frequencies)    
            
            
    end_1 = time.time()
    m_SP_opt = funktionen_LP_TT_CB.set_up_LP_TT_integer_Subproblem(iteration-1, m_MP_solution_frequencies, beta, h, edges, events, activities, line_alternatives, T, M ,M_2, k)
    m_SP_opt.optimize()        
    print()
    
    end = time.time()
    print('Computing time for opt line plan is: ' + str(end_1-start))
    print('Computing time for opt solution is: ' + str(end-start))
    
   
    if set_LA == 'A':    
           funktionen_sol.write_solution_objective_and_line_frequencies_LP_TT_CB_A(obj_MP, obj_eta, obj_SP, it_solution_frequencies)        
    elif set_LA == 'B':    
           funktionen_sol.write_solution_objective_and_line_frequencies_LP_TT_CB_B(obj_MP, obj_eta, obj_SP, it_solution_frequencies)
           
           
    #Visualization
    if draw == True:
        G_LP_TT_MP = funktionen_vis_net.draw_graph_of_network('LP_TT_CB_'+ str(iteration)+'_optimal', list_of_stops, T, k, m_MP_solution_events, m_MP_solution_frequencies, m_MP_solution_y, activities, events, stops, edges, line_alternatives, lines)