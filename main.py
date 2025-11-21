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
    print("Sim finished. Metrics:", metrics)
    
    print("\n=== Estatísticas Finais ===")
    print(f"Total de pedidos: {metrics['total_orders']}")
    print(f"Completados: {metrics['completed']}")
    print(f"Desistências: {metrics['desisted']}")
    print(f"Taxa de sucesso: {round(metrics['completed']/max(1, metrics['total_orders'])*100, 1)}%")
    
    avg_delivery = metrics.get('total_delivery_time', 0) / max(1, metrics['completed'])
    print(f"Tempo médio de entrega: {round(avg_delivery, 1)}s")
    
    print("\n=== Estatísticas por Courier ===")
    for c in couriers:
        print(f"Courier {c.id}: {c.total_deliveries} entregas, "
              f"{round(c.utilization * 100, 1)}% utilização")
    
    sys.exit(0)


if __name__ == "__main__":
    main()