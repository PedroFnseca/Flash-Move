import random
import numpy as np
from models import Order


def order_generator(env, orders_queue, all_orders, metrics, config):
    if config.PEAK_ENABLED:
        peak_start = random.uniform(config.SIM_TIME * 0.3, config.SIM_TIME * 0.6)
        peak_end = peak_start + config.PEAK_DURATION
        metrics['peak_start'] = peak_start
        metrics['peak_end'] = peak_end
        metrics['peak_active'] = False
    
    while env.now < config.SIM_TIME:
        in_peak = False
        if config.PEAK_ENABLED and peak_start <= env.now < peak_end:
            in_peak = True
            if not metrics['peak_active']:
                metrics['peak_active'] = True
                print(f"\n🔥 PICO DE PEDIDOS INICIADO! Tempo: {round(env.now, 1)}s")
        elif config.PEAK_ENABLED and env.now >= peak_end and metrics['peak_active']:
            metrics['peak_active'] = False
            print(f"\n✅ Pico de pedidos finalizado. Tempo: {round(env.now, 1)}s\n")
        
        if in_peak:
            inter = np.random.exponential(config.INTERARRIVAL_MEAN / config.PEAK_MULTIPLIER)
        else:
            inter = np.random.exponential(config.INTERARRIVAL_MEAN)
        
        yield env.timeout(inter)
        
        pickup = (
            random.uniform(50, config.MAP_SIZE[0] - 50),
            random.uniform(50, config.MAP_SIZE[1] - 50)
        )
        dropoff = (
            random.uniform(50, config.MAP_SIZE[0] - 50),
            random.uniform(50, config.MAP_SIZE[1] - 50)
        )
        
        o = Order(env, pickup, dropoff, env.now)
        orders_queue.append(o)
        all_orders.append(o)
        metrics['total_orders'] += 1


def dispatcher(env, orders_queue, couriers, metrics, config):
    while env.now < config.SIM_TIME:
        _handle_order_abandonment(env, orders_queue, metrics, config)
        assigned_any = _assign_orders(orders_queue, couriers, metrics, env)
        
        if not assigned_any:
            yield env.timeout(0.5)
        else:
            yield env.timeout(0.01)


def _handle_order_abandonment(env, orders_queue, metrics, config):
    for o in list(orders_queue):
        wait_time = env.now - o.created
        if len(orders_queue) > config.MAX_QUEUE_FORGIVE and wait_time > 0:
            p_give = min(
                0.99,
                0.12 * (len(orders_queue) - config.MAX_QUEUE_FORGIVE) + 0.008 * wait_time
            )
            if random.random() < p_give:
                orders_queue.remove(o)
                metrics['desisted'] += 1
                
                if wait_time > 300:
                    reason = "Tempo de espera muito longo"
                elif len(orders_queue) > 40:
                    reason = "Fila muito grande"
                else:
                    reason = "Cliente desistiu"
                
                print(f"Pedido #{o.id} desistiu - Motivo: {reason} (Espera: {round(wait_time, 1)}s, Fila: {len(orders_queue)+1})")


def _assign_orders(orders_queue, couriers, metrics, env):
    assigned_any = False
    
    while orders_queue:
        free = [c for c in couriers if c.status == "idle"]
        if not free:
            break
        
        best_score = float('inf')
        best_courier = None
        best_order = None
        
        for order in list(orders_queue):
            wait_time = env.now - order.created
            base_priority = getattr(order, 'base_priority', 2.0)
            
            for courier in free:
                dist = courier.distance_to(order.pickup)
                priority_bonus = -(base_priority - 2.0) * 30.0
                score = dist + wait_time * 5.0 + priority_bonus
                
                if score < best_score:
                    best_score = score
                    best_courier = courier
                    best_order = order
        
        if best_order and best_courier:
            orders_queue.remove(best_order)
            best_courier.assign(best_order)
            metrics['assigned'] += 1
            assigned_any = True
            free.remove(best_courier)
        else:
            break
    
    return assigned_any


def monitor_completions(env, metrics, all_orders, config):
    if 'total_delivery_time' not in metrics:
        metrics['total_delivery_time'] = 0.0
    if 'accidents' not in metrics:
        metrics['accidents'] = 0
    
    while env.now < config.SIM_TIME:
        for o in list(all_orders):
            if o.completed and not getattr(o, "_counted", False):
                metrics['completed'] += 1
                delivery_time = o.completed - o.created
                metrics['total_delivery_time'] += delivery_time
                setattr(o, "_counted", True)
        
        yield env.timeout(0.5)
