import pygame


class UIController:
    
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.speed_mult = 1.0
    
    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.speed_mult = min(10.0, self.speed_mult * 1.5)
                elif event.key == pygame.K_MINUS:
                    self.speed_mult = max(0.25, self.speed_mult / 1.5)
        
        return True
    
    def tick(self, fps=60):
        self.clock.tick(fps)
    
    def flip_display(self):
        pygame.display.flip()
