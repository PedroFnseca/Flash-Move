import numpy as np
import random
from collections import deque

class Courier:
    
    def __init__(self, env, cid, start_pos=(0, 0), service_speed=80.0, name=None, metrics=None, config=None):
        self.env = env
        self.id = cid
        self.name = name if name else f"Courier {cid}"
        self.pos = np.array(start_pos, dtype=float)
        self.status = "idle"
        self.current_order = None
        self.assigned_event = None
        self.total_busy_time = 0.0
        self.total_deliveries = 0
        self.trail = deque(maxlen=20)
        self.service_speed = service_speed
        self.metrics = metrics
        self.config = config
        self.had_accident = False
        self._run_proc = env.process(self.process())

    def assign(self, order):
        if self.assigned_event is None or self.assigned_event.triggered:
            self.assigned_event = self.env.event()
        self.assigned_event.succeed(value=order)

    def distance_to(self, point):
        return np.linalg.norm(self.pos - np.array(point, dtype=float))

    def process(self):
        while True:
            self.status = "idle"
            self.current_order = None
            self.assigned_event = self.env.event()
            order = yield self.assigned_event
            
            self.current_order = order
            order.assigned = self.env.now
            
            self.status = "to_pickup"
            start = self.pos.copy()
            end = np.array(order.pickup, dtype=float)
            travel_time = max(1e-6, np.linalg.norm(end - start) / self.service_speed)
            yield from self._move(start, end, travel_time)
            order.picked = self.env.now
            
            self.status = "to_dropoff"
            start = self.pos.copy()
            end = np.array(order.dropoff, dtype=float)
            travel_time = max(1e-6, np.linalg.norm(end - start) / self.service_speed)
            yield from self._move(start, end, travel_time)
            order.completed = self.env.now
            
            self.total_busy_time += (self.env.now - order.assigned)
            self.total_deliveries += 1
            
            self.status = "idle"
            self.current_order = None
            
            yield self.env.timeout(0.1)

    def _move(self, start, end, total_time, step=0.2):
        dist_vec = end - start
        remaining = total_time
        t0 = self.env.now
        
        while remaining > 1e-9:
            dt = min(step, remaining)
            elapsed = self.env.now - t0
            done_frac = elapsed / total_time if total_time > 0 else 1.0
            frac = dt / total_time if total_time > 0 else 1.0
            
            self.pos = start + dist_vec * min(1.0, done_frac + frac)
            self.trail.append(tuple(self.pos))
            
            if self.config and self.metrics and not self.had_accident:
                accident_prob = self.config.ACCIDENT_PROBABILITY * dt
                if random.random() < accident_prob:
                    self.had_accident = True
                    self.metrics['accidents'] += 1
                    print(f"\n🚨 ACIDENTE! {self.name} sofreu um acidente durante a entrega do pedido #{self.current_order.id if self.current_order else '?'}")
                    print(f"   Posição: ({int(self.pos[0])}, {int(self.pos[1])}) - Tempo: {round(self.env.now, 1)}s\n")
                    yield self.env.timeout(30)
                    self.had_accident = False
            
            yield self.env.timeout(dt)
            remaining -= dt
        
        self.pos = end.copy()
        self.trail.append(tuple(self.pos))
    
    @property
    def utilization(self):
        if self.env.now > 0:
            return self.total_busy_time / self.env.now
        return 0.0
    
    def __repr__(self):
        return f"Courier(id={self.id}, status={self.status}, deliveries={self.total_deliveries})"
