# 🚀 Flash Move

Sistema de simulação de delivery em tempo real com visualização moderna e arquitetura modular.

## 📋 Descrição

Flash Move é um simulador de sistema de entregas que utiliza SimPy para modelagem de eventos discretos e Pygame para visualização gráfica avançada. O projeto apresenta tema neon/cyberpunk com efeitos visuais modernos incluindo partículas, sombras, brilhos e animações fluidas.

## ✨ Características

### Simulação
- Sistema de eventos discretos com SimPy
- 4 couriers autônomos com movimentação suave
- Geração dinâmica de pedidos
- Sistema inteligente de despacho e atribuição
- Limite de tempo de espera (30s) com desistências
- Métricas em tempo real

### Visual
- Tema neon/cyberpunk com paleta de cores vibrante
- Taxa de atualização: 60 FPS
- Sistema de partículas para couriers em movimento
- Efeitos de brilho (glow) e sombras
- Animações de pulso em pedidos pendentes
- Linhas animadas conectando couriers a destinos
- Trilhas (trails) com efeito de fade
- Painéis arredondados com bordas accent
- Barra de progresso de sucesso
- Grid modernizado com níveis de profundidade

### Controles Interativos
- **ESPAÇO**: Pausar/continuar simulação
- **+/-**: Aumentar/diminuir velocidade (0.5x a 5x)
- **ESC**: Sair

## 📁 Estrutura do Projeto

```
Flash-Move/
├── config.py                   # Configurações centralizadas
├── main.py                     # Entry point da aplicação
├── requirements.txt            # Dependências Python
│
├── models/                     # Entidades do domínio
│   ├── __init__.py
│   ├── order.py               # Modelo de pedido
│   └── courier.py             # Modelo de courier
│
├── simulation/                 # Lógica de simulação
│   ├── __init__.py
│   ├── environment.py         # Setup do ambiente SimPy
│   └── processes.py           # Geradores de processos
│
└── visualization/              # Renderização e UI
    ├── __init__.py
    ├── renderer.py            # Sistema de renderização
    └── ui.py                  # Controles e eventos
```

## 🎨 Paleta de Cores

O projeto utiliza uma paleta neon/cyberpunk:
- **Background**: RGB(25, 28, 35) - Escuro profundo
- **Accent**: RGB(70, 150, 255) - Azul neon
- **Success**: RGB(0, 255, 170) - Verde neon
- **Warning**: RGB(255, 200, 50) - Amarelo vibrante
- **Danger**: RGB(255, 50, 100) - Rosa neon

## 🔧 Configurações

Parâmetros principais em `config.py`:
- **SIM_TIME**: 3600s (1 hora de simulação)
- **MAP_SIZE**: 1400x900 pixels
- **NUM_COURIERS**: 4
- **COURIER_SPEED**: 100 unidades/s
- **ORDER_INTERVAL**: 10s (média entre pedidos)
- **MAX_WAIT_TIME**: 30s (antes de desistência)
- **FPS**: 60

## 🚀 Instalação

### Requisitos
- Python 3.13+
- pip

### Dependências

```bash
pip install -r requirements.txt
```

Pacotes principais:
- **simpy**: 4.0+ (simulação de eventos discretos)
- **pygame**: 2.5+ (renderização gráfica)
- **numpy**: 1.24+ (cálculos matemáticos)

## ▶️ Execução

```bash
python main.py
```

## 📊 Métricas Exibidas

### Painel Principal
- Tempo de simulação
- Velocidade de execução
- Pedidos pendentes, totais, atribuídos, completados e desistências
- Taxa de sucesso com barra visual
- Tempo médio de entrega
- Taxa de utilização dos couriers

### Painel de Couriers
- Status atual (Ocioso/Coleta/Entrega)
- Total de entregas realizadas
- Cor identificadora única

## 🎯 Funcionalidades Técnicas

### Models
**Order**: Representa um pedido com origem, destino e métricas de tempo
**Courier**: Entidade autônoma com:
- Sistema de movimentação suave (interpolação)
- Rastro de posições (trail)
- Máquina de estados (idle/to_pickup/to_dropoff)
- Contabilização de tempo ocupado e entregas

### Simulation
**Environment**: Configura o ambiente SimPy com filas e métricas
**Processes**: 
- `order_generator()`: Cria pedidos aleatórios
- `dispatcher()`: Atribui pedidos a couriers disponíveis
- `monitor_wait_times()`: Remove pedidos com timeout

### Visualization
**Renderer**: Sistema completo de renderização com:
- Background com gradiente
- Grid em duas camadas
- Partículas dinâmicas
- Efeitos visuais avançados (glow, sombras, pulsos)
- Painéis informativos modernos

**UIController**: Gerenciamento de:
- Eventos de teclado
- Estados de pausa/velocidade
- Clock de framerate

## 🧩 Arquitetura

O projeto segue princípios de:
- **Separação de responsabilidades**: Models, Simulation, Visualization
- **Configuração centralizada**: Todos os parâmetros em `config.py`
- **Modularidade**: Cada módulo tem responsabilidade única
- **Código limpo**: Sem comentários, código autoexplicativo

## 📈 Exemplo de Saída

Ao finalizar a simulação, são exibidas estatísticas:

```
=== Estatísticas Finais ===
Total de pedidos: 360
Completados: 312
Desistências: 48
Taxa de sucesso: 86.7%
Tempo médio de entrega: 45.3s

=== Estatísticas por Courier ===
Courier 0: 78 entregas, 87.2% utilização
Courier 1: 82 entregas, 89.1% utilização
Courier 2: 76 entregas, 85.5% utilização
Courier 3: 76 entregas, 84.8% utilização
```

## 🔄 Extensões Possíveis

- Adicionar diferentes tipos de couriers (bicicleta, moto, carro)
- Implementar zonas de prioridade no mapa
- Sistema de recompensas/penalidades
- Exportação de dados para análise
- Machine learning para otimização de rotas
- Múltiplas estratégias de despacho

## 📝 Licença

Projeto educacional - Flash Move Delivery Simulator

## 👨‍💻 Desenvolvimento

Desenvolvido com foco em:
- Performance (60 FPS estável)
- Visual moderno e atrativo
- Código limpo e manutenível
- Arquitetura escalável