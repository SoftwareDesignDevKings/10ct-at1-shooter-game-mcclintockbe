def draw(self):
    self.screen.blit(self.background, (0, 0))

    if not self.game_over:
        self.player.draw(self.screen) 

    for enemy in self.enemies:
        enemy.draw(self.screen)

    pygame.display.flip()
