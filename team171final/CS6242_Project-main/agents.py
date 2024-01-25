import numpy as np
import networkx as nx
from utils import get_shortest_distance, get_unit_step

class Order:
    def __init__(self, order_id, time, r_id, c_id):
        # Basic properties
        self.order_id = order_id
        self.restaurant_id = r_id
        self.customer_id = c_id
        
        # Time tracking
        self.driver_id = None
        self.order_time = time
        self.pickup_time = None
        self.delivery_time = None

        # Other
        self.coords = None # optional? track driver instead?
        self.distance_traveled = 0
        self.picked_up = False
        self.delivered = False
        self.handoff = False

class Customer:
    def __init__(self, c_id, c_coords):
        self.customer_id = c_id
        self.coords = c_coords
        self.order_ids = []

class Restaurant:
    def __init__(self, r_id, r_coords):
        self.restaurant_id = r_id
        self.coords = r_coords
        self.order_ids = []
        self.order_queue = []
        
    def allocate_to_driver(self, order_id, sim):

        # Retrieve all driver current coordinates
        r_id = self.restaurant_id
        r_node_map = sim.r_node_map
        r_node_id = r_node_map[r_id]
        d_node_ids = sim.d_prev_node_ids

        # Allocate to closest driver provided there is capacity
        acceptation = False
        
        distances = [get_shortest_distance(sim, r_node_id, d_node_id) for d_node_id in d_node_ids]
        distances = np.array(distances)
        
        sorted_d_ids = np.argsort(distances)
        
        # Loop through the drivers from closest to furthest
        i = 0
        while not acceptation:
            if i < len(distances) - 1:
                d_id = sorted_d_ids[i]
                acceptation = sim.drivers[d_id].accept(order_id, sim)
                # Remove from queue now that it's served
                if acceptation:
                    self.order_queue.pop(0)
            else:
                # Do nothing (i.e. leave in the queue)
                acceptation = True
            i += 1

class Driver:
    def __init__(self, d_id, d_coord, d_node_map, max_order_limit, speed):
        self.driver_id = d_id
        self.speed = speed
        self.max_order_limit = max_order_limit
        self.picking_up = False
        self.pending_orders = [] 
        self.carrying_orders = [] 
        self.completed_orders = []
        self.t_id = None #index to know which order is being addressed

        self.prev_node_id = d_node_map[d_id]
        self.next_node_id = None
        
        self.orig_coord = d_coord
        self.coords = d_coord
        self.next_node_coord = None
        self.current_shortest_path = None
        self.current_destination = None
        self.picking_up = False
        self.pickup_release = 0

    def accept(self, order_id, sim):
        
        acceptation = False
        # Only accept order if there is space
        if (len(self.pending_orders)+len(self.carrying_orders) < self.max_order_limit):
            self.pending_orders.append(order_id)
            sim.orders[order_id].driver_id = self.driver_id
            acceptation = True
        
        return acceptation
        
    def update_target(self, sim):
        
        t_ids = []; target_node_ids = []
        r_node_map = sim.r_node_map; c_node_map = sim.c_node_map; d_node_map = sim.d_node_map

        # First check if there are any pending orders to pickup - these have priority
        if len(self.pending_orders) > 0:
            for order_id in self.pending_orders:

                t_id = sim.orders[order_id].restaurant_id
                t_ids.append(t_id)
                
                target_node_ids.append(r_node_map[t_id])
            
            self.current_destination = 'R'
            
        # If none, set path towards next customer
        elif len(self.carrying_orders) > 0:
            for order_id in self.carrying_orders:

                t_id = sim.orders[order_id].customer_id
                t_ids.append(t_id)
                
                target_node_ids.append(c_node_map[t_id])
                
            self.current_destination = 'C'
                
        # Else return to original location
        else:
            t_id = self.driver_id
            t_ids.append(t_id)
            target_node_ids.append(d_node_map[t_id])
            
            self.current_destination = 'D'
        
        # Get closest destination & head there
        distances = []
        for target_node_id in target_node_ids:
            distances.append(get_shortest_distance(sim, self.prev_node_id, target_node_id))
        distances = np.array(distances)
        
        closest_order_idx = np.argmin(distances)
        target_id = t_ids[closest_order_idx]
        
        # Get the corresponding node_id in the chart
        if self.current_destination == 'R':
            target_node_id = r_node_map[target_id]
        elif self.current_destination == 'C':
            target_node_id = c_node_map[target_id]
        else:
            target_node_id = d_node_map[target_id]   # Stick to initialized position         

        # Update path to next destination - make sure to truncate shortest path each time
        shortest_path = nx.shortest_path(sim.graph, source = self.prev_node_id, target = target_node_id)[1:]
        
        next_node_id = self.next_node_id
        if len(shortest_path) > 0:
            next_node_id = shortest_path[0]
        elif ((len(shortest_path)==0) & (self.current_destination == 'D')):
            next_node_id = d_node_map[self.driver_id]   # Stick to initialize position  
        
        self.next_node_id = next_node_id
        self.next_node_coord = np.array(sim.graph.nodes[next_node_id]['coords'])
        self.current_shortest_path = shortest_path
        
        # Make sure the driver remembers which order he is handling
        self.t_id = closest_order_idx
        if self.current_destination == 'R':
            self.current_order_to_handle = self.pending_orders[closest_order_idx]
        elif self.current_destination == 'C':
            self.current_order_to_handle = self.carrying_orders[closest_order_idx]
        
    def step(self, sim, time):
        unit_step = get_unit_step(self.coords, self.next_node_coord, self.speed)
        distance_to_next_junction = np.sqrt(np.power((self.coords - self.next_node_coord), 2).sum())
        
        if distance_to_next_junction > self.speed:
            # Stay along edge
            self.coords += unit_step
            
        else:
            # Stop at next node - make sure to truncate shortest path each time
            self.coords = self.next_node_coord
            self.prev_node_id = self.next_node_id
            shortest_path = self.current_shortest_path[1:]
            
            # If not arrived at current target
            if len(shortest_path) > 0:
                next_node_id = shortest_path[0]
                self.next_node_id = next_node_id
                self.next_node_coord = np.array(sim.graph.nodes[next_node_id]['coords']) 
                self.current_shortest_path = shortest_path
                
            # Pickup or deliver
            else:
                if self.current_destination == 'R':
                    # Transfer order from pending to carrying
                    order_to_transfer = self.pending_orders.pop(self.t_id)
                    self.carrying_orders.append(order_to_transfer)
                    # Record pickup time
                    sim.orders[order_to_transfer].pickup_time = time
                    sim.orders[order_to_transfer].picked_up = True
                    
                    print ('Driver {0} has picked up order {1} from node {2}'.format(self.driver_id, order_to_transfer, self.prev_node_id))
                    
                elif self.current_destination == 'C':
                    order_to_transfer = self.carrying_orders.pop(self.t_id)
                    # Record delivery time
                    sim.orders[order_to_transfer].delivery_time = time
                    sim.orders[order_to_transfer].delivered = True
                    sim.orders_completed += 1
                    print ('Driver {0} has delivered order {1}'.format(self.driver_id, order_to_transfer))
                    