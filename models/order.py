import random
import numpy as np
class Order:
    newid = 0
    
    def __init__(self, env, pickup, dropoff, created_time):
        self.id = Order.newid
        Order.newid += 1
        self.pickup = pickup
        self.dropoff = dropoff
        self.created = created_time
        self.assigned = None
        self.picked = None
        self.completed = None
        self.base_priority = np.clip(np.random.normal(2.0, 0.8), 0.5, 3.5)
    
    @property
    def wait_time(self):
        if self.completed:
            return self.completed - self.created
        return None
    
    @property
    def delivery_time(self):
        if self.completed:
            return self.completed - self.created
        return None
    
    def __repr__(self):
        return f"Order(id={self.id}, pickup={self.pickup}, dropoff={self.dropoff})"
