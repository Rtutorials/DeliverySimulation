
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from IPython.display import clear_output
import random
from itertools import combinations
from utils import get_shortest_distance, get_unit_step


class Simulation:
    def __init__(self, city_graph, node_coords_G, restaurants, customers, drivers, r_node_map, c_node_map, d_node_map, speed, handover_driver_threshold, handover_customer_threshold):
        
        self.clock = 0
        self.graph = city_graph # Networkx graph
        self.node_coords_G = node_coords_G
        self.restaurants = restaurants # Dict of restaurant classes
        self.customers = customers # Dict of destination
        self.drivers = drivers # Dict of drivers
        self.r_node_map = r_node_map
        self.c_node_map = c_node_map
        self.d_node_map = d_node_map

        self.orders = {}
        self.orders_completed = 0
        self.r_coords = np.array([restaurant.coords for restaurant in restaurants.values()])
        self.total_in_queue = []
        self.speed = speed

        self.handoff_distance_threshold = 1
        self.handoff_destination_distance_threshold = 1
        self.handoffs = 0
        self.handover_driver_threshold = handover_driver_threshold
        self.handover_customer_threshold = handover_customer_threshold

    def update_driver_location(self):
        # Run at the end of each step
        self.d_prev_node_ids = np.array([self.drivers[d_id].prev_node_id for d_id in self.drivers.keys()])

    def view(self):
        fig, ax = plt.subplots(figsize=(10, 10))
        
        nx.draw(self.graph, pos=nx.get_node_attributes(self.graph, 'coords'), width=0.2, node_color="black", node_size=1, ax=ax)

        # Add restaurants to the plot
        restaurant_scatter = ax.scatter([], [], color="lime", s=30, zorder=9, label='Restaurant')
        driver_scatter = ax.scatter([], [], color="red", s=30, zorder=10, label='Driver')
        customer_scatter = ax.scatter([], [], color="gold", s=30, zorder=8, label='Customer')
        legend1 = ax.legend(handles=[restaurant_scatter, driver_scatter, customer_scatter], loc='upper right', title='Locations', markerscale=2)
        ax.add_artist(legend1)

        # Add clock and orders completed to the plot
        text = 'Clock: {}\nOrders Completed: {}'.format(self.clock, self.orders_completed)
        ax.text(0.02, 0.98, text, transform=ax.transAxes, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))

        # Update scatter plot data
        restaurant_scatter.set_offsets(np.array([restaurant.coords for restaurant in self.restaurants.values()]))
        driver_scatter.set_offsets(np.array([driver.coords for driver in self.drivers.values()]))
        customer_scatter.set_offsets(np.array([customer.coords for customer in self.customers.values()]))

        # Refresh plot
        clear_output(wait=True)
        plt.show()
    
    def check_all_handoffs(self, time):

        drivers = self.drivers
        handover_driver_threshold = self.handover_driver_threshold
        handover_customer_threshold = self.handover_customer_threshold

        driver_pairs = combinations(drivers.keys(), 2)

        for driver_pair in driver_pairs:

            driver_A = drivers[driver_pair[0]]; driver_B = drivers[driver_pair[1]]

            # First check that both drivers are headed to a customer
            if ((driver_A.current_destination == 'C') & (driver_B.current_destination == 'C')):

                
                if ((len(driver_A.pending_orders) == 0) & (len(driver_B.pending_orders) == 0)):
                    # Then calculate distances & ensure that these are under the threshold to trigger a handoff
                    try:
                        driver_distance = get_shortest_distance(self, driver_A.current_shortest_path[0], driver_B.current_shortest_path[0])
                        customer_distance = get_shortest_distance(self, driver_A.current_shortest_path[-1], driver_B.current_shortest_path[-1])

                        if ((driver_distance <= handover_driver_threshold) & (customer_distance <= handover_customer_threshold)):

                            # Finally, check that these are not currently locked in handover
                            if not driver_A.picking_up and not driver_B.picking_up:

                                # Handoff from A --> B
                                self.handoff(driver_pair, driver_distance, time)
                    except IndexError:
                        pass
    
    def handoff(self, driver_pair, driver_distance, time):

        drivers = self.drivers; speed = self.speed

        driver_A = drivers[driver_pair[0]]; driver_B = drivers[driver_pair[1]]

        # Swap orders 
        order_to_transfer = driver_A.carrying_orders.pop(driver_A.t_id)
        driver_B.carrying_orders.append(order_to_transfer)

        # Update order properties
        self.orders[order_to_transfer].driver_id = driver_pair[1]
        self.orders[order_to_transfer].handoff = True

        # Update targets
        driver_A.update_target(self); driver_B.update_target(self)
        driver_A.picking_up = True; driver_B.picking_up = True

        # Block the movement of these drivers during handover period
        handoff_duration = np.ceil(driver_distance/speed)
        release_time = time + handoff_duration
        driver_A.pickup_release = driver_B.pickup_release = release_time

        # Finally tell the simulator a handover has taken place!
        self.handoffs += 1
        print ('Driver {0} has handed order to Driver {1}'.format(driver_pair[0], driver_pair[1]))
