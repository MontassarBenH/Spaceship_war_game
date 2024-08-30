import pygame
import random
import os
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spaceship War Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Load background image
current_dir = os.path.dirname(os.path.abspath(__file__))
background_img = pygame.image.load(os.path.join(current_dir, 'space_background.jpg'))
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# Load player image
player_image = pygame.image.load("spacecraft.png")
player_image = pygame.transform.scale(player_image, (60, 60))

# Load enemy spaceship image
enemy_spaceship_image = pygame.image.load("enemy_spaceship.png")
enemy_spaceship_image = pygame.transform.scale(enemy_spaceship_image, (70, 70))

# Load heart image for lives display
heart_img = pygame.image.load(os.path.join(current_dir, 'heart.png'))
heart_img = pygame.transform.scale(heart_img, (20, 20))

# Player settings
player_width, player_height = 50, 40
player_x, player_y = WIDTH // 2, HEIGHT - 60
player_speed = 5
player_bullet_level = 0 
player_lives = 5 

BASE_ENEMY_BULLET_SPEED = 2
BULLET_SPEED_INCREASE = 0.5
BULLET_SPEED_INCREASE_INTERVAL = 2
initial_enemies_in_wave = 0


# Game balance constants
BASE_ENEMY_HEALTH = 1
HEALTH_INCREASE_PER_WAVE = 0.5
MAX_ENEMY_HEALTH = 20
MIN_ENEMIES_PER_WAVE = 5
MAX_ENEMIES_PER_WAVE = 20
WAVE_INCREASE_INTERVAL = 5  
FRAME_RATE = 60 

# Modify these constants for game balance
BASE_ENEMY_HEALTH = 1
HEALTH_INCREASE_PER_WAVE = 0.5
MAX_ENEMY_HEALTH = 20

# Bullet settings
bullet_width, bullet_height = 5, 10
bullet_speed = 3
bullets = []

# New bullet power levels
BULLET_LEVELS = [
    {"damage": 1, "color": WHITE, "shape": "rectangle"},
    {"damage": 2, "color": (255, 255, 0), "shape": "triangle"},  # Yellow
    {"damage": 3, "color": (0, 255, 255), "shape": "circle"},    # Cyan
    {"damage": 4, "color": (255, 0, 255), "shape": "star"}       # Magenta
]

# Enemy settings
enemy_width, enemy_height = 50, 40
enemies = []
enemy_bullets = []
enemy_bullet_speed = 2
enemy_shoot_chance = 0.02
last_enemy_shot_time = 0
min_time_between_enemy_shots = 500

# Wave settings
current_wave = 1
enemies_per_wave = 10
enemy_health_multiplier = 1.5

# Power-up settings
power_ups = []
power_up_speed = 1
power_up_chance = 0.001

# Score
score = 0
font = pygame.font.Font(None, 36)

# Bullet cooldown
bullet_cooldown = 250  
last_bullet_time = pygame.time.get_ticks()



# Function to reset player position
def reset_player_position():
    global player_x, player_y
    player_x = WIDTH // 2
    player_y = HEIGHT - 60

