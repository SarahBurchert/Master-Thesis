# -*- coding: utf-8 -*-
"""
@author: Sarah Burchert

"""

import funktionen
import funktionen_sol
import networkx as nx
import matplotlib.pyplot as plt
   

###################################################          
######## Functions Visualrization #################
###################################################



def draw_graph_of_network(Dateiname, list_of_stops, T, k, solution_events, solution_frequencies, solution_y, activities, events, stops, edges, line_alternatives, lines):
    
    print()
    print('Creating Visualization!')
    print()
    
    plt.figure('network', figsize=(40,10))
    G_net = nx.DiGraph()   
    
    list_of_lines = []
    for stop in list_of_stops:
        add_events_wait_activities_of_stop(G_net, stop, T, k, solution_events, solution_frequencies, solution_y, activities, events, stops, line_alternatives, list_of_lines)
    add_position_to_nodes(G_net, list_of_lines, stops)
    add_nodes_for_line_str(G_net, list_of_lines)
    add_edges_of_driving_activities(G_net, list_of_stops, solution_events,solution_y, activities, T, k)
    add_edges_of_transfer_activities(G_net, list_of_stops, solution_events, solution_y, events, activities, T, k)
    
    
    draw_graph(G_net)

    plt.savefig(r'.\Visualization\bahn_network_'+str(Dateiname)+'.pdf')
    plt.close()
      
    return(G_net)


def draw_graph(G):
  pos = nx.get_node_attributes(G, 'pos') 
  for node in pos:
      pos[node] = (pos[node][0]*10, pos[node][1]*10)
  
  # draw nodes
  list_nodes_choosen = [n for (n, attribute) in G.nodes(data=True) if attribute['color'] == 'choosen']
  list_nodes_not_choosen = [n for (n, attribute) in G.nodes(data=True) if attribute['color'] == 'not_choosen']
  list_nodes_fixed_line = [n for (n, attribute) in G.nodes(data=True) if attribute['color'] == 'fixed_line']
  list_nodes_white = [n for (n, attribute) in G.nodes(data=True) if attribute['color'] == 'white'] 
  nx.draw_networkx_nodes(list_nodes_choosen, pos, node_size=800, node_color = '#ffd966', node_shape = 's')
  nx.draw_networkx_nodes(list_nodes_not_choosen, pos, node_size=800, node_color = '#bcbcbc', node_shape = 's')
  nx.draw_networkx_nodes(list_nodes_fixed_line, pos, node_size=800, node_color = '#9fc5e8', node_shape = 's')
  nx.draw_networkx_nodes(list_nodes_white, pos, node_size=200, node_color = 'white')
  
  # node_labels
  node_labels_time = nx.get_node_attributes(G, 'time')
  node_labels_lines = nx.get_node_attributes(G, 'line')
  node_labels_arrdep = nx.get_node_attributes(G, 'arr/dep')
  node_labels_stop = nx.get_node_attributes(G, 'stop')
  nx.draw_networkx_labels(G, pos, alpha = 1, font_size = 15, labels = node_labels_time)
  nx.draw_networkx_labels(G, pos, font_size = 15, labels = node_labels_lines)
  nx.draw_networkx_labels(G, pos, font_size = 15, labels = node_labels_arrdep)
  nx.draw_networkx_labels(G, pos, font_size = 15, labels = node_labels_stop)
  
  # wait edges
  #list_wait_edges = [(e_1, e_2) for (e_1, e_2, attribute) in G.edges(data=True) if attribute['activity_type'] == 'wait']
  #nx.draw_networkx_edges(G, pos,list_wait_edges,  node_size = 800, arrowsize= 25)
  # drive edges
  list_drive_edges = [(e_1, e_2) for (e_1, e_2, attribute) in G.edges(data=True) if attribute['activity_type'] == 'drive']     
  nx.draw_networkx_edges(G, pos, list_drive_edges, node_size = 800, arrowsize= 25)
  # transfer edges
  list_trans_edges = [(e_1, e_2) for (e_1, e_2, attribute) in G.edges(data=True) if attribute['activity_type'] == 'transfer']     
  nx.draw_networkx_edges(G, pos, list_trans_edges, node_size = 800, arrowsize= 25)
  # edges from str Feld arr - dep
  list_str_edges = [(e_1, e_2) for (e_1, e_2, attribute) in G.edges(data=True) if attribute['activity_type'] == 'str']     
  nx.draw_networkx_edges(G, pos, list_str_edges, node_size = 1200, arrowsize= 10)
  
  # edge_labels
  edge_labels = nx.get_edge_attributes(G, 'duration')
  nx.draw_networkx_edge_labels(G, pos, edge_labels)


