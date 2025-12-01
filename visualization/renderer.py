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
            self.alert_font = pygame.font.SysFont("Segoe UI", 24, bold=True)
        except:
            self.title_font = pygame.font.SysFont("Arial", 18, bold=True)
            self.font = pygame.font.SysFont("Arial", 13)
            self.small_font = pygame.font.SysFont("Arial", 11)
            self.alert_font = pygame.font.SysFont("Arial", 24, bold=True)
        
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
        self._draw_pending_orders_panel(env, orders_queue, couriers)
        self._draw_peak_alert(metrics, env)
    
    def _draw_background(self):
        # Gradiente de fundo mais suave e escuro
        for y in range(0, self.config.MAP_SIZE[1], 8):
            factor = y / self.config.MAP_SIZE[1]
            # Gradiente radial do centro
            center_y = self.config.MAP_SIZE[1] / 2
            distance_from_center = abs(y - center_y) / center_y
            
            r = int(self.config.COLORS['background'][0] + (self.config.COLORS['background_light'][0] - self.config.COLORS['background'][0]) * factor * 0.5)
            g = int(self.config.COLORS['background'][1] + (self.config.COLORS['background_light'][1] - self.config.COLORS['background'][1]) * factor * 0.5)
            b = int(self.config.COLORS['background'][2] + (self.config.COLORS['background_light'][2] - self.config.COLORS['background'][2]) * factor * 0.5)
            
            # Adicionar variação radial
            vignette = 1 - (distance_from_center * 0.2)
            r = int(r * vignette)
            g = int(g * vignette)
            b = int(b * vignette)
            
            pygame.draw.rect(self.screen, (r, g, b), (0, y, self.config.MAP_SIZE[0], 8))
    
    def _draw_grid(self):
        # Grid com efeito de profundidade
        for i in range(0, self.config.MAP_SIZE[0], 50):
            # Linhas verticais com gradiente
            for y in range(0, self.config.MAP_SIZE[1], 50):
                alpha = int(25 + 10 * math.sin(y / 100))
                color = (*self.config.COLORS['grid'][:3], alpha) if len(self.config.COLORS['grid']) == 3 else self.config.COLORS['grid']
                pygame.draw.line(self.screen, color, (i, y), (i, min(y + 50, self.config.MAP_SIZE[1])), 1)
        
        for i in range(0, self.config.MAP_SIZE[1], 50):
            # Linhas horizontais com gradiente
            for x in range(0, self.config.MAP_SIZE[0], 50):
                alpha = int(25 + 10 * math.sin(x / 100))
                color = (*self.config.COLORS['grid'][:3], alpha) if len(self.config.COLORS['grid']) == 3 else self.config.COLORS['grid']
                pygame.draw.line(self.screen, color, (x, i), (min(x + 50, self.config.MAP_SIZE[0]), i), 1)
        
        # Grid maior (major) com mais destaque
        for i in range(0, self.config.MAP_SIZE[0], 200):
            pygame.draw.line(self.screen, self.config.COLORS['grid_major'], 
                           (i, 0), (i, self.config.MAP_SIZE[1]), 1)
        for i in range(0, self.config.MAP_SIZE[1], 200):
            pygame.draw.line(self.screen, self.config.COLORS['grid_major'], 
                           (0, i), (self.config.MAP_SIZE[0], i), 1)
    
    def _draw_header(self):
        header_height = 70
        header_rect = pygame.Rect(0, 0, self.config.MAP_SIZE[0], header_height)
        
        # Gradiente no header
        header_surf = pygame.Surface((self.config.MAP_SIZE[0], header_height), pygame.SRCALPHA)
        for y in range(header_height):
            factor = y / header_height
            alpha = int(230 - factor * 50)
            r = int(20 + factor * 15)
            g = int(25 + factor * 15)
            b = int(35 + factor * 15)
            pygame.draw.line(header_surf, (r, g, b, alpha), (0, y), (self.config.MAP_SIZE[0], y))
        self.screen.blit(header_surf, (0, 0))
        
        # Linha de borda com brilho
        glow_surf = pygame.Surface((self.config.MAP_SIZE[0], 6), pygame.SRCALPHA)
        for i in range(3):
            alpha = 80 - i * 25
            pygame.draw.line(glow_surf, (*self.config.COLORS['accent'], alpha), 
                           (0, i), (self.config.MAP_SIZE[0], i), 1)
        self.screen.blit(glow_surf, (0, header_height - 3))
        
        # Título com efeito de brilho
        title_text = "🚀 FLASH MOVE"
        
        # Sombra do título
        title_shadow = self.title_font.render(title_text, True, (0, 0, 0, 150))
        self.screen.blit(title_shadow, (22, 18))
        
        # Título principal com gradiente simulado
        title = self.title_font.render(title_text, True, self.config.COLORS['accent'])
        self.screen.blit(title, (20, 16))
        
        # Brilho no título
        pulse = abs(math.sin(self.time * 2)) * 0.3 + 0.7
        glow_title = self.title_font.render(title_text, True, (*self.config.COLORS['accent'], int(100 * pulse)))
        self.screen.blit(glow_title, (20, 16), special_flags=pygame.BLEND_ADD)
        
        subtitle = self.small_font.render("Simulação de Sistema de Delivery em Tempo Real", True, self.config.COLORS['text_dim'])
        self.screen.blit(subtitle, (22, 44))
        
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
            
            # Linha tracejada com gradiente
            self._draw_dashed_line((px, py), (dx, dy), color, dash_length=10)
            
            # Dropoff com sombra e brilho
            if self.config.SHOW_SHADOWS:
                for i in range(3):
                    shadow_alpha = 40 - i * 10
                    pygame.draw.circle(self.screen, (0, 0, 0, shadow_alpha), (dx + 2 + i, dy + 2 + i), 8 + i)
            
            # Anel externo do dropoff
            pulse_drop = abs(math.sin(self.time * 2 + o.id * 0.5)) * 2 + 6
            pygame.draw.circle(self.screen, (*color, 100), (dx, dy), int(pulse_drop), 2)
            pygame.draw.circle(self.screen, color, (dx, dy), 7, 2)
            pygame.draw.circle(self.screen, (*color, 150), (dx, dy), 4)
            
            # Pickup com animação pulsante aprimorada
            if self.config.SHOW_SHADOWS:
                for i in range(3):
                    shadow_alpha = 50 - i * 12
                    pygame.draw.circle(self.screen, (0, 0, 0, shadow_alpha), (px + 2 + i, py + 2 + i), 11 + i)
            
            pulse = math.sin(self.time * 4 + o.id) * 3 + 10
            
            # Múltiplas camadas de brilho
            for i in range(3, 0, -1):
                glow_size = int(pulse * (1 + i * 0.3))
                glow_alpha = int(40 / i)
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, glow_alpha), (glow_size, glow_size), glow_size)
                self.screen.blit(glow_surf, (px - glow_size, py - glow_size))
            
            # Círculo principal do pickup
            pygame.draw.circle(self.screen, color, (px, py), 10)
            pygame.draw.circle(self.screen, (*self.config.COLORS['background'], 200), (px, py), 10, 3)
            
            # Brilho interno
            highlight_offset = 2
            pygame.draw.circle(self.screen, (*color, 150), (px - highlight_offset, py - highlight_offset), 4)
            
            # Label com estilo aprimorado
            label_text = f"#{o.id}"
            label = self.small_font.render(label_text, True, (255, 255, 255))
            label_rect = label.get_rect()
            label_rect.topleft = (px + 14, py - 10)
            
            bg_rect = label_rect.inflate(10, 6)
            
            # Sombra do label
            shadow_surf = pygame.Surface((bg_rect.width + 4, bg_rect.height + 4), pygame.SRCALPHA)
            self._draw_rounded_rect(shadow_surf, pygame.Rect(2, 2, bg_rect.width, bg_rect.height), (0, 0, 0, 80), 8)
            self.screen.blit(shadow_surf, (bg_rect.x - 2, bg_rect.y - 2))
            
            # Fundo do label com gradiente
            label_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            for y in range(bg_rect.height):
                factor = y / bg_rect.height
                alpha = int(200 + 55 * factor)
                pygame.draw.line(label_surf, (*color, alpha), (0, y), (bg_rect.width, y))
            
            # Aplicar bordas arredondadas
            mask = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, bg_rect.width, bg_rect.height), border_radius=8)
            for x in range(bg_rect.width):
                for y in range(bg_rect.height):
                    mask_alpha = mask.get_at((x, y))[3]
                    if mask_alpha > 0:
                        current = label_surf.get_at((x, y))
                        label_surf.set_at((x, y), (*current[:3], int(current[3] * mask_alpha / 255)))
            
            self.screen.blit(label_surf, bg_rect)
            pygame.draw.rect(self.screen, (*color, 255), bg_rect, 2, border_radius=8)
            self.screen.blit(label, label_rect)
    
    def _draw_courier_trails(self, couriers):
        if not self.config.SHOW_TRAILS:
            return
        
        for c in couriers:
            if len(c.trail) > 1:
                trail_color = self._get_courier_color(c.id)
                for i in range(len(c.trail) - 1):
                    progress = i / len(c.trail)
                    alpha = int(self.config.COLORS['trail_alpha'] * progress)
                    color_with_alpha = (*trail_color, alpha)
                    
                    trail_surf = pygame.Surface((self.config.MAP_SIZE[0], self.config.MAP_SIZE[1]), pygame.SRCALPHA)
                    thickness = max(2, int(5 * progress))
                    
                    # Desenhar brilho da trilha
                    glow_thickness = thickness + 4
                    pygame.draw.line(trail_surf, (*trail_color, int(alpha * 0.3)), 
                                   c.trail[i], c.trail[i + 1], glow_thickness)
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
            
            # Múltiplas camadas de sombra para profundidade
            if self.config.SHOW_SHADOWS:
                for i in range(4, 0, -1):
                    shadow_alpha = 70 - i * 15
                    shadow_size = i * 2
                    shadow_surf = pygame.Surface((img_size[0] + shadow_size * 2, img_size[1] + shadow_size * 2), pygame.SRCALPHA)
                    pygame.draw.ellipse(shadow_surf, (0, 0, 0, shadow_alpha), 
                                      (shadow_size, shadow_size + i, img_size[0] + shadow_size, img_size[1] + shadow_size))
                    self.screen.blit(shadow_surf, (x - img_size[0] // 2 - shadow_size, y - img_size[1] // 2 - shadow_size))
            
            # Anel de status ao redor do courier
            if c.status != "idle":
                pulse = abs(math.sin(self.time * 5)) * 8 + img_size[0] // 2 + 8
                
                # Anel externo brilhante
                for i in range(3):
                    ring_alpha = int(80 - i * 25)
                    ring_radius = int(pulse + i * 3)
                    pygame.draw.circle(self.screen, (*color, ring_alpha), (x, y), ring_radius, 2)
            
            # Glow pulsante baseado no status
            if c.status != "idle":
                pulse_glow = abs(math.sin(self.time * 4)) * 10 + 10
                glow_size = int(img_size[0] // 2 + pulse_glow)
                
                # Múltiplas camadas de brilho
                for i in range(3, 0, -1):
                    layer_size = int(glow_size * (1 + i * 0.2))
                    layer_alpha = int(50 / i)
                    glow_surf = pygame.Surface((layer_size * 2, layer_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (*color, layer_alpha), (layer_size, layer_size), layer_size)
                    self.screen.blit(glow_surf, (x - layer_size, y - layer_size))
            
            # Desenhar imagem do courier
            self.screen.blit(courier_img, img_rect)
            
            # Borda brilhante ao redor da imagem
            border_pulse = abs(math.sin(self.time * 3)) * 0.5 + 0.5
            pygame.draw.circle(self.screen, (*color, int(150 * border_pulse)), 
                             (x, y), img_size[0] // 2 + 2, 2)
            
            # Indicador de status aprimorado
            status_colors = {
                "idle": self.config.COLORS['success'],
                "to_pickup": self.config.COLORS['accent'],
                "to_dropoff": self.config.COLORS['warning']
            }
            status_color = status_colors.get(c.status, color)
            status_pos = (x + img_size[0] // 2 - 8, y - img_size[1] // 2 + 8)
            
            # Glow do indicador
            indicator_glow = abs(math.sin(self.time * 6)) * 4 + 8
            glow_surf = pygame.Surface((int(indicator_glow * 2), int(indicator_glow * 2)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*status_color, 60), 
                             (int(indicator_glow), int(indicator_glow)), int(indicator_glow))
            self.screen.blit(glow_surf, (status_pos[0] - int(indicator_glow), status_pos[1] - int(indicator_glow)))
            
            # Indicador sólido
            pygame.draw.circle(self.screen, status_color, status_pos, 6)
            pygame.draw.circle(self.screen, (255, 255, 255), status_pos, 6, 2)
            
            # Highlight interno
            pygame.draw.circle(self.screen, (*status_color, 200), (status_pos[0] - 1, status_pos[1] - 1), 3)
    
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
                order_label = self.small_font.render(order_text, True, (255, 255, 255))
                order_rect = order_label.get_rect(center=(int(mid_x), int(mid_y)))
                
                bg_rect = order_rect.inflate(12, 8)
                
                # Sombra do badge
                shadow_surf = pygame.Surface((bg_rect.width + 6, bg_rect.height + 6), pygame.SRCALPHA)
                self._draw_rounded_rect(shadow_surf, pygame.Rect(3, 3, bg_rect.width, bg_rect.height), (0, 0, 0, 100), 10)
                self.screen.blit(shadow_surf, (bg_rect.x - 3, bg_rect.y - 3))
                
                # Fundo com gradiente
                badge_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                for y_pos in range(bg_rect.height):
                    factor = y_pos / bg_rect.height
                    alpha = int(220 + 35 * factor)
                    pygame.draw.line(badge_surf, (*color, alpha), (0, y_pos), (bg_rect.width, y_pos))
                
                # Aplicar bordas arredondadas
                mask = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, bg_rect.width, bg_rect.height), border_radius=10)
                for x_pos in range(bg_rect.width):
                    for y_pos in range(bg_rect.height):
                        mask_alpha = mask.get_at((x_pos, y_pos))[3]
                        if mask_alpha > 0:
                            current = badge_surf.get_at((x_pos, y_pos))
                            badge_surf.set_at((x_pos, y_pos), (*current[:3], int(current[3] * mask_alpha / 255)))
                
                self.screen.blit(badge_surf, bg_rect)
                
                # Borda brilhante
                border_pulse = abs(math.sin(self.time * 4)) * 0.4 + 0.6
                pygame.draw.rect(self.screen, (*color, int(255 * border_pulse)), bg_rect, 2, border_radius=10)
                
                self.screen.blit(order_label, order_rect)
    
    def _update_particles(self, couriers):
        if not self.config.SHOW_PARTICLES:
            return
        
        for c in couriers:
            if c.status != "idle" and random.random() < 0.4:
                color = self._get_courier_color(c.id)
                # Partículas em direções aleatórias
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.5, 2.0)
                particle = {
                    'pos': list(c.pos),
                    'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                    'life': random.randint(20, 40),
                    'max_life': 40,
                    'color': color,
                    'size': random.uniform(2, 5)
                }
                self.particles.append(particle)
        
        for p in self.particles[:]:
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            p['vel'][0] *= 0.98  # Arrasto
            p['vel'][1] *= 0.98
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)
    
    def _draw_particles(self):
        for p in self.particles:
            life_factor = p['life'] / p.get('max_life', 30)
            alpha = int(life_factor * 150)
            size = int(p.get('size', 4) * life_factor)
            
            if size > 0:
                # Glow da partícula
                glow_size = size * 2
                particle_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(particle_surf, (*p['color'], int(alpha * 0.3)), (glow_size, glow_size), glow_size)
                pygame.draw.circle(particle_surf, (*p['color'], alpha), (glow_size, glow_size), size)
                self.screen.blit(particle_surf, (int(p['pos'][0]) - glow_size, int(p['pos'][1]) - glow_size))
    
    def _draw_metrics_panel(self, env, orders_queue, metrics, couriers, paused, speed_mult):
        panel_width = 380
        panel_height = 500
        panel_x = 20
        panel_y = 80
        
        card_radius = 28
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        shadow_offset = 4
        shadow_surf = pygame.Surface((panel_width + shadow_offset * 2, panel_height + shadow_offset * 2), pygame.SRCALPHA)
        shadow_rect = pygame.Rect(shadow_offset, shadow_offset, panel_width, panel_height)
        for i in range(3):
            alpha = 30 - i * 8
            shadow_size = shadow_offset + i * 2
            shadow_blur = pygame.Surface((panel_width + shadow_size * 2, panel_height + shadow_size * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_blur, (0, 0, 0, alpha), 
                           (shadow_size, shadow_size, panel_width, panel_height), 
                           border_radius=card_radius)
            self.screen.blit(shadow_blur, (panel_x - shadow_size, panel_y - shadow_size))
        
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        bg_top = (50, 53, 60, 245)
        bg_bottom = (40, 43, 50, 250)
        
        for y in range(panel_height):
            factor = y / panel_height
            r = int(bg_top[0] + (bg_bottom[0] - bg_top[0]) * factor)
            g = int(bg_top[1] + (bg_bottom[1] - bg_top[1]) * factor)
            b = int(bg_top[2] + (bg_bottom[2] - bg_top[2]) * factor)
            a = int(bg_top[3] + (bg_bottom[3] - bg_top[3]) * factor)
            pygame.draw.line(panel_surf, (r, g, b, a), (0, y), (panel_width, y))
        
        mask = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, panel_width, panel_height), border_radius=card_radius)
        
        for x in range(panel_width):
            for y in range(panel_height):
                mask_alpha = mask.get_at((x, y))[3]
                if mask_alpha < 255:
                    current_color = panel_surf.get_at((x, y))
                    panel_surf.set_at((x, y), (*current_color[:3], int(current_color[3] * mask_alpha / 255)))
        
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        inner_padding = 24
        content_x = panel_x + inner_padding
        content_width = panel_width - inner_padding * 2
        
        header_height = 50
        header_y = panel_y + 12
        
        title = self.title_font.render("Métricas", True, self.config.COLORS['text'])
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, header_y + header_height // 2))
        self.screen.blit(title, title_rect)
        
        divider_y = header_y + header_height - 1
        divider_color = (*self.config.COLORS['text_dim'], 40)
        divider_surf = pygame.Surface((content_width, 1), pygame.SRCALPHA)
        pygame.draw.rect(divider_surf, divider_color, (0, 0, content_width, 1))
        self.screen.blit(divider_surf, (content_x, divider_y))
        
        y_offset = panel_y + header_height + 20
        
        mobile_line_height = 24
        soft_text_color = (200, 205, 215)
        
        completed = metrics['completed']
        total = metrics['total_orders']
        avg_delivery_time = metrics.get('total_delivery_time', 0) / max(1, completed)
        utilization = sum(c.total_busy_time for c in couriers) / (env.now * len(couriers)) * 100 if env.now > 0 else 0
        
        status_icon = "⏸️" if paused else "▶️"
        status_text = f"{status_icon} Tempo: {round(env.now, 1)} / {self.config.SIM_TIME}s"
        self._draw_metric_line(status_text, content_x, y_offset, soft_text_color)
        y_offset += mobile_line_height
        
        speed_text = f"⚡ Velocidade: {round(speed_mult, 1)}x"
        self._draw_metric_line(speed_text, content_x, y_offset, soft_text_color)
        y_offset += mobile_line_height + 16
        
        metrics_data = [
            ("📦 Pendentes", len(orders_queue), self.config.COLORS['warning']),
            ("📊 Total", total, soft_text_color),
            ("✅ Atribuídos", metrics['assigned'], self.config.COLORS['accent']),
            ("✓  Completados", completed, self.config.COLORS['success']),
            ("❌ Desistências", metrics['desisted'], self.config.COLORS['danger']),
        ]
        
        for label, value, color in metrics_data:
            if color == soft_text_color:
                row_color = soft_text_color
            else:
                r, g, b = color
                row_color = (min(255, r + 20), min(255, g + 20), min(255, b + 20))
            
            text = f"{label}: {value}"
            self._draw_metric_line(text, content_x, y_offset, row_color)
            y_offset += mobile_line_height
        
        y_offset += 16
        
        success_rate = completed / max(1, total) * 100
        self._draw_metric_line(f"📈 Taxa de Sucesso: {round(success_rate, 1)}%", 
                               content_x, y_offset, soft_text_color)
        y_offset += mobile_line_height + 8
        
        bar_x = content_x
        bar_y = y_offset
        bar_width = content_width
        bar_height = 12
        
        track_color = (*self.config.COLORS['background_light'], 180)
        pygame.draw.rect(self.screen, track_color, 
                        (bar_x, bar_y, bar_width, bar_height), border_radius=bar_height // 2)
        
        fill_width = int(bar_width * success_rate / 100)
        if fill_width > 0:
            if success_rate < 50:
                base_color = self.config.COLORS['danger']
            elif success_rate < 80:
                base_color = self.config.COLORS['warning']
            else:
                base_color = self.config.COLORS['success']

            pygame.draw.rect(
                self.screen,
                base_color,
                (bar_x, bar_y, fill_width, bar_height),
                border_radius=bar_height // 2
            )
        
        y_offset += mobile_line_height + 12
        
        self._draw_metric_line(f"⏱️  Tempo Médio: {round(avg_delivery_time, 1)}s", 
                               content_x, y_offset, soft_text_color)
        y_offset += mobile_line_height
        
        self._draw_metric_line(f"📊 Utilização: {round(utilization, 1)}%", 
                               content_x, y_offset, soft_text_color)
        y_offset += mobile_line_height + 20
        
        controls_title = self.font.render("🎮 Controles", True, soft_text_color)
        self.screen.blit(controls_title, (content_x, y_offset))
        y_offset += mobile_line_height + 8
        
        controls = [
            "ESPAÇO: Pausar/Continuar",
            "+/- : Velocidade",
            "ESC  : Sair"
        ]
        
        for ctrl in controls:
            self._draw_metric_line(ctrl, content_x + 8, y_offset, soft_text_color, self.small_font)
            y_offset += 16
    
    def _draw_courier_status_panel(self, couriers):
        panel_width = 320
        panel_height = min(250, 125 + len(couriers) * 40)
        panel_x = self.config.MAP_SIZE[0] - panel_width - 20
        panel_y = 80
        
        card_radius = 28
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        shadow_offset = 4
        for i in range(3):
            alpha = 30 - i * 8
            shadow_size = shadow_offset + i * 2
            shadow_blur = pygame.Surface((panel_width + shadow_size * 2, panel_height + shadow_size * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_blur, (0, 0, 0, alpha), 
                           (shadow_size, shadow_size, panel_width, panel_height), 
                           border_radius=card_radius)
            self.screen.blit(shadow_blur, (panel_x - shadow_size, panel_y - shadow_size))
        
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        bg_top = (50, 53, 60, 245)
        bg_bottom = (40, 43, 50, 250)
        
        for y in range(panel_height):
            factor = y / panel_height
            r = int(bg_top[0] + (bg_bottom[0] - bg_top[0]) * factor)
            g = int(bg_top[1] + (bg_bottom[1] - bg_top[1]) * factor)
            b = int(bg_top[2] + (bg_bottom[2] - bg_top[2]) * factor)
            a = int(bg_top[3] + (bg_bottom[3] - bg_top[3]) * factor)
            pygame.draw.line(panel_surf, (r, g, b, a), (0, y), (panel_width, y))
        
        mask = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, panel_width, panel_height), border_radius=card_radius)
        
        for x in range(panel_width):
            for y in range(panel_height):
                mask_alpha = mask.get_at((x, y))[3]
                if mask_alpha < 255:
                    current_color = panel_surf.get_at((x, y))
                    panel_surf.set_at((x, y), (*current_color[:3], int(current_color[3] * mask_alpha / 255)))
        
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        inner_padding = 20
        content_x = panel_x + inner_padding
        content_width = panel_width - inner_padding * 2
        
        header_height = 50
        header_y = panel_y + 12
        
        title = self.title_font.render("Entregadores", True, self.config.COLORS['text'])
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, header_y + header_height // 2))
        self.screen.blit(title, title_rect)
        
        divider_y = header_y + header_height - 1
        divider_color = (*self.config.COLORS['text_dim'], 40)
        divider_surf = pygame.Surface((content_width, 1), pygame.SRCALPHA)
        pygame.draw.rect(divider_surf, divider_color, (0, 0, content_width, 1))
        self.screen.blit(divider_surf, (content_x, divider_y))
        
        y_offset = panel_y + header_height + 20
        row_spacing = 70
        
        for i, c in enumerate(couriers):
            status_map = {
                "idle": ("Ocioso", self.config.COLORS['success']),
                "to_pickup": ("→ Coleta", self.config.COLORS['accent']),
                "to_dropoff": ("→ Entrega", self.config.COLORS['warning'])
            }
            status_txt, status_color = status_map.get(c.status, (c.status, self.config.COLORS['text']))
            
            icon_size = 32
            icon_x = content_x
            icon_y = y_offset + 12
            
            if c.id < len(self.courier_images):
                courier_img = self.courier_images[c.id]
                small_img = pygame.transform.scale(courier_img, (icon_size, icon_size))
                
                border_surf = pygame.Surface((icon_size + 4, icon_size + 4), pygame.SRCALPHA)
                pygame.draw.circle(border_surf, (*self.config.COLORS['text'], 100), 
                                 (icon_size // 2 + 2, icon_size // 2 + 2), icon_size // 2 + 2)
                self.screen.blit(border_surf, (icon_x - 2, icon_y - 2))
                
                img_rect = small_img.get_rect(center=(icon_x + icon_size // 2, icon_y + icon_size // 2))
                self.screen.blit(small_img, img_rect)
            else:
                color = self._get_courier_color(c.id)
                pygame.draw.circle(self.screen, (*self.config.COLORS['text'], 100), 
                                 (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2 + 2)
                pygame.draw.circle(self.screen, color, 
                                 (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2)
                pygame.draw.circle(self.screen, (*self.config.COLORS['background'], 200), 
                                 (icon_x + icon_size // 2, icon_y + icon_size // 2), icon_size // 2, 2)
            
            text_start_x = content_x + icon_size + 12
            
            courier_name = c.name
            name_txt = self.font.render(courier_name, True, self.config.COLORS['text'])
            self.screen.blit(name_txt, (text_start_x, y_offset + 4))
            
            status_badge_x = text_start_x
            status_badge_y = y_offset + 24
            
            badge_size = 6
            pygame.draw.circle(self.screen, status_color, 
                             (status_badge_x, status_badge_y + 7), badge_size)
            pygame.draw.circle(self.screen, (*status_color, 150), 
                             (status_badge_x, status_badge_y + 7), badge_size + 1, 1)
            
            status_display = self.font.render(status_txt, True, status_color)
            self.screen.blit(status_display, (status_badge_x + 12, status_badge_y))
            
            deliveries_txt = self.small_font.render(f"{c.total_deliveries} entregas", True, self.config.COLORS['text_dim'])
            self.screen.blit(deliveries_txt, (text_start_x, y_offset + 44))
            
            y_offset += row_spacing
    
    def _draw_pending_orders_panel(self, env, orders_queue, couriers):
        active_orders = []
        for c in couriers:
            if c.current_order:
                active_orders.append(c.current_order)
        
        total_orders = list(orders_queue) + active_orders
        if not total_orders:
            return
        
        panel_width = 320
        max_cards = 6
        card_height = 60
        header_height = 50
        card_spacing = 8
        visible_cards = min(len(total_orders), max_cards)
        
        panel_height = header_height + 20 + (visible_cards * (card_height + card_spacing))
        panel_x = self.config.MAP_SIZE[0] - panel_width - 20
        
        courier_panel_height = min(250, 125 + len(couriers) * 40)
        panel_y = 80 + courier_panel_height + 20
        
        card_radius = 28
        
        shadow_offset = 4
        for i in range(3):
            alpha = 30 - i * 8
            shadow_size = shadow_offset + i * 2
            shadow_blur = pygame.Surface((panel_width + shadow_size * 2, panel_height + shadow_size * 2), pygame.SRCALPHA)
            pygame.draw.rect(shadow_blur, (0, 0, 0, alpha), 
                           (shadow_size, shadow_size, panel_width, panel_height), 
                           border_radius=card_radius)
            self.screen.blit(shadow_blur, (panel_x - shadow_size, panel_y - shadow_size))
        
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        bg_top = (50, 53, 60, 245)
        bg_bottom = (40, 43, 50, 250)
        
        for y in range(panel_height):
            factor = y / panel_height
            r = int(bg_top[0] + (bg_bottom[0] - bg_top[0]) * factor)
            g = int(bg_top[1] + (bg_bottom[1] - bg_top[1]) * factor)
            b = int(bg_top[2] + (bg_bottom[2] - bg_top[2]) * factor)
            a = int(bg_top[3] + (bg_bottom[3] - bg_top[3]) * factor)
            pygame.draw.line(panel_surf, (r, g, b, a), (0, y), (panel_width, y))
        
        mask = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, panel_width, panel_height), border_radius=card_radius)
        
        for x in range(panel_width):
            for y in range(panel_height):
                mask_alpha = mask.get_at((x, y))[3]
                if mask_alpha < 255:
                    current_color = panel_surf.get_at((x, y))
                    panel_surf.set_at((x, y), (*current_color[:3], int(current_color[3] * mask_alpha / 255)))
        
        self.screen.blit(panel_surf, (panel_x, panel_y))
        
        inner_padding = 20
        content_x = panel_x + inner_padding
        content_width = panel_width - inner_padding * 2
        
        header_y = panel_y + 12
        
        title = self.title_font.render("Entregas Pendentes", True, self.config.COLORS['text'])
        title_rect = title.get_rect(center=(panel_x + panel_width // 2, header_y + header_height // 2))
        self.screen.blit(title, title_rect)
        
        divider_y = header_y + header_height - 1
        divider_color = (*self.config.COLORS['text_dim'], 40)
        divider_surf = pygame.Surface((content_width, 1), pygame.SRCALPHA)
        pygame.draw.rect(divider_surf, divider_color, (0, 0, content_width, 1))
        self.screen.blit(divider_surf, (content_x, divider_y))
        
        y_offset = panel_y + header_height + 20
        
        sorted_orders = sorted(total_orders, key=lambda o: self._calculate_priority(o, env), reverse=True)
        
        for i, order in enumerate(sorted_orders[:visible_cards]):
            is_active = order in active_orders
            
            wait_time = env.now - order.created
            
            priority_score = self._calculate_priority(order, env)
        
            if priority_score >= 3.5:
                order_color = self.config.COLORS['order_urgent']
                priority_text = "Muito Alta"
            elif priority_score >= 2.5:
                order_color = self.config.COLORS['order_urgent']
                priority_text = "Alta"
            elif priority_score >= 1.5:
                order_color = self.config.COLORS['order_waiting']
                priority_text = "Média"
            else:
                order_color = self.config.COLORS['order_new']
                priority_text = "Baixa"
            
            card_surf = pygame.Surface((content_width, card_height), pygame.SRCALPHA)
            card_bg = (*order_color, 40)
            pygame.draw.rect(card_surf, card_bg, (0, 0, content_width, card_height), border_radius=12)
            pygame.draw.rect(card_surf, order_color, (0, 0, content_width, card_height), width=2, border_radius=12)
            
            self.screen.blit(card_surf, (content_x, y_offset))
            
            order_id_text = f"#{order.id}"
            order_id_label = self.font.render(order_id_text, True, self.config.COLORS['text'])
            self.screen.blit(order_id_label, (content_x + 12, y_offset + 8))
            
            if is_active:
                status_text = "Em Andamento"
                for c in couriers:
                    if c.current_order == order:
                        if c.status == "to_pickup":
                            status_text = "→ Coleta"
                        elif c.status == "to_dropoff":
                            status_text = "→ Entrega"
                        break
                status_label = self.small_font.render(status_text, True, self.config.COLORS['accent'])
                self.screen.blit(status_label, (content_x + 12, y_offset + 30))
            else:
                status_text = "Na Fila"
                status_label = self.small_font.render(status_text, True, self.config.COLORS['text_dim'])
                self.screen.blit(status_label, (content_x + 12, y_offset + 30))
            
            priority_label = self.small_font.render(f"Prioridade: {priority_text}", True, order_color)
            priority_rect = priority_label.get_rect()
            priority_rect.topright = (content_x + content_width - 12, y_offset + 10)
            self.screen.blit(priority_label, priority_rect)
            
            wait_time_text = f"{round(wait_time, 1)}s"
            wait_label = self.small_font.render(wait_time_text, True, self.config.COLORS['text_dim'])
            wait_rect = wait_label.get_rect()
            wait_rect.topright = (content_x + content_width - 12, y_offset + 38)
            self.screen.blit(wait_label, wait_rect)
            
            y_offset += card_height + card_spacing
    
    def _calculate_priority(self, order, env):
        wait_time = env.now - order.created
        
        base_priority = getattr(order, 'base_priority', 2.0)
        
        time_penalty = 0
        if wait_time >= self.config.ORDER_COLOR_THRESHOLDS['waiting']:
            time_penalty = 2.0 + min((wait_time - self.config.ORDER_COLOR_THRESHOLDS['waiting']) / 100, 1.0)
        elif wait_time >= self.config.ORDER_COLOR_THRESHOLDS['new']:
            time_penalty = 1.0 + (wait_time - self.config.ORDER_COLOR_THRESHOLDS['new']) / 70
        
        variability = random.uniform(-0.15, 0.15)
        
        priority_score = base_priority + time_penalty + variability
        
        return priority_score
    
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
        
        # Linha com gradiente de transparência
        line_surf = pygame.Surface((self.config.MAP_SIZE[0], self.config.MAP_SIZE[1]), pygame.SRCALPHA)
        
        # Desenhar linha base com brilho
        pygame.draw.line(line_surf, (*color, 80), start, end, 4)
        pygame.draw.line(line_surf, (*color, 180), start, end, 2)
        self.screen.blit(line_surf, (0, 0))
        
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Múltiplos pontos animados ao longo da linha
            for i in range(3):
                progress = ((self.time * 0.8 + i * 0.33) % 1.0)
                point_x = x1 + dx * progress
                point_y = y1 + dy * progress
                
                # Brilho pulsante
                pulse = abs(math.sin(self.time * 5 + i)) * 0.5 + 0.5
                glow_size = int(8 * pulse)
                
                glow_surf = pygame.Surface((glow_size * 3, glow_size * 3), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, int(100 * pulse)), (glow_size * 1.5, glow_size * 1.5), glow_size * 1.5)
                pygame.draw.circle(glow_surf, (*color, int(200 * pulse)), (glow_size * 1.5, glow_size * 1.5), glow_size)
                self.screen.blit(glow_surf, (int(point_x) - int(glow_size * 1.5), int(point_y) - int(glow_size * 1.5)))
    
    def _get_courier_color(self, courier_id):
        palette = self.config.COLORS['courier_palette']
        return palette[courier_id % len(palette)]
    
    def _make_circular_image(self, img, size):
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
    
    def _draw_peak_alert(self, metrics, env):
        """Desenha alerta de pico de pedidos na tela"""
        if not metrics.get('peak_active', False):
            return
        
        alert_width = 500
        alert_height = 80
        alert_x = (self.config.MAP_SIZE[0] - alert_width) // 2
        alert_y = 70
        
        pulse = abs(math.sin(self.time * 3)) * 0.2 + 0.8
        
        shadow_surf = pygame.Surface((alert_width + 10, alert_height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 100), (5, 5, alert_width, alert_height), border_radius=20)
        self.screen.blit(shadow_surf, (alert_x - 5, alert_y - 5))
        
        alert_surf = pygame.Surface((alert_width, alert_height), pygame.SRCALPHA)
        danger_color = self.config.COLORS['danger']
        
        for y in range(alert_height):
            factor = y / alert_height
            alpha = int(220 + 35 * factor)
            r = int(danger_color[0] * pulse)
            g = int(danger_color[1] * pulse)
            b = int(danger_color[2] * pulse)
            pygame.draw.line(alert_surf, (r, g, b, alpha), (0, y), (alert_width, y))
        
        mask = pygame.Surface((alert_width, alert_height), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, alert_width, alert_height), border_radius=20)
        
        for x in range(alert_width):
            for y in range(alert_height):
                mask_alpha = mask.get_at((x, y))[3]
                if mask_alpha < 255:
                    current_color = alert_surf.get_at((x, y))
                    alert_surf.set_at((x, y), (*current_color[:3], int(current_color[3] * mask_alpha / 255)))
        
        self.screen.blit(alert_surf, (alert_x, alert_y))
        
        border_surf = pygame.Surface((alert_width, alert_height), pygame.SRCALPHA)
        pygame.draw.rect(border_surf, (*danger_color, int(255 * pulse)), 
                        (0, 0, alert_width, alert_height), width=3, border_radius=20)
        self.screen.blit(border_surf, (alert_x, alert_y))
        
        alert_text = "🔥 PICO DE PEDIDOS! 🔥"
        text_surface = self.alert_font.render(alert_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(alert_x + alert_width // 2, alert_y + alert_height // 2 - 8))
        self.screen.blit(text_surface, text_rect)
        
        remaining = metrics.get('peak_end', 0) - env.now
        if remaining > 0:
            time_text = f"Tempo restante: {int(remaining)}s"
            time_surface = self.small_font.render(time_text, True, (255, 255, 200))
            time_rect = time_surface.get_rect(center=(alert_x + alert_width // 2, alert_y + alert_height // 2 + 18))
            self.screen.blit(time_surface, time_rect)
    
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