# Function to draw player ship
def draw_player(surface, x, y):
    # Main body
    pygame.draw.polygon(surface, (100, 200, 100), [
        (x + player_width // 2, y),  
        (x + player_width * 3 // 4, y + player_height * 3 // 4),  
        (x + player_width, y + player_height),  
        (x + player_width * 3 // 4, y + player_height),  
        (x + player_width // 4, y + player_height),  
        (x, y + player_height),  
        (x + player_width // 4, y + player_height * 3 // 4),  
    ])
    
    # Cockpit
    pygame.draw.ellipse(surface, (150, 150, 255), 
                        (x + player_width // 4, y + player_height // 4, 
                         player_width // 2, player_height // 2))
    
    # Engine glow
    engine_glow = pygame.Surface((player_width, player_height // 2), pygame.SRCALPHA)
    pygame.draw.polygon(engine_glow, (255, 165, 0, 200), [
        (player_width // 4, player_height // 2),
        (player_width // 2, 0),
        (player_width * 3 // 4, player_height // 2)
    ])
    surface.blit(engine_glow, (x, y + player_height * 2 // 3))
    
    # Highlights
    pygame.draw.line(surface, (200, 255, 200), 
                     (x + player_width // 4, y + player_height // 2),
                     (x + player_width * 3 // 4, y + player_height // 2), 2)
    pygame.draw.line(surface, (200, 255, 200),
                     (x + player_width // 2, y + player_height // 4),
                     (x + player_width // 2, y + player_height * 3 // 4), 2)
    
def draw_bullet(surface, bullet):
    level = BULLET_LEVELS[bullet['level']]
    if level['shape'] == "rectangle":
        pygame.draw.rect(surface, level['color'], bullet['rect'])
    elif level['shape'] == "triangle":
        pygame.draw.polygon(surface, level['color'], [
            (bullet['rect'].centerx, bullet['rect'].top),
            (bullet['rect'].left, bullet['rect'].bottom),
            (bullet['rect'].right, bullet['rect'].bottom)
        ])
    elif level['shape'] == "circle":
        pygame.draw.circle(surface, level['color'], bullet['rect'].center, bullet['rect'].width // 2)
    elif level['shape'] == "star":
        points = []
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2
            points.append((
                bullet['rect'].centerx + int(math.cos(angle) * bullet['rect'].width / 2),
                bullet['rect'].centery + int(math.sin(angle) * bullet['rect'].height / 2)
            ))
            angle += math.pi / 5
            points.append((
                bullet['rect'].centerx + int(math.cos(angle) * bullet['rect'].width / 4),
                bullet['rect'].centery + int(math.sin(angle) * bullet['rect'].height / 4)
            ))
        pygame.draw.polygon(surface, level['color'], points)

def move_enemy_bullets(enemy_bullets, speed, delta_time):
    for bullet in enemy_bullets[:]:
        bullet.y += speed * delta_time
        if bullet.top > HEIGHT:
            enemy_bullets.remove(bullet)

# Function to create a new bullet
def create_bullet(x, y):
    return {
        'rect': pygame.Rect(x - bullet_width // 2, y - bullet_height // 2, bullet_width, bullet_height),
        'level': player_bullet_level,
    }

# Function to draw enemy ship
def draw_enemy(surface, x, y):
    
    pygame.draw.polygon(surface, (200, 100, 100), [
        (x + enemy_width // 2, y + enemy_height),  
        (x, y + enemy_height // 4),  
        (x + enemy_width // 4, y),  
        (x + enemy_width * 3 // 4, y),  
        (x + enemy_width, y + enemy_height // 4),  
    ])
    
    # Cockpit 
    pygame.draw.ellipse(surface, (255, 200, 200), 
                        (x + enemy_width // 4, y, 
                         enemy_width // 2, enemy_height // 2))
    
    # Wing details 
    pygame.draw.line(surface, (255, 150, 150),
                     (x, y + enemy_height // 4),
                     (x + enemy_width // 4, y + enemy_height // 2), 2)
    pygame.draw.line(surface, (255, 150, 150),
                     (x + enemy_width, y + enemy_height // 4),
                     (x + enemy_width * 3 // 4, y + enemy_height // 2), 2)
    
    # Engine glow 
    engine_glow = pygame.Surface((enemy_width // 2, enemy_height // 4), pygame.SRCALPHA)
    pygame.draw.ellipse(engine_glow, (255, 100, 100, 150), 
                        (0, 0, enemy_width // 2, enemy_height // 4))
    surface.blit(engine_glow, (x + enemy_width // 4, y))

# Function to create enemy formation using game balance constants
def create_enemy_formation(num_enemies, wave):
    global initial_enemies_in_wave
    formation = []

    # Determine the number of rows and columns based on the number of enemies
    max_enemies_per_row = min(8, (WIDTH - 100) // (enemy_width + 20))

    # Calculate the number of rows needed
    num_rows = math.ceil(num_enemies / max_enemies_per_row)

    # Calculate the vertical spacing between rows
    vertical_spacing = min(80, (HEIGHT * 2/3) // (num_rows + 1))

    # Add special enemies for waves that are multiples of 5
    if wave % 5 == 0:
        num_enemies += 2

    for i in range(num_enemies):
        row = i // max_enemies_per_row
        col = i % max_enemies_per_row

        # Calculate x position (spread across the entire width)
        total_width = WIDTH - 100  # Leave some margin on both sides
        x_spacing = total_width / (max_enemies_per_row + 1)
        x = 50 + (col + 1) * x_spacing - enemy_width / 2

        # Calculate y position (distribute rows evenly across the top 2/3 of the screen)
        y = 50 + row * vertical_spacing

        # Calculate enemy health based on wave and health constants
        enemy_health = min(
            BASE_ENEMY_HEALTH + (wave - 1) * HEALTH_INCREASE_PER_WAVE,
            MAX_ENEMY_HEALTH
        )

        # Create an enemy and add it to the formation
        enemy = {
            'rect': pygame.Rect(x, y, enemy_width, enemy_height),
            'health': math.ceil(enemy_health)
        }

        # Make the last two enemies special for waves that are multiples of 5
        if wave % 5 == 0 and i >= num_enemies - 2:
            enemy['health'] = math.ceil(enemy_health * 1.5)
            enemy['special'] = True

        formation.append(enemy)

    initial_enemies_in_wave = len(formation)
    return formation

def get_enemy_bullet_speed(wave, remaining_enemies):
    global initial_enemies_in_wave
    
    # Slower base speed increase
    base_speed = BASE_ENEMY_BULLET_SPEED + (wave - 1) * 0.1
    
    # More restrictive cap on base speed
    max_base_speed = BASE_ENEMY_BULLET_SPEED * 1.5
    base_speed = min(base_speed, max_base_speed)
    
    # Calculate the enemy ratio
    enemy_ratio = remaining_enemies / initial_enemies_in_wave if initial_enemies_in_wave > 0 else 1
    
    # Smaller speed increase based on eliminated enemies
    speed_increase = (1 - enemy_ratio) * 0.3
    
    # Combine base speed and increase, with a lower maximum cap
    final_speed = min(base_speed + speed_increase, BASE_ENEMY_BULLET_SPEED * 1.8)
    
    return final_speed

# In the main game loop, update the wave transition logic:
if len(enemies) == 0:
    wave_transition = True
    transition_timer = pygame.time.get_ticks()
    print(f"Wave {current_wave} completed. Preparing next wave...")

# In the wave transition part of the main game loop:
if wave_transition:
    if pygame.time.get_ticks() - transition_timer > 3000:  # 3 second delay
        current_wave += 1
        if current_wave % WAVE_INCREASE_INTERVAL == 0:
            enemies_per_wave = min(enemies_per_wave + 1, MAX_ENEMIES_PER_WAVE)
        enemies = create_enemy_formation(enemies_per_wave, current_wave)
        initial_enemies_in_wave = len(enemies)
        wave_transition = False
        wave_start_time = pygame.time.get_ticks()
        enemy_bullets.clear()
        
        # Update player speed
        player_speed = 5 + (current_wave - 1) * 0.2  # Increase speed slightly each wave
        player_speed = min(player_speed, 8)  # Cap at a maximum speed
        
        print(f"Wave {current_wave} started with {len(enemies)} enemies")

def draw_power_up(surface, power_up):
    rect = power_up['rect']
    power_up_type = power_up['type']
    
    if power_up_type == 'bullet_upgrade':
        # Draw a star shape for bullet upgrade
        color = (255, 255, 0)  
        points = []
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2
            outer_point = (
                rect.centerx + int(rect.width / 2 * math.cos(angle)),
                rect.centery + int(rect.height / 2 * math.sin(angle))
            )
            points.append(outer_point)
            
            inner_angle = angle + math.pi / 5
            inner_point = (
                rect.centerx + int(rect.width / 4 * math.cos(inner_angle)),
                rect.centery + int(rect.height / 4 * math.sin(inner_angle))
            )
            points.append(inner_point)
        
        pygame.draw.polygon(surface, color, points)
        
        # Draw a small circle in the center
        pygame.draw.circle(surface, (255, 165, 0), rect.center, rect.width // 6)
        
    elif power_up_type == 'speed':
        # Draw a lightning bolt for speed upgrade
        color = (0, 191, 255)  
        
        bolt_points = [
            (rect.centerx - rect.width // 4, rect.top),
            (rect.centerx + rect.width // 4, rect.centery - rect.height // 4),
            (rect.centerx, rect.centery),
            (rect.centerx + rect.width // 4, rect.bottom),
            (rect.centerx - rect.width // 4, rect.centery + rect.height // 4),
            (rect.centerx, rect.centery)
        ]
        
        pygame.draw.polygon(surface, color, bolt_points)
        
        # Draw a white outline
        pygame.draw.lines(surface, (255, 255, 255), False, bolt_points, 2)

    # Draw a pulsating glow effect
    glow_size = int(rect.width * (1 + 0.2 * math.sin(pygame.time.get_ticks() * 0.01)))
    glow_rect = pygame.Rect(0, 0, glow_size, glow_size)
    glow_rect.center = rect.center
    glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
    pygame.draw.circle(glow_surface, (*color, 100), (glow_size // 2, glow_size // 2), glow_size // 2)
    surface.blit(glow_surface, glow_rect)

# Function to spawn a power-up
def spawn_power_up():
    power_up_type = random.choice(['bullet_upgrade', 'speed'])
    x = random.randint(0, WIDTH - 20)
    power_ups.append({
        'rect': pygame.Rect(x, -20, 20, 20),
        'type': power_up_type
    })

# Main game loop
clock = pygame.time.Clock()
running = True
game_over = False
current_wave = 1
enemies_per_wave = MIN_ENEMIES_PER_WAVE
enemies = create_enemy_formation(enemies_per_wave, current_wave)
initial_enemies_in_wave = len(enemies)  
wave_transition = False
transition_timer = 0
wave_start_time = pygame.time.get_ticks()

while running:
    
    clock.tick(FRAME_RATE)
    screen.fill(BLACK)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                # Reset game state
                player_lives = 5
                player_bullet_level = 0
                score = 0
                current_wave = 1
                enemies_per_wave = MIN_ENEMIES_PER_WAVE
                enemies = create_enemy_formation(enemies_per_wave, current_wave)
                initial_enemies_in_wave = len(enemies)  # Add this line
                bullets.clear()
                enemy_bullets.clear()
                power_ups.clear()
                reset_player_position()
                game_over = False
                wave_transition = False
                transition_timer = 0
                wave_start_time = pygame.time.get_ticks()

    if not game_over:
        # Player input handling 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x - player_speed > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x + player_speed < WIDTH - player_width:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y - player_speed > HEIGHT // 2:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y + player_speed < HEIGHT - player_height:
            player_y += player_speed

        # Shooting 
        current_time = pygame.time.get_ticks()

        enemy_shoot_chance = 0.02 / math.sqrt(current_wave)
        if random.random() < enemy_shoot_chance and current_time - last_enemy_shot_time > min_time_between_enemy_shots:
            enemy_bullet = pygame.Rect(enemy['rect'].centerx - bullet_width // 2, 
                                    enemy['rect'].bottom, bullet_width, bullet_height)
            enemy_bullets.append(enemy_bullet)
            last_enemy_shot_time = current_time
        
        if keys[pygame.K_SPACE] and current_time - last_bullet_time > bullet_cooldown:
            new_bullet = create_bullet(player_x + player_width // 2, player_y)
            bullets.append(new_bullet)
            last_bullet_time = current_time

        # Move and remove off-screen bullets
        bullets = [bullet for bullet in bullets if bullet['rect'].bottom > 0]
        for bullet in bullets:
            bullet['rect'].y -= bullet_speed
            if bullet['rect'].bottom < 0:
                bullets.remove(bullet)

        if not game_over and not wave_transition:
            # Enemy behavior
            for enemy in enemies[:]:
                # Calculate the center of the playable area
                center_y = HEIGHT // 4

                # Move enemies towards the center with some randomness
                if enemy['rect'].centery < center_y:
                    enemy['rect'].y += random.randint(0, 2)
                elif enemy['rect'].centery > center_y:
                    enemy['rect'].y -= random.randint(0, 2)
                
                # Add slight horizontal movement
                enemy['rect'].x += random.randint(-1, 1)
                
                # Define the playable area for enemies
                playable_height = HEIGHT * 2 // 3  
                enemy_area = pygame.Rect(0, 0, WIDTH, playable_height)
                
                # Keep enemies within the defined playable area
                enemy['rect'].clamp_ip(enemy_area)
                
                # Enemy shooting
                if random.random() < enemy_shoot_chance:
                    enemy_bullet = pygame.Rect(enemy['rect'].centerx - bullet_width // 2, 
                                               enemy['rect'].bottom, bullet_width, bullet_height)
                    enemy_bullets.append(enemy_bullet)

                
                # Move and remove off-screen enemy bullets
                for bullet in enemy_bullets[:]:
                    bullet_speed = get_enemy_bullet_speed(current_wave, len(enemies))
                    bullet.y += bullet_speed
                    if bullet.top > HEIGHT:
                        enemy_bullets.remove(bullet)


            # Collision detection
            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            
            # Player bullet - enemy collision
            for enemy in enemies[:]:
                for bullet in bullets[:]:
                    if enemy['rect'].colliderect(bullet['rect']):
                        enemy['health'] -= BULLET_LEVELS[bullet['level']]['damage']
                        bullets.remove(bullet)
                        if enemy['health'] <= 0:
                            enemies.remove(enemy)
                            score += 10 * current_wave
                        break

            # Player - enemy collision
            for enemy in enemies[:]:
                if player_rect.colliderect(enemy['rect']):
                    player_lives -= 1
                    enemies.remove(enemy)
                    reset_player_position()
                    if player_lives <= 0:
                        game_over = True
                    break

            # Player - enemy bullet collision
            for bullet in enemy_bullets[:]:
                if player_rect.colliderect(bullet):
                    player_lives -= 1
                    enemy_bullets.remove(bullet)
                    reset_player_position()
                    if player_lives <= 0:
                        game_over = True
                    break

            # Check for wave completion
            if len(enemies) == 0:
                wave_transition = True
                transition_timer = pygame.time.get_ticks()
                print(f"Wave {current_wave} completed. Preparing next wave...")

        else:
            # Wave transition
            if pygame.time.get_ticks() - transition_timer > 3000:  # 3 second delay
                current_wave += 1
                if current_wave % WAVE_INCREASE_INTERVAL == 0:
                    enemies_per_wave = min(enemies_per_wave + 1, MAX_ENEMIES_PER_WAVE)
                enemies = create_enemy_formation(enemies_per_wave, current_wave)
                wave_transition = False
                wave_start_time = pygame.time.get_ticks()
                print(f"Wave {current_wave} started with {len(enemies)} enemies")  # Debug print

        # Power-up logic
        for power_up in power_ups[:]:
            power_up['rect'].y += power_up_speed
            if power_up['rect'].y > HEIGHT:
                power_ups.remove(power_up)
            elif player_rect.colliderect(power_up['rect']):
                if power_up['type'] == 'bullet_upgrade':
                    player_bullet_level = min(player_bullet_level + 1, len(BULLET_LEVELS) - 1)
                elif power_up['type'] == 'speed':
                    player_speed = min(player_speed + 1, 10) 
                power_ups.remove(power_up)

        # Spawn power-ups
        if random.random() < power_up_chance:
            spawn_power_up()

    # Drawing
    screen.blit(background_img, (0, 0))
    
    if not game_over:
        # Draw player
        screen.blit(player_image, (player_x, player_y))
        
        # Draw bullets
        for bullet in bullets:
            draw_bullet(screen, bullet)
        
        # Draw enemies
        for enemy in enemies:
            screen.blit(enemy_spaceship_image, (enemy['rect'].x, enemy['rect'].y))
        
        # Draw enemy bullets
        for bullet in enemy_bullets:
            pygame.draw.rect(screen, RED, bullet)
        
        # Draw power-ups
        for power_up in power_ups:
            draw_power_up(screen, power_up)

        # Draw HUD
        score_text = font.render(f"Score: {score}", True, WHITE)
        wave_text = font.render(f"Wave: {current_wave}", True, WHITE)
        enemy_count_text = font.render(f"Enemies: {len(enemies)}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(wave_text, (10, 50))
        screen.blit(enemy_count_text, (10, 90))

        # Draw lives
        for i in range(player_lives):
            screen.blit(heart_img, (WIDTH - 30 - i * 25, 10))

        # Draw wave transition message
        if wave_transition:
            if pygame.time.get_ticks() - transition_timer > 1000:  # 1 second delay
                current_wave += 1
                if current_wave % WAVE_INCREASE_INTERVAL == 0:
                    enemies_per_wave = min(enemies_per_wave + 1, MAX_ENEMIES_PER_WAVE)
                enemies = create_enemy_formation(enemies_per_wave, current_wave)
                initial_enemies_in_wave = len(enemies)  # Add this line
                wave_transition = False
                wave_start_time = pygame.time.get_ticks()
                print(f"Wave {current_wave} started with {len(enemies)} enemies")  # Debug print

    else:
        # Game Over screen
        game_over_text = font.render("GAME OVER", True, RED)
        final_score_text = font.render(f"Final Score: {score}", True, WHITE)
        restart_text = font.render("Press 'R' to Restart", True, WHITE)
        initial_enemies_in_wave = len(enemies)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
        screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))

    pygame.display.flip()

pygame.quit()

print("Game loop ended. Final game state:")
print(f"Final score: {score}")
print(f"Final wave: {current_wave}")
print(f"Remaining enemies: {len(enemies)}")