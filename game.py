# game.py
from ast import main
import pygame
import random
import os
import math
import time
import threading

import app
from coin import Coin
from enemy import Enemy
from player import Player
from powerup import powerup 

class Game:
  
    def __init__(self):
        pygame.init()  # Initialize Pygame

        # All of the important variables except the player stats. e.g sfx, xp, emeny 
        # characteristics, etc
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 40
        self.enemies_per_spawn = 1
        self.player_level = 0
        self.powerup_number = 0
        self.xp = 0
        self.level_up_amount = 5
        self.xp_progression = 1
        self.last_level_up = "None"
        self.level_up_sfx = pygame.mixer.Sound('assets/sfx/level_up.wav')
        self.enemy_kill_sfx = pygame.mixer.Sound('assets/sfx/enemy_killed.wav')
        self.health_regen_sfx = pygame.mixer.Sound('assets/sfx/health_recharge.wav')
        self.bullet_fire_sfx = pygame.mixer.Sound('assets/sfx/bullet_fire.wav')
        self.game_start_sfx = pygame.mixer.Sound('assets/sfx/game_start.mp3')
        self.coin_collect_sfx = pygame.mixer.Sound('assets/sfx/coin-257878.mp3')
        self.power_up_collect_sfx = pygame.mixer.Sound('assets/sfx/power_up_grab-88510.mp3')
        self.game_over_sfx = pygame.mixer.Sound('assets/sfx/game-over-arcade-6435.mp3')
        self.player_damage_sfx = pygame.mixer.Sound('assets/sfx/mixkit-soft-quick-punch-2151.wav')
        self.invulnerable_until = 0


        #Create a game window using Pygame
        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT))
        pygame.display.set_caption("AT1 2D Shooter")

        self.clock = pygame.time.Clock()

        #Set up the game clock for frame rate control
        

        #Load assets (e.g., fonts, images)
        self.assets = app.load_assets()
        font_path = os.path.join("assets", "PressStart2P.ttf")
        self.font_small = pygame.font.Font(font_path, 18)
        self.font_large = pygame.font.Font(font_path, 32)


        # Create a random background
        self.background = self.create_random_background(
            app.WIDTH, app.HEIGHT, self.assets["floor_tiles"]
        )

         # Set up game state variables
        self.running = True
        self.game_over = False
        self.coins = []
        self.powerup = []
        

        self.enemies = 1
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 60
        self.enemies_per_spawn = 1
        self.reset_game()

    def reset_game(self):
        #reset all varibles when game reset
        self.player = Player(app.WIDTH // 2, app.HEIGHT // 2, self.assets)
        self.game_start_sfx.play()
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemies_per_spawn = 1
        self.coins = []
        self.powerup = []

        self.game_over = False

    def create_random_background(self, width, height, floor_tiles):
        #set the background from assets
        print("{create_random_background} is running")
        bg = pygame.Surface((width, height))
        tile_w = floor_tiles[0].get_width()
        tile_h = floor_tiles[0].get_height()

        for y in range(0, height, tile_h):
            for x in range(0, width, tile_w):
                tile = random.choice(floor_tiles)
                bg.blit(tile, (x, y))

        return bg
    
    def spawn_enemies(self):
        #time enemy spawning
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0

            for _ in range(self.enemies_per_spawn):
                #randomly decide where enemies spawn
                side = random.choice(["top", "bottom", "left", "right"])
                if side == "top":
                    x = random.randint(0, app.WIDTH)
                    y = -app.SPAWN_MARGIN
                elif side == "bottom":
                    x = random.randint(0, app.WIDTH)
                    y = app.HEIGHT + app.SPAWN_MARGIN
                elif side == "left":
                    x = -app.SPAWN_MARGIN
                    y = random.randint(0, app.HEIGHT)
                else:
                    x = app.WIDTH + app.SPAWN_MARGIN
                    y = random.randint(0, app.HEIGHT)

            enemy_type = random.choice(list(self.assets["enemies"].keys()))
            enemy = Enemy(x, y, enemy_type, self.assets["enemies"])
            self.enemies.append(enemy)

    def run(self):
        while self.running:
            self.clock.tick(app.FPS)
            self.handle_events()

            if not self.game_over:
                #keep running until player dies
                self.update()

            self.draw()

        pygame.quit()   
    

    def handle_events(self):
        """Process user input (keyboard, mouse, quitting)."""

        for event in pygame.event.get():
          
            if event.type == pygame.QUIT:
                 self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

    def update(self):
        self.player.handle_input()
        self.player.update()
        for enemy in self.enemies:
            enemy.update(self.player)

        #all of the functions that must always be running
        self.check_player_enemy_collisions()
        self.check_bullet_enemy_collisions()
        self.check_player_coin_collisions()
        self.check_player_powerup_collisions()
        self.test_level_up()

        if self.player.health <= 0:
            self.game_over_sfx.play()
            self.game_over = True
            return
        self.spawn_enemies()

    def draw(self):
        self.screen.blit(self.background, (0, 0))


        for coin in self.coins:
            coin.draw(self.screen)
        
        for powerup in self.powerup:
            powerup.draw(self.screen)

            
        if not self.game_over:
            self.player.draw(self.screen) 

        for enemy in self.enemies:
            enemy.draw(self.screen)

        hp = max(0, min(self.player.health, 5))
        health_img = self.assets["health"][hp]
        self.screen.blit(health_img, (10, 10))

        # Text on the side for info

        xp_text_surf = self.font_small.render(f"XP to next level: {int(self.level_up_amount - self.player.xp)}", True, (255, 255, 255))
        self.screen.blit(xp_text_surf, (10, 70))

        level_text_surf = self.font_small.render(f"Level: {self.player_level}", True, (255, 255, 255))
        self.screen.blit(level_text_surf, (10, 100))

        upgrade_text_surf = self.font_small.render(f"Last Upgrade: {self.last_level_up}", True, (255, 255, 255))
        self.screen.blit(upgrade_text_surf, (10, 130))

        if self.game_over:
            self.player_level = 0
            self.level_up_amount = 5
            self.last_level_up = "None"
            self.draw_game_over_screen()

        pygame.display.flip()

    def check_player_enemy_collisions(self):
        if pygame.time.get_ticks() < self.invulnerable_until:
            return
        collided = False
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                
                collided = True
                break

        if collided:
            self.player.take_damage(1)
            self.player_damage_sfx.play()
            #Makes sure the player cant take damage for half a second after taking damage to avoid instant deaths by touching multiple
            #enemies at once or accidentally following ones in knockback
            self.invulnerable_until = pygame.time.get_ticks() + 500
            px, py = self.player.x, self.player.y
            for enemy in self.enemies:
                enemy.set_knockback(px, py, app.PUSHBACK_DISTANCE)



    def draw_game_over_screen(self):
        # Dark overlay
        overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_surf = self.font_large.render("GAME OVER!", True, (255, 0, 0))
        game_over_rect = game_over_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 - 50))
        self.screen.blit(game_over_surf, game_over_rect)

        # Prompt to restart or quit
        prompt_surf = self.font_small.render("Press R to Play Again or ESC to Quit", True, (255, 255, 255))
        prompt_rect = prompt_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 + 20))
        self.screen.blit(prompt_surf, prompt_rect)
    
    def find_nearest_enemy(self):
        if not self.enemies:
            return None
        nearest = None
        min_dist = float('inf')
        px, py = self.player.x, self.player.y
        for enemy in self.enemies:
            # More Pythag
            dist = math.sqrt((enemy.x - px)**2 + (enemy.y - py)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
        return nearest
    
    

    def handle_events(self):
        #Keeps everything Running
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                else:
                    if event.key == pygame.K_SPACE:
                        nearest_enemy = self.find_nearest_enemy()
                        if nearest_enemy:
                            self.player.shoot_toward_enemy(nearest_enemy)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.player.shoot_toward_mouse(event.pos)
    
    def find_nearest_enemy(self):
        #locates nearest enemy
        if not self.enemies:
            return None
        nearest = None
        min_dist = float('inf')
        px, py = self.player.x, self.player.y
        for enemy in self.enemies:
            dist = math.sqrt((enemy.x - px)**2 + (enemy.y - py)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
        return nearest
    
    def check_bullet_enemy_collisions(self):
        #does everything important when bullet touches bad guy
        bullets_to_remove = []
        enemies_to_remove = []
        for bullet in self.player.bullets[:]:  # Iterate over a copy of the list
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):
                    bullets_to_remove.append(bullet)  # Mark bullet for removal
                    enemies_to_remove.append(enemy)  # Store enemy to remove later

                    #drops a coin
                    new_coin = Coin(enemy.x, enemy.y)
                    self.coins.append(new_coin)

                    # Random chance of powerup being dropped
                    if random.choice([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]) == 15:
                        new_powerup = powerup(enemy.x, enemy.y)
                        self.powerup.append(new_powerup)

                    #kills the bad guy
                    self.enemy_kill_sfx.play()
                    self.enemies.remove(enemy)
        # Remove bullets outside of the loop
        for bullet in bullets_to_remove:
            if bullet in self.player.bullets:
                self.player.bullets.remove(bullet)

        for enemy in enemies_to_remove:
            if enemy in self.enemies:  # Check before removing
                self.enemies.remove(enemy)
    
    def check_player_coin_collisions(self):
        #Allows for coin collection when the player does over coin
        coins_collected = []
        for coin in self.coins:
                if coin.rect.colliderect(self.player.rect):
                    self.coin_collect_sfx.play()
                    coins_collected.append(coin)

                    self.player.add_xp(self.xp_progression)
        for c in coins_collected:
            if c in self.coins:
                self.coins.remove(c) 
    
    def check_player_powerup_collisions(self):
        # Allows for powerup collection
        powerups_collected = []
        for powerup in self.powerup:
                if powerup.rect.colliderect(self.player.rect):
                    self.power_up_collect_sfx.play()
                    self.powerup_number = random.choice([1, 2, 3, 4])
                    # Activates a random powerup for 15 seconds
                    if self.powerup_number == 1:
                        #When speed gets too high, the game becomes unplayable, so i limited it to avoid stacking speed buffs too much
                        if self.player.speed < 8:
                            self.player.speed = self.player.speed*2 - 1
                            threading.Timer(15, self.reset_speed).start()
                            self.reset_speed
                        else:
                            self.powerup_numder = random.choice ([2, 3, 4])

                        
                    if self.powerup_number == 2:
                        self.player.bullet_count = self.player.bullet_count*3
                        threading.Timer(15, self.reset_bullets).start()
                        
                        
                    elif self.powerup_number == 3:
                        self.player.health = self.player.health+3
                    else:
                        self.xp_progression += 2
                        threading.Timer(15, self.reset_xp).start()
                        
                        
                    powerups_collected.append(powerup)
        
        for p in powerups_collected:
            self.powerup.remove(p) 




                   

        

    #probably where the error is, all my own code, level up system
    def test_level_up(self):
        
        #Makes a random level up upgrade every level
        level_up_choice = random.choice([1,2,3,4,5])
        if self.player.xp >= self.level_up_amount:
            self.level_up_sfx.play()
            if level_up_choice == 1:
                #lowers something exponetioally to avoid negative functions if the game goes on too long, to avoid problems we dont need
                self.player.shoot_cooldown = self.player.shoot_cooldown*0.9   
                #Changes the text on the left so they know what level up they got        
                self.last_level_up = "Shot Cooldown"
            elif level_up_choice == 2:
                self.player.health = self.player.health+1               
                self.last_level_up = "Health Increase"
                self.health_regen_sfx.play()
            elif level_up_choice == 3:
                self.player.bullet_size = self.player.bullet_size*1.4               
                self.last_level_up = "Bullet Size"
            elif level_up_choice == 4:
                app.PLAYER_SPEED = app.PLAYER_SPEED*1.2
                self.player.speed = app.PLAYER_SPEED              
                self.last_level_up = "Movement Speed"
            else:
                self.player.bullet_speed = self.player.bullet_speed*1.3               
                self.last_level_up = "Bullet speed"
            #resets xp
            self.player.xp = 0
            #Increases Xp need for next level
            self.level_up_amount = self.level_up_amount*1.3
            #Increases Level
            self.player_level = self.player_level+1
            #Enemyies spawn faster the higher your level, to keep some difficulty
            self.enemy_spawn_interval = self.enemy_spawn_interval*0.9
            #little buffs at milestones regardless of upgrades
            if self.player_level == 5:
                self.player.bullet_count += 3
            if self.player_level == 10:
                self.player.bullet_count += 5
    #resets powerups
    def reset_speed(self):
        self.player.speed = self.player.speed - 1

    def reset_bullets(self):
        self.player.bullet_count /= 3

    def reset_xp(self):
        self.xp_progression -= 2



   
        