import pygame
import math
import random
import os


class Renderer:
    
    def __init__(self, config):
        self.config = config
        self.screen = None
        self.font = None
        self.small_font = None
        self.title_font = None
        self.bg_image = None
        self.time = 0
        self.particles = []
        self.courier_images = []
        
    def initialize(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.config.MAP_SIZE)
        pygame.display.set_caption("🚀 Flash Move - Simulação de Delivery")
        
        try:
            self.title_font = pygame.font.SysFont("Segoe UI", 18, bold=True)
            self.font = pygame.font.SysFont("Segoe UI", 13)
            self.small_font = pygame.font.SysFont("Segoe UI", 11)
        except:
            self.title_font = pygame.font.SysFont("Arial", 18, bold=True)
            self.font = pygame.font.SysFont("Arial", 13)
            self.small_font = pygame.font.SysFont("Arial", 11)
        
        if self.config.BACKGROUND_IMAGE:
            try:
                self.bg_image = pygame.image.load(self.config.BACKGROUND_IMAGE)
                self.bg_image = pygame.transform.scale(self.bg_image, self.config.MAP_SIZE)
            except Exception:
                self.bg_image = None
        
        self._load_courier_images()
    
    def draw(self, env, couriers, orders_queue, metrics, paused=False, speed_mult=1.0):
        self.time += 0.1
        
        self._draw_background()
        
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        
        self._draw_grid()
        self._update_particles(couriers)
        self._draw_particles()
        self._draw_orders(orders_queue, env)
        self._draw_courier_trails(couriers)
        self._draw_couriers(couriers, env)
        self._draw_connections(couriers)
        self._draw_header()
        self._draw_metrics_panel(env, orders_queue, metrics, couriers, paused, speed_mult)
        self._draw_courier_status_panel(couriers)
    
    def _draw_background(self):
        for y in range(0, self.config.MAP_SIZE[1], 10):
            factor = y / self.config.MAP_SIZE[1]
            color = tuple(int(c + (self.config.COLORS['background_light'][i] - c) * factor * 0.3) 
                         for i, c in enumerate(self.config.COLORS['background']))
            pygame.draw.rect(self.screen, color, (0, y, self.config.MAP_SIZE[0], 10))
    
    def _draw_grid(self):
        for i in range(0, self.config.MAP_SIZE[0], 50):
            pygame.draw.line(self.screen, self.config.COLORS['grid'], 
                           (i, 0), (i, self.config.MAP_SIZE[1]), 1)
        for i in range(0, self.config.MAP_SIZE[1], 50):
            pygame.draw.line(self.screen, self.config.COLORS['grid'], 
                           (0, i), (self.config.MAP_SIZE[0], i), 1)
        
        for i in range(0, self.config.MAP_SIZE[0], 100):
            pygame.draw.line(self.screen, self.config.COLORS['grid_major'], 
                           (i, 0), (i, self.config.MAP_SIZE[1]), 1)
        for i in range(0, self.config.MAP_SIZE[1], 100):
            pygame.draw.line(self.screen, self.config.COLORS['grid_major'], 
                           (0, i), (self.config.MAP_SIZE[0], i), 1)
    
    def _draw_header(self):
        header_height = 60
        header_rect = pygame.Rect(0, 0, self.config.MAP_SIZE[0], header_height)
        
        header_surf = pygame.Surface((self.config.MAP_SIZE[0], header_height), pygame.SRCALPHA)
        pygame.draw.rect(header_surf, (*self.config.COLORS['background'], 200), (0, 0, self.config.MAP_SIZE[0], header_height))
        self.screen.blit(header_surf, (0, 0))
        
        pygame.draw.line(self.screen, self.config.COLORS['accent'], 
                        (0, header_height), (self.config.MAP_SIZE[0], header_height), 2)
        
        title = self.title_font.render("🚀 FLASH MOVE", True, self.config.COLORS['accent'])
        self.screen.blit(title, (20, 15))
        
        subtitle = self.small_font.render("Simulação de Sistema de Delivery", True, self.config.COLORS['text_dim'])
        self.screen.blit(subtitle, (22, 38))
    
    def _draw_orders(self, orders_queue, env):
        for o in list(orders_queue):
            px, py = int(o.pickup[0]), int(o.pickup[1])
            dx, dy = int(o.dropoff[0]), int(o.dropoff[1])
            wait_time = env.now - o.created
            
            if wait_time < self.config.ORDER_COLOR_THRESHOLDS['new']:
                color = self.config.COLORS['order_new']
            elif wait_time < self.config.ORDER_COLOR_THRESHOLDS['waiting']:
                color = self.config.COLORS['order_waiting']
            else:
                color = self.config.COLORS['order_urgent']
            
            self._draw_dashed_line((px, py), (dx, dy), color, dash_length=8)
            
            if self.config.SHOW_SHADOWS:
                pygame.draw.circle(self.screen, (0, 0, 0, 50), (dx + 2, dy + 2), 7)
            pygame.draw.circle(self.screen, color, (dx, dy), 6, 2)
            
            if self.config.SHOW_SHADOWS:
                pygame.draw.circle(self.screen, (0, 0, 0, 50), (px + 2, py + 2), 10)
            
            pulse = math.sin(self.time * 3 + o.id) * 2 + 8
            glow_surf = pygame.Surface((int(pulse * 3), int(pulse * 3)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, 30), (int(pulse * 1.5), int(pulse * 1.5)), int(pulse * 1.5))
            self.screen.blit(glow_surf, (px - int(pulse * 1.5), py - int(pulse * 1.5)))
            
            pygame.draw.circle(self.screen, color, (px, py), 8)
            pygame.draw.circle(self.screen, self.config.COLORS['background'], (px, py), 8, 2)
            
            label_text = f"#{o.id}"
            label = self.small_font.render(label_text, True, self.config.COLORS['text'])
            label_rect = label.get_rect()
            label_rect.topleft = (px + 12, py - 8)
            
            bg_rect = label_rect.inflate(8, 4)
            self._draw_rounded_rect(self.screen, bg_rect, (*color, 180), 6)
            self.screen.blit(label, label_rect)
    
    def _draw_courier_trails(self, couriers):
        if not self.config.SHOW_TRAILS:
            return
        
        for c in couriers:
            if len(c.trail) > 1:
                trail_color = self._get_courier_color(c.id)
                for i in range(len(c.trail) - 1):
                    alpha = int(self.config.COLORS['trail_alpha'] * (i / len(c.trail)))
                    color_with_alpha = (*trail_color, alpha)
                    
                    trail_surf = pygame.Surface((self.config.MAP_SIZE[0], self.config.MAP_SIZE[1]), pygame.SRCALPHA)
                    thickness = max(1, int(3 * (i / len(c.trail))))
                    pygame.draw.line(trail_surf, color_with_alpha, c.trail[i], c.trail[i + 1], thickness)
                    self.screen.blit(trail_surf, (0, 0))
    
    def _draw_couriers(self, couriers, env):
        for c in couriers:
            x, y = int(c.pos[0]), int(c.pos[1])
            
            if c.status == "idle":
                color = self.config.COLORS['courier_idle']
            elif c.status == "to_pickup":
                color = self.config.COLORS['courier_to_pickup']
            else:
                color = self.config.COLORS['courier_to_dropoff']
            
            if c.id < len(self.courier_images):
                courier_img = self.courier_images[c.id]
            else:
                courier_img = pygame.Surface((64, 64), pygame.SRCALPHA)
                pygame.draw.circle(courier_img, color, (32, 32), 32)
            
            img_size = courier_img.get_size()
            img_rect = courier_img.get_rect(center=(x, y))
            
            if self.config.SHOW_SHADOWS:
                shadow_surf = pygame.Surface((img_size[0] + 10, img_size[1] + 10), pygame.SRCALPHA)
                pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), 
                                  (5, 7, img_size[0], img_size[1]))
                self.screen.blit(shadow_surf, (x - img_size[0] // 2 - 5, y - img_size[1] // 2 - 5))
            
            if c.status != "idle":
                pulse = abs(math.sin(self.time * 4)) * 5
                glow_size = int(img_size[0] // 2 + pulse)
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, 40), (glow_size, glow_size), glow_size)
                self.screen.blit(glow_surf, (x - glow_size, y - glow_size))
            
            self.screen.blit(courier_img, img_rect)
            
            status_colors = {
                "idle": self.config.COLORS['success'],
                "to_pickup": self.config.COLORS['accent'],
                "to_dropoff": self.config.COLORS['warning']
            }
            status_color = status_colors.get(c.status, color)
            status_pos = (x + img_size[0] // 2 - 8, y - img_size[1] // 2 + 8)
            pygame.draw.circle(self.screen, status_color, status_pos, 5)
            pygame.draw.circle(self.screen, self.config.COLORS['background'], status_pos, 5, 1)
    
    def _draw_connections(self, couriers):
        for c in couriers:
            if c.current_order:
                x, y = int(c.pos[0]), int(c.pos[1])
                target = c.current_order.pickup if c.status == "to_pickup" else c.current_order.dropoff
                tx, ty = int(target[0]), int(target[1])
                
                color = self.config.COLORS['courier_to_pickup'] if c.status == "to_pickup" else self.config.COLORS['courier_to_dropoff']
                
                self._draw_animated_line((x, y), (tx, ty), color)
                
                mid_x = (x + tx) / 2
                mid_y = (y + ty) / 2
                
                order_text = f"#{c.current_order.id}"
                order_label = self.small_font.render(order_text, True, self.config.COLORS['text'])
                order_rect = order_label.get_rect(center=(int(mid_x), int(mid_y)))
                
                bg_rect = order_rect.inflate(10, 6)
                self._draw_rounded_rect(self.screen, bg_rect, (*color, 200), 8)
                pygame.draw.rect(self.screen, color, bg_rect, 1, border_radius=8)
                
                self.screen.blit(order_label, order_rect)
    
    def _update_particles(self, couriers):
        if not self.config.SHOW_PARTICLES:
            return
        
        for c in couriers:
            if c.status != "idle" and random.random() < 0.3:
                color = self._get_courier_color(c.id)
                particle = {
                    'pos': list(c.pos),
                    'vel': [random.uniform(-1, 1), random.uniform(-1, 1)],
                    'life': 30,
                    'color': color
                }
                self.particles.append(particle)
        
        for p in self.particles[:]:
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
    
    def _draw_particles(self):
        for p in self.particles:
            alpha = int((p['life'] / 30) * 100)
            size = max(1, int((p['life'] / 30) * 4))
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*p['color'], alpha), (size, size), size)
            self.screen.blit(particle_surf, (int(p['pos'][0]) - size, int(p['pos'][1]) - size))
    
    def _draw_metrics_panel(self, env, orders_queue, metrics, couriers, paused, speed_mult):
        panel_width = 380
        panel_height = 320
        panel_x = 20
        panel_y = 80
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, self.config.COLORS['panel_bg'], (0, 0, panel_width, panel_height), border_radius=15)
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        pygame.draw.rect(self.screen, self.config.COLORS['panel_border'], panel_rect, 2, border_radius=15)
        
        completed = metrics['completed']
        total = metrics['total_orders']
        avg_delivery_time = metrics.get('total_delivery_time', 0) / max(1, completed)
        utilization = sum(c.total_busy_time for c in couriers) / (env.now * len(couriers)) * 100 if env.now > 0 else 0
        
        title = self.title_font.render("📊 Métricas", True, self.config.COLORS['accent'])
        self.screen.blit(title, (panel_x + 20, panel_y + 15))
        
        y_offset = panel_y + 50
        line_height = 18
        
        status_icon = "⏸️" if paused else "▶️"
        status_text = f"{status_icon} Tempo: {round(env.now, 1)} / {self.config.SIM_TIME}s"
        self._draw_metric_line(status_text, panel_x + 20, y_offset, self.config.COLORS['text'])
        y_offset += line_height
        
        speed_text = f"⚡ Velocidade: {round(speed_mult, 1)}x"
        self._draw_metric_line(speed_text, panel_x + 20, y_offset, self.config.COLORS['text_dim'])
        y_offset += line_height + 10
        
        metrics_data = [
            ("📦 Pendentes", len(orders_queue), self.config.COLORS['warning']),
            ("📊 Total", total, self.config.COLORS['text']),
            ("✅ Atribuídos", metrics['assigned'], self.config.COLORS['accent']),
            ("✓  Completados", completed, self.config.COLORS['success']),
            ("❌ Desistências", metrics['desisted'], self.config.COLORS['danger']),
        ]
        
        for label, value, color in metrics_data:
            text = f"{label}: {value}"
            self._draw_metric_line(text, panel_x + 20, y_offset, color)
            y_offset += line_height
        
        y_offset += 10
        
        success_rate = completed / max(1, total) * 100
        self._draw_metric_line(f"📈 Taxa de Sucesso: {round(success_rate, 1)}%", 
                               panel_x + 20, y_offset, self.config.COLORS['text'])
        y_offset += line_height
        
        bar_x = panel_x + 20
        bar_y = y_offset
        bar_width = panel_width - 40
        bar_height = 8
        
        pygame.draw.rect(self.screen, self.config.COLORS['background_light'], 
                        (bar_x, bar_y, bar_width, bar_height), border_radius=4)
        
        fill_width = int(bar_width * success_rate / 100)
        if fill_width > 0:
            pygame.draw.rect(self.screen, self.config.COLORS['success'], 
                            (bar_x, bar_y, fill_width, bar_height), border_radius=4)
        
        y_offset += line_height + 5
        
        self._draw_metric_line(f"⏱️  Tempo Médio: {round(avg_delivery_time, 1)}s", 
                               panel_x + 20, y_offset, self.config.COLORS['text'])
        y_offset += line_height
        
        self._draw_metric_line(f"📊 Utilização: {round(utilization, 1)}%", 
                               panel_x + 20, y_offset, self.config.COLORS['text'])
        y_offset += line_height + 15
        
        controls_title = self.font.render("🎮 Controles", True, self.config.COLORS['text_dim'])
        self.screen.blit(controls_title, (panel_x + 20, y_offset))
        y_offset += line_height + 5
        
        controls = [
            "ESPAÇO: Pausar/Continuar",
            "+/- : Velocidade",
            "ESC  : Sair"
        ]
        
        for ctrl in controls:
            self._draw_metric_line(ctrl, panel_x + 30, y_offset, self.config.COLORS['text_dim'], self.small_font)
            y_offset += 14
    
    def _draw_courier_status_panel(self, couriers):
        panel_width = 320
        panel_height = min(200, 60 + len(couriers) * 35)
        panel_x = self.config.MAP_SIZE[0] - panel_width - 20
        panel_y = 80
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, self.config.COLORS['panel_bg'], (0, 0, panel_width, panel_height), border_radius=15)
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        pygame.draw.rect(self.screen, self.config.COLORS['panel_border'], panel_rect, 2, border_radius=15)
        
        title = self.title_font.render("🚴 Couriers", True, self.config.COLORS['accent'])
        self.screen.blit(title, (panel_x + 20, panel_y + 15))
        
        y_offset = panel_y + 50
        
        for i, c in enumerate(couriers):
            status_map = {
                "idle": ("⚪ Ocioso", self.config.COLORS['success']),
                "to_pickup": ("🔵 → Coleta", self.config.COLORS['accent']),
                "to_dropoff": ("🟣 → Entrega", self.config.COLORS['warning'])
            }
            status_txt, status_color = status_map.get(c.status, (c.status, self.config.COLORS['text']))
            

            if c.id < len(self.courier_images):
                courier_img = self.courier_images[c.id]
                small_img = pygame.transform.scale(courier_img, (24, 24))
                img_rect = small_img.get_rect(center=(panel_x + 25, y_offset + 8))
                self.screen.blit(small_img, img_rect)
            else:
                color = self._get_courier_color(c.id)
                pygame.draw.circle(self.screen, color, (panel_x + 25, y_offset + 8), 7)
                pygame.draw.circle(self.screen, self.config.COLORS['background'], (panel_x + 25, y_offset + 8), 7, 1)
            
            txt = self.small_font.render(f"C{c.id}: {status_txt}", True, self.config.COLORS['text'])
            self.screen.blit(txt, (panel_x + 40, y_offset + 2))
            
            deliveries_txt = self.small_font.render(f"{c.total_deliveries} entregas", True, self.config.COLORS['text_dim'])
            self.screen.blit(deliveries_txt, (panel_x + 40, y_offset + 17))
            
            y_offset += 35
    
    def _draw_metric_line(self, text, x, y, color, font=None):
        if font is None:
            font = self.font
        label = font.render(text, True, color)
        self.screen.blit(label, (x, y))
    
    def _draw_rounded_rect(self, surface, rect, color, radius):
        pygame.draw.rect(surface, color, rect, border_radius=radius)
    
    def _draw_dashed_line(self, start, end, color, dash_length=10):
        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return
        
        dashes = int(distance / dash_length)
        for i in range(dashes):
            if i % 2 == 0:
                start_pos = (
                    x1 + (dx * i / dashes),
                    y1 + (dy * i / dashes)
                )
                end_pos = (
                    x1 + (dx * (i + 1) / dashes),
                    y1 + (dy * (i + 1) / dashes)
                )
                pygame.draw.line(self.screen, color, start_pos, end_pos, 1)
    
    def _draw_animated_line(self, start, end, color):
        x1, y1 = start
        x2, y2 = end
        
        pygame.draw.line(self.screen, color, start, end, 2)
        
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            progress = (self.time * 0.5) % 1.0
            point_x = x1 + dx * progress
            point_y = y1 + dy * progress
            
            glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, 150), (10, 10), 5)
            self.screen.blit(glow_surf, (int(point_x) - 10, int(point_y) - 10))
    
    def _get_courier_color(self, courier_id):
        palette = self.config.COLORS['courier_palette']
        return palette[courier_id % len(palette)]
    
    def _make_circular_image(self, img, size):
        """Aplica uma máscara circular na imagem"""
        if img.get_size() != (size, size):
            img = pygame.transform.scale(img, (size, size))
        
        img_with_alpha = img.convert_alpha()
        
        final_img = pygame.Surface((size, size), pygame.SRCALPHA)
        final_img.blit(img_with_alpha, (0, 0))
        
        center = size // 2
        radius = size // 2
        radius_sq = radius * radius
        
        for x in range(size):
            for y in range(size):
                dx = x - center
                dy = y - center
                if dx * dx + dy * dy > radius_sq:
                    final_img.set_at((x, y), (0, 0, 0, 0))
        
        return final_img
    
    def _load_courier_images(self):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
        courier_image_files = ['Pedro.jpg', 'Barreto.png']
        
        self.courier_images = []
        for img_file in courier_image_files:
            img_path = os.path.join(assets_dir, img_file)
            try:
                img = pygame.image.load(img_path)
                img = img.convert_alpha()
                circular_img = self._make_circular_image(img, 64)
                self.courier_images.append(circular_img)
            except Exception as e:
                placeholder = pygame.Surface((64, 64), pygame.SRCALPHA)
                pygame.draw.circle(placeholder, (100, 100, 100, 255), (32, 32), 32)
                self.courier_images.append(placeholder)
    
    def cleanup(self):
        pygame.quit()
