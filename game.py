import pygame
import random
import time

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
ITEM_SIZE = 30
PLAYER_SIZE = 50
ENEMY_SIZE = 40
POWERUP_SIZE = 30
TIMER_LIMIT = 30  # 30 seconds for the game
LEVEL_TIME_LIMIT = 30  # Each level lasts 30 seconds

# Set up screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enhanced Collecting Game")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Fonts
font = pygame.font.Font(None, 36)

# Load sound effects and background music
pygame.mixer.music.load("background_music.mp3")  # Make sure you have a music file
pygame.mixer.music.play(-1, 0.0)  # Loop the background music

# High Score File
high_score_file = "high_score.txt"
try:
    with open(high_score_file, "r") as f:
        high_score = int(f.read())
except FileNotFoundError:
    high_score = 0

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.invincible = False
        self.invincible_timer = 0
        self.speed_boost = False
        self.speed_timer = 0
        self.speed = PLAYER_SPEED

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Handle invincibility timer
        if self.invincible:
            if time.time() - self.invincible_timer > 5:  # 5 seconds of invincibility
                self.invincible = False

        # Handle speed boost timer
        if self.speed_boost:
            if time.time() - self.speed_timer > 5:  # 5 seconds of speed boost
                self.speed_boost = False
                self.speed = PLAYER_SPEED

# Item class
class Item(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((ITEM_SIZE, ITEM_SIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - ITEM_SIZE)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - ITEM_SIZE)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - ENEMY_SIZE)
        self.speed = random.randint(1, 3)  # Random speed for each enemy

    def update(self):
        # Random movement with increased speed for difficulty
        self.rect.x += random.choice([-1, 1]) * self.speed
        self.rect.y += random.choice([-1, 1]) * self.speed
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH - ENEMY_SIZE:
            self.rect.x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE)
        if self.rect.y < 0 or self.rect.y > SCREEN_HEIGHT - ENEMY_SIZE:
            self.rect.y = random.randint(0, SCREEN_HEIGHT - ENEMY_SIZE)

# Power-up classes
class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - POWERUP_SIZE)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - POWERUP_SIZE)

class SpeedBoost(PowerUp):
    def __init__(self):
        super().__init__()
        self.image.fill(ORANGE)

class ExtraTime(PowerUp):
    def __init__(self):
        super().__init__()
        self.image.fill(BLUE)

# Set up the player, items, enemies, and power-ups
player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

item_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
powerup_group = pygame.sprite.Group()

# Spawn functions
def spawn_item():
    item = Item()
    item_group.add(item)
    all_sprites.add(item)

def spawn_enemy():
    enemy = Enemy()
    enemy_group.add(enemy)
    all_sprites.add(enemy)

def spawn_powerup():
    powerup_type = random.choice([SpeedBoost, ExtraTime])
    powerup = powerup_type()
    powerup_group.add(powerup)
    all_sprites.add(powerup)

# Game loop
score = 0
level = 1
start_time = time.time()
level_start_time = time.time()

spawn_item()
spawn_enemy()
spawn_powerup()

running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update player position based on key press
    keys = pygame.key.get_pressed()
    player.update(keys)

    # Check for collisions with items
    collided_items = pygame.sprite.spritecollide(player, item_group, True)
    for item in collided_items:
        score += 1
        spawn_item()  # Spawn a new item after one is collected

    # Check for collisions with enemies
    if not player.invincible:
        collided_enemies = pygame.sprite.spritecollide(player, enemy_group, False)
        if collided_enemies:
            running = False  # Game Over

    # Check for collisions with power-ups
    collided_powerups = pygame.sprite.spritecollide(player, powerup_group, True)
    for powerup in collided_powerups:
        if isinstance(powerup, SpeedBoost):
            player.speed_boost = True
            player.speed_timer = time.time()  # Set speed boost timer
            player.speed = PLAYER_SPEED * 2  # Double the speed
        elif isinstance(powerup, ExtraTime):
            TIMER_LIMIT += 10  # Add extra 10 seconds to the game timer

    # Spawn new enemies and power-ups at intervals
    if random.random() < 0.01:
        spawn_enemy()
    if random.random() < 0.005:
        spawn_powerup()

    # Update enemies' positions
    enemy_group.update()

    # Timer check and level-up
    elapsed_time = time.time() - start_time
    level_time = time.time() - level_start_time

    if level_time > LEVEL_TIME_LIMIT:
        level += 1
        spawn_enemy()  # Increase enemy count
        spawn_powerup()  # Add more power-ups
        level_start_time = time.time()  # Reset level timer

    if elapsed_time > TIMER_LIMIT:
        running = False  # Game over after the timer runs out

    # Draw everything
    all_sprites.draw(screen)

    # Display score, level, and timer
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    level_text = font.render(f"Level: {level}", True, BLACK)
    screen.blit(level_text, (SCREEN_WIDTH - 150, 10))

    time_left = max(0, TIMER_LIMIT - int(elapsed_time))
    timer_text = font.render(f"Time: {time_left}s", True, BLACK)
    screen.blit(timer_text, (SCREEN_WIDTH - 150, 40))

    pygame.display.flip()
    clock.tick(60)

# Game Over screen
screen.fill(WHITE)
game_over_text = font.render(f"Game Over! Final Score: {score}", True, BLACK)
screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 20))

high_score = max(score, high_score)
high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
screen.blit(high_score_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 20))

# Save high score
with open(high_score_file, "w") as f:
    f.write(str(high_score))

pygame.display.flip()
pygame.time.wait(3000)

pygame.quit()