def  add_events_wait_activities_of_stop(G, stop, T, k, solution_events,solution_frequencies, solution_y, activities, events, stops, line_alternatives, list_of_lines):  
    events_at_stop = {}
    
    list_of_wait_activities = funktionen.get_list_of_wait_activities(activities)
    
    for event in events:
        if event[0] == stop and event in solution_events:
            events_at_stop[event]=round(solution_events[event]/k,1)
        elif event[0] == stop:
            events_at_stop[event] = events[event][1]/k
    
    list_of_choosen_events = funktionen_sol.get_choosen_events(solution_events, solution_frequencies, line_alternatives)
    for event in events_at_stop:      
        # set color and time of event
        if event in list_of_choosen_events:
            event_color = 'choosen'
        elif event[2] not in line_alternatives: 
            event_color = 'fixed_line'
        else:
            event_color = 'not_choosen'
        G.add_node(event)
        G.nodes[event]['time']=events_at_stop[event]
        G.nodes[event]['color'] = event_color
        event_line = event[2]
        event_line_richtung = event[3]
        
        # set line of event
        G.nodes[event]['event_line'] = event_line
        if event_line not in list_of_lines:
            list_of_lines.append(event_line)
        
        # set direction of event
        if event_line in stops[stop][3]['W']:
            if event_line_richtung == stops[stop][3]['W'][event_line]: 
                event_direction = 'W'
            else: 
                event_direction = 'O'
        if event_line in stops[stop][3]['N']:
             if event_line_richtung == stops[stop][3]['N'][event_line]: 
                 event_direction = 'N'
             else: 
                 event_direction = 'S'
        G.nodes[event]['direction']=event_direction         
    
    # waiting time of edges
    for activity in list_of_wait_activities:
        event_1 = activity[0]
        event_2 = activity[1]
        if event_1[0] == stop and event_2[0] == stop:
             haltezeit = round(solution_y[activity]/k,1)
             if G.nodes[event_1]['color'] == 'choosen' or G.nodes[event_1]['color'] == 'fixed_line':
                 if G.nodes[event_2]['color'] == 'choosen' or G.nodes[event_2]['color'] == 'fixed_line':
                     G.add_edge(event_1, event_2)
                     G.edges[event_1,event_2]['duration'] = haltezeit
                     G.edges[event_1, event_2]['activity_type'] = 'wait'
        
    
    
