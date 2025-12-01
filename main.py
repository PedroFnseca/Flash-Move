import sys
import pygame
import config
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime

from simulation import setup_simulation
from visualization import Renderer, UIController

# Usar backend que não requer interface gráfica durante a simulação
matplotlib.use('Agg')


def generate_charts(metrics, couriers, all_orders, config):
    """Gera gráficos com os dados da simulação"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Configurar estilo
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('Flash Move - Relatório da Simulação', fontsize=20, fontweight='bold', y=0.98)
    
    # 1. Gráfico de Pizza - Distribuição de Pedidos
    ax1 = plt.subplot(2, 3, 1)
    labels = ['Completados', 'Desistências', 'Em Andamento', 'Na Fila']
    sizes = [
        metrics['completed'],
        metrics['desisted'],
        metrics.get('in_progress', 0),
        metrics.get('in_queue', 0)
    ]
    colors = ['#32FF96', '#FF466E', '#64B4FF', '#FFDC64']
    explode = (0.1, 0.05, 0.05, 0.05)
    
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 10, 'weight': 'bold'})
    ax1.set_title('Distribuição de Pedidos', fontsize=12, fontweight='bold', pad=15)
    
    # 2. Gráfico de Barras - Desempenho dos Entregadores
    ax2 = plt.subplot(2, 3, 2)
    courier_names = [c.name for c in couriers]
    deliveries = [c.total_deliveries for c in couriers]
    utilization = [c.utilization * 100 for c in couriers]
    
    x = range(len(courier_names))
    width = 0.35
    
    bars1 = ax2.bar([i - width/2 for i in x], deliveries, width, label='Entregas', color='#64B4FF', edgecolor='white', linewidth=1.5)
    ax2_twin = ax2.twinx()
    bars2 = ax2_twin.bar([i + width/2 for i in x], utilization, width, label='Utilização (%)', color='#FFDC64', edgecolor='white', linewidth=1.5)
    
    ax2.set_xlabel('Entregadores', fontweight='bold')
    ax2.set_ylabel('Número de Entregas', fontweight='bold', color='#64B4FF')
    ax2_twin.set_ylabel('Utilização (%)', fontweight='bold', color='#FFDC64')
    ax2.set_title('Desempenho dos Entregadores', fontsize=12, fontweight='bold', pad=15)
    ax2.set_xticks(x)
    ax2.set_xticklabels(courier_names)
    ax2.tick_params(axis='y', labelcolor='#64B4FF')
    ax2_twin.tick_params(axis='y', labelcolor='#FFDC64')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Adicionar valores nas barras
    for bar in bars1:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=9, fontweight='bold')
    for bar in bars2:
        height = bar.get_height()
        ax2_twin.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 3. Gráfico de Métricas Gerais
    ax3 = plt.subplot(2, 3, 3)
    metrics_labels = ['Total\nPedidos', 'Completados', 'Desistências', 'Acidentes']
    metrics_values = [
        metrics['total_orders'],
        metrics['completed'],
        metrics['desisted'],
        metrics.get('accidents', 0)
    ]
    metrics_colors = ['#64B4FF', '#32FF96', '#FF466E', '#FF8C50']
    
    bars = ax3.bar(metrics_labels, metrics_values, color=metrics_colors, edgecolor='white', linewidth=1.5)
    ax3.set_title('Métricas Gerais', fontsize=12, fontweight='bold', pad=15)
    ax3.set_ylabel('Quantidade', fontweight='bold')
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 4. Histograma - Distribuição de Tempos de Entrega
    ax4 = plt.subplot(2, 3, 4)
    delivery_times = [o.delivery_time for o in all_orders if o.completed]
    
    if delivery_times:
        ax4.hist(delivery_times, bins=20, color='#32FF96', edgecolor='white', linewidth=1.2, alpha=0.8)
        ax4.axvline(sum(delivery_times)/len(delivery_times), color='#FF466E', 
                   linestyle='--', linewidth=2, label=f'Média: {sum(delivery_times)/len(delivery_times):.1f}s')
        ax4.set_xlabel('Tempo de Entrega (segundos)', fontweight='bold')
        ax4.set_ylabel('Frequência', fontweight='bold')
        ax4.set_title('Distribuição dos Tempos de Entrega', fontsize=12, fontweight='bold', pad=15)
        ax4.legend(loc='upper right', fontsize=9)
        ax4.grid(axis='y', alpha=0.3, linestyle='--')
    
    # 5. Linha do Tempo - Pedidos ao Longo do Tempo
    ax5 = plt.subplot(2, 3, 5)
    
    # Criar timeline de eventos
    time_intervals = 20
    interval_size = config.SIM_TIME / time_intervals
    completed_per_interval = [0] * time_intervals
    created_per_interval = [0] * time_intervals
    desisted_per_interval = [0] * time_intervals
    
    for order in all_orders:
        created_idx = min(int(order.created / interval_size), time_intervals - 1)
        created_per_interval[created_idx] += 1
        
        if order.completed:
            completed_idx = min(int(order.completed / interval_size), time_intervals - 1)
            completed_per_interval[completed_idx] += 1
    
    # Estimar desistências (distribuição baseada no total)
    total_desisted = metrics['desisted']
    if total_desisted > 0:
        for i in range(time_intervals):
            desisted_per_interval[i] = int(total_desisted / time_intervals)
    
    time_labels = [f'{int(i * interval_size)}' for i in range(time_intervals)]
    
    ax5.plot(time_labels, created_per_interval, marker='o', linewidth=2, 
            label='Criados', color='#64B4FF', markersize=5)
    ax5.plot(time_labels, completed_per_interval, marker='s', linewidth=2, 
            label='Completados', color='#32FF96', markersize=5)
    ax5.plot(time_labels, desisted_per_interval, marker='^', linewidth=2, 
            label='Desistências', color='#FF466E', markersize=5)
    
    ax5.set_xlabel('Tempo (segundos)', fontweight='bold')
    ax5.set_ylabel('Número de Pedidos', fontweight='bold')
    ax5.set_title('Linha do Tempo - Pedidos', fontsize=12, fontweight='bold', pad=15)
    ax5.legend(loc='upper left', fontsize=9)
    ax5.grid(True, alpha=0.3, linestyle='--')
    
    # Mostrar apenas alguns labels no eixo x
    ax5.set_xticks(range(0, time_intervals, max(1, time_intervals // 10)))
    ax5.set_xticklabels([time_labels[i] for i in range(0, time_intervals, max(1, time_intervals // 10))], rotation=45)
    
    # 6. Resumo em Texto
    ax6 = plt.subplot(2, 3, 6)
    ax6.axis('off')
    
    avg_delivery = metrics.get('total_delivery_time', 0) / max(1, metrics['completed'])
    success_rate = metrics['completed'] / max(1, metrics['total_orders']) * 100
    
    summary_text = f"""
    📊 RESUMO DA SIMULAÇÃO
    
    ⏱️  Tempo Total: {config.SIM_TIME}s
    
    📦 PEDIDOS:
       • Total: {metrics['total_orders']}
       • Completados: {metrics['completed']}
       • Desistências: {metrics['desisted']}
       • Em Andamento: {metrics.get('in_progress', 0)}
       • Na Fila: {metrics.get('in_queue', 0)}
    
    🚨 Acidentes: {metrics.get('accidents', 0)}
    
    🎯 Taxa de Sucesso: {success_rate:.1f}%
    
    ⏱️  Tempo Médio: {avg_delivery:.1f}s
    
    🚴 ENTREGADORES:
    """
    
    for c in couriers:
        summary_text += f"\n       • {c.name}: {c.total_deliveries} entregas"
        summary_text += f" ({c.utilization * 100:.1f}%)"
    
    ax6.text(0.1, 0.95, summary_text, transform=ax6.transAxes, 
            fontsize=11, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='#1a1a2e', edgecolor='#64B4FF', linewidth=2, alpha=0.9),
            color='#e0e0e0')
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    
    # Salvar gráfico
    filename = f'flash_move_report_{timestamp}.png'
    plt.savefig(filename, dpi=150, facecolor='#0f0f1e', edgecolor='none')
    print(f"\n📊 Gráficos salvos em: {filename}")
    
    # Mostrar gráficos
    plt.show()
    plt.close()


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
    
    # Gerar gráficos
    print("\n📊 Gerando gráficos...")
    generate_charts(metrics, couriers, all_orders, config)
    
    sys.exit(0)


if __name__ == "__main__":
    main()