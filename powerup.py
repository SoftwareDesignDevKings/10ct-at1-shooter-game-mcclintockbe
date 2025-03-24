import app

class powerup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = app.pygame.Surface((15, 15), app.pygame.SRCALPHA)
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)