import simpy
import random
import numpy as np
from collections import deque
from models import Courier
from .processes import order_generator, dispatcher, monitor_completions


def setup_simulation(config):
    random.seed(config.SEED)
    np.random.seed(config.SEED)
    
    env = simpy.Environment()
    
    orders_queue = deque()
    all_orders = []
    metrics = {
        'total_orders': 0,
        'assigned': 0,
        'completed': 0,
        'desisted': 0,
        'total_delivery_time': 0.0
    }
    
    couriers = []
    for i in range(config.NUM_COURIERS):
        start = (
            config.MAP_SIZE[0] // 2 + random.uniform(-50, 50),
            config.MAP_SIZE[1] // 2 + random.uniform(-50, 50)
        )
        c = Courier(env, i, start_pos=start, service_speed=config.SERVICE_SPEED)
        couriers.append(c)
    
    env.process(order_generator(env, orders_queue, all_orders, metrics, config))
    env.process(dispatcher(env, orders_queue, couriers, metrics, config))
    env.process(monitor_completions(env, metrics, all_orders, config))
    
    return env, couriers, orders_queue, all_orders, metrics