def add_position_to_nodes(G, list_of_lines, stops):
    list_of_nodes = []
    for event in G.nodes:
        list_of_nodes.append(event)
        
    for event in list_of_nodes:
        stop = event[0]
        pos_x = int(stops[stop][5])
        pos_y = int(stops[stop][6])
        event_direction = G.nodes[event]['direction']
        event_ankunft = event[1]
        event_line = event[2]
        # position of event in x-direction
        if event_ankunft == 'arr':
            if event_direction == 'W' or event_direction == 'S':
                pos_x += 0
            elif event_direction == 'O' or event_direction == 'N':
                pos_x += 1.5
        elif event_ankunft == 'dep':
            if event_direction == 'W' or event_direction == 'S':
                pos_x += 1
            elif event_direction == 'O' or event_direction == 'N':
                pos_x += 0.5
                
        # position event in y-direction
        for i in range(0, len(list_of_lines)):
            if event_line == list_of_lines[i]:
                if event_direction == 'W' or event_direction == 'S':
                     pos_y += 0.9-i/10
                elif event_direction == 'O' or event_direction == 'N':
                     pos_y += -0.9+i/10 
        G.nodes[event]['pos']= (pos_x, pos_y)    

        
        pos_x = int(stops[stop][5])
        pos_y = int(stops[stop][6])
        # label of Arr-Dep
        G.add_node((stop, 'arr',1))
        G.nodes[(stop, 'arr', 1)]['pos']=(pos_x , pos_y + 1)
        G.nodes[(stop, 'arr',1)]['arr/dep']='arr'
        G.nodes[(stop, 'arr',1)]['color']='white'
        G.add_node((stop, 'arr',2))
        G.nodes[(stop, 'arr', 2)]['pos']=(pos_x + 1.5, pos_y-1)
        G.nodes[(stop, 'arr',2)]['arr/dep']='arr'
        G.nodes[(stop, 'arr',2)]['color']='white'
        
        G.add_node((stop, 'dep',1))
        G.nodes[(stop, 'dep', 1)]['pos']=(pos_x + 1 , pos_y +1)
        G.nodes[(stop, 'dep',1)]['arr/dep']='dep'
        G.nodes[(stop, 'dep',1)]['color']='white'
        G.add_node((stop, 'dep',2))
        G.nodes[(stop, 'dep', 2)]['pos']=(pos_x +0.5 , pos_y-1)
        G.nodes[(stop, 'dep',2)]['arr/dep']='dep'
        G.nodes[(stop, 'dep',2)]['color']='white'
        
        # label name of stop
        G.add_node((stop,1))
        G.nodes[(stop,1)]['pos']=(pos_x-1, pos_y + 1)
        G.nodes[(stop,1)]['color']= 'white'
        G.nodes[(stop,1)]['stop'] = stop
        G.add_node((stop,2) )
        G.nodes[(stop,2)]['pos']=(pos_x-1, pos_y-1)
        G.nodes[(stop,2)]['color']= 'white'
        G.nodes[(stop,2)]['stop'] = stop
        
        # arrow of arr to dep
        G.add_edge((stop, 'arr', 1), (stop, 'dep', 1))
        G.edges[(stop, 'arr', 1), (stop, 'dep', 1)]['activity_type'] = 'str'
        G.add_edge((stop, 'arr', 2), (stop, 'dep', 2))
        G.edges[(stop, 'arr', 2), (stop, 'dep', 2)]['activity_type'] = 'str'
  
def add_edges_of_driving_activities(G, list_of_stops, solution_events, solution_y, activities, T, k):
    list_of_drive_activities = funktionen.get_list_of_drive_activities(activities)
    for activity in list_of_drive_activities:
        event_1 = activity[0]
        event_2 = activity[1]
        if event_1[0] in list_of_stops and event_2[0] in list_of_stops:
            fahrzeit = round(solution_y[activity]/k, 1)
            if G.nodes[event_1]['color'] == 'choosen' or G.nodes[event_1]['color'] == 'fixed_line':
                if G.nodes[event_2]['color'] == 'choosen' or G.nodes[event_2]['color'] == 'fixed_line':
                    G.add_edge(event_1, event_2)
                    G.edges[event_1,event_2]['duration']=fahrzeit
                    G.edges[event_1, event_2]['activity_type'] = 'drive'

def add_edges_of_transfer_activities(G, list_of_stops, solution_events,solution_y, events, activities, T, k):
    list_of_trans_activities = funktionen.get_list_of_trans_activities(activities)
    for activity in list_of_trans_activities:
        event_1 = activity[0]
        event_2 = activity[1]
        if event_1[0] in list_of_stops and event_2[0] in list_of_stops:
            transfer_time = round(solution_y[activity]/k, 1)
            if G.nodes[event_1]['color'] == 'choosen' or G.nodes[event_1]['color'] == 'fixed_line':
                if G.nodes[event_2]['color'] == 'choosen' or G.nodes[event_2]['color'] == 'fixed_line':
                    G.add_edge(event_1, event_2)
                    G.edges[event_1,event_2]['duration']=transfer_time
                    G.edges[event_1, event_2]['activity_type'] = 'transfer'
        
        
def add_nodes_for_line_str(G, list_of_lines):
    # nodes of labels
    # label of lines
    
    for line in list_of_lines:
        
        line_nr = line[0]
        
        for i in range(0, len(list_of_lines)):
            if line == list_of_lines[i]:
                pos_y_1 = 0.9 - i/10
                pos_y_2 = -0.9 +i/10
                
        G.add_node((line,1))
        G.add_node((line,2))
        G.nodes[(line,1)]['pos']= (- 1, pos_y_1)
        G.nodes[(line,1)]['line']= line_nr
        G.nodes[(line,1)]['color']= 'white'
        G.nodes[(line,2)]['pos']= ( -1, pos_y_2)
        G.nodes[(line,2)]['line']= line_nr
        G.nodes[(line,2)]['color']= 'white'
    
            