import sys
import pygame
import config

from simulation import setup_simulation
from visualization import Renderer, UIController


def main():
    env, couriers, orders_queue, all_orders, metrics = setup_simulation(config)
    
    renderer = Renderer(config)
    renderer.initialize()
    
    ui = UIController()
    
    while ui.running:
        if not ui.process_events():
            break
        
        if not ui.paused and env.now < config.SIM_TIME:
            env.run(until=env.now + config.FRAME_DT * ui.speed_mult)
        
        renderer.draw(env, couriers, orders_queue, metrics, ui.paused, ui.speed_mult)
        ui.flip_display()
        ui.tick(config.FPS) 
        
        if env.now >= config.SIM_TIME:
            if metrics['completed'] + metrics['desisted'] >= metrics['total_orders']:
                pygame.time.wait(2000)
                break
    
    renderer.cleanup()
    
    in_progress = 0
    for c in couriers:
        if c.current_order and not c.current_order.completed:
            in_progress += 1
    
    in_queue = len(orders_queue)
    
    metrics['in_progress'] = in_progress
    metrics['in_queue'] = in_queue
    
    print("Sim finished. Metrics:", metrics)
    
    print("\n=== Estatísticas Finais ===")
    print(f"Total de pedidos: {metrics['total_orders']}")
    print(f"Completados: {metrics['completed']}")
    print(f"Desistências: {metrics['desisted']}")
    print(f"Em andamento (não finalizados): {in_progress}")
    print(f"Na fila (não atribuídos): {in_queue}")
    print(f"Acidentes de moto: {metrics.get('accidents', 0)}")
    print(f"Taxa de sucesso: {round(metrics['completed']/max(1, metrics['total_orders'])*100, 1)}%")
    
    avg_delivery = metrics.get('total_delivery_time', 0) / max(1, metrics['completed'])
    print(f"Tempo médio de entrega: {round(avg_delivery, 1)}s")
    
    print("\n=== Estatísticas por Entregador ===")
    for c in couriers:
        print(f"{c.name}: {c.total_deliveries} entregas, "
              f"{round(c.utilization * 100, 1)}% utilização")
    
    sys.exit(0)


if __name__ == "__main__":
    main()