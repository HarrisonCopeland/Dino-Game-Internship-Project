import pygame
from random import randint

# ----------------------------------------------------------------
# Initialize Pygame
# ----------------------------------------------------------------
pygame.init()
screen = pygame.display.set_mode((800, 400))
display_surface = pygame.Surface((800, 400)) # Used for screen shake
pygame.display.set_caption("Dino Game: Boss Edition")
clock = pygame.time.Clock()
running = True

# --- Game State ---
is_playing = 0  # 0: Menu, 1: Normal, 3: Pause, 4: Controls, 5/6: Options, 7: Leaderboard, 8: Boss Intro, 9: Boss Fight, 10: Boss Defeated
GROUND_Y = 375
FLOOR_HEIGHT = 600
JUMP_GRAVITY_START_SPEED = -20
players_gravity_speed = 0
score = 0
high_score = 0
frame_count = 0
egg_speed = 5
lives = 3
hit_cooldown = 0
double_jump = False
game_mode = 0
score_saved = False
show_hitboxes = False 
screen_shake = 0

BITE_DISTANCE = 60

# --- Boss State ---
boss_active = False
boss_defeated = False
boss_state = 'hidden' # hidden, idle, jumping, telegraph_landing, smash, telegraph_shockwave, shockwave
boss_timer = 0
boss_cycles = 0
intro_timer = 0
boss_facing_left = True

boss_rect = pygame.Rect(400, -200, 150, 150)
landing_zone = pygame.Rect(0, GROUND_Y - 20, 230, 20) # INCREASED: Width expanded from 150 to 230 for bigger smash radius
shockwave_zone_l = pygame.Rect(0, GROUND_Y - 40, 0, 40)
shockwave_zone_r = pygame.Rect(0, GROUND_Y - 40, 0, 40)

# --- Fonts ---
game_font = pygame.font.Font(pygame.font.get_default_font(), 30)
large_font = pygame.font.Font(pygame.font.get_default_font(), 50)
leaderboard_font = pygame.font.Font(pygame.font.get_default_font(), 25)

# ----------------------------------------------------------------
# Helper loaders
# ----------------------------------------------------------------
def load_scaled(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except FileNotFoundError:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((255, 0, 0, 100))
        return surf

def load_bg(path):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (800, 400))
    except FileNotFoundError:
        surf = pygame.Surface((800, 400))
        surf.fill("Skyblue")
        return surf

# ----------------------------------------------------------------
# Level Assets
# ----------------------------------------------------------------
BACKGROUND_SURF = load_bg("graphics/level/mainbackround.png")

try:
    _floor_raw = pygame.image.load("graphics/level/floorground.png").convert_alpha()
    GROUND_SURF = pygame.transform.scale(_floor_raw, (800, FLOOR_HEIGHT))
except FileNotFoundError:
    GROUND_SURF = pygame.Surface((800, FLOOR_HEIGHT))
    GROUND_SURF.fill("Brown")

# --- Gorilla Boss Assets ---
BOSS_SIZE = (150, 150)
BOSS_SPRITES = {
    'idle1': load_scaled("graphics/gorillaboss/gorillaidle.png", BOSS_SIZE),
    'idle2': load_scaled("graphics/gorillaboss/gorillaidle2.png", BOSS_SIZE),
    'jump_prep': load_scaled("graphics/gorillaboss/gorilla_about_to_jump.png", BOSS_SIZE),
    'falling': load_scaled("graphics/gorillaboss/fallinggorilla.png", BOSS_SIZE),
    'land': load_scaled("graphics/gorillaboss/gorillaland.png", BOSS_SIZE),
    'smash': load_scaled("graphics/gorillaboss/gorillasmash.png", BOSS_SIZE),
}

# --- Player Sprites ---
PLAYER_SIZE = (60, 70)
PLAYER_WALK = [
    load_scaled("graphics/player/player_walk_1.png", PLAYER_SIZE),
    load_scaled("graphics/player/player_walk_2.png", PLAYER_SIZE),
]
PLAYER_STAND = load_scaled("graphics/player/player_stand.png", PLAYER_SIZE)
PLAYER_JUMP  = load_scaled("graphics/player/player_jump.png",  PLAYER_SIZE)

# --- Enemy Loaders ---
ENEMY_SIZE = (65, 65)
def load_enemy(path):
    img = load_scaled(path, ENEMY_SIZE)
    return pygame.transform.flip(img, True, False)

ENEMY_FRAMES = [
    load_enemy("graphics/enemyground/enemy1.png"),
    load_enemy("graphics/enemyground/enemy2.png"),
    load_enemy("graphics/enemyground/enemy3.png"),
]
ENEMY_BITE_FRAMES = [
    load_enemy("graphics/enemyground/enemybite1.png"),
    load_enemy("graphics/enemyground/enemybite2.png"),
    load_enemy("graphics/enemyground/enemybite3.png"),
]

FLYING_ENEMY_SIZE = (55, 55)
def load_flying_enemy(path):
    img = load_scaled(path, FLYING_ENEMY_SIZE)
    return pygame.transform.flip(img, True, False)

FLYING_ENEMY_FRAMES = [
    load_flying_enemy("graphics/flyingenemy/flyingenemy1.png"),
    load_flying_enemy("graphics/flyingenemy/flyingenemy2.png"),
]
FLYING_ENEMY_HEIGHT = GROUND_Y - 100

HEART_SURF = load_scaled("graphics/level/heart.png", (32, 32))

POWERUP_SIZE = (40, 40)
POWERUP_SURF = load_scaled("graphics/level/powerup2.png", POWERUP_SIZE)
powerup_rect = POWERUP_SURF.get_rect(bottomleft=(900, GROUND_Y))
powerup_active = False
next_powerup_score = 50

# ----------------------------------------------------------------
# Menu Assets
# ----------------------------------------------------------------
game_name = large_font.render('Dino Game', True, (255, 255, 255))
game_name_rect = game_name.get_rect(center=(400, 80))

start_btn = load_scaled("graphics/level/start.png", (96, 48))
start_rect = start_btn.get_rect(center=(400, 185))

controls_btn = load_scaled("graphics/level/controls.png", (144, 48))
controls_rect = controls_btn.get_rect(midright=(390, 255))

options_btn = load_scaled("graphics/level/options.png", (144, 48))
options_rect = options_btn.get_rect(midleft=(410, 255))

leaderboard_btn = load_scaled("graphics/level/leaderboard.png", (192, 48))
leaderboard_btn_rect = leaderboard_btn.get_rect(midtop=(400, 295))

back_btn = load_scaled("graphics/level/back.png", (96, 48))
back_rect = back_btn.get_rect(bottomleft=(20, 390))

controls_message = game_font.render('SPACE / Click = Jump', True, (13, 57, 118))
controls_message_rect = controls_message.get_rect(center=(400, 100))
controls_message2 = game_font.render('ESC = Pause', True, (13, 57, 118))
controls_message2_rect = controls_message2.get_rect(center=(400, 150))
controls_message3 = game_font.render('Pink powerup = double jump', True, (13, 57, 118))
controls_message3_rect = controls_message3.get_rect(center=(400, 200))

options_message = game_font.render('Hard Mode (1 life):', True, (13, 57, 118))
options_message_rect = options_message.get_rect(midleft=(50, 200))

on_btn = load_scaled("graphics/level/on.png", (96, 48))
on_rect = on_btn.get_rect(midleft=options_message_rect.midright)

off_btn = load_scaled("graphics/level/off.png", (96, 48))
off_rect = off_btn.get_rect(midleft=options_message_rect.midright)

leaderboard_title = large_font.render('Leaderboard', True, (13, 57, 118))
leaderboard_title_rect = leaderboard_title.get_rect(midtop=(400, 25))

game_pause = large_font.render('Paused', True, (255, 255, 255))
game_pause_rect = game_pause.get_rect(center=(400, 100))

resume_btn = load_scaled("graphics/level/resume.png", (144, 48))
resume_rect = resume_btn.get_rect(center=(400, 180))

exit_btn = load_scaled("graphics/level/exit.png", (96, 48))
exit_rect = exit_btn.get_rect(center=(400, 250))

pause_btn = load_scaled("graphics/level/pause.png", (40, 40))
pause_rect = pause_btn.get_rect(topright=(790, 10))

not_pause_btn = load_scaled("graphics/level/not_pause.png", (40, 40))
not_pause_rect = not_pause_btn.get_rect(topright=(790, 10))

# ----------------------------------------------------------------
# Functions
# ----------------------------------------------------------------
player_surf = PLAYER_STAND
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))
walk_frame_index = 0
obstacle_list = []
bg_x = 0

obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

def display_score():
    score_surf = game_font.render(f'Score: {int(score)}', True, 'Black')
    score_rect = score_surf.get_rect(topright=(780, 15))
    pygame.draw.rect(display_surface, "#c0e8ec", score_rect.inflate(16, 8), border_radius=6)
    display_surface.blit(score_surf, score_rect)

def draw_lives(lives_count):
    for i in range(lives_count):
        display_surface.blit(HEART_SURF, (10 + i * 36, 10))

def player_animation():
    global player_surf, walk_frame_index
    if player_rect.bottom < GROUND_Y:
        player_surf = PLAYER_JUMP
    else:
        if frame_count % 10 == 0:
            walk_frame_index = (walk_frame_index + 1) % len(PLAYER_WALK)
        player_surf = PLAYER_WALK[walk_frame_index]
        
    keys = pygame.key.get_pressed()
    if is_playing == 9 and (keys[pygame.K_a] or keys[pygame.K_LEFT]):
        player_surf = pygame.transform.flip(player_surf, True, False)

def obstacle_movement(obstacle_list):
    if obstacle_list:
        for obstacle in obstacle_list:
            obstacle["rect"].x -= int(egg_speed)
            if obstacle["type"] == "ground":
                distance_to_player = obstacle["rect"].left - player_rect.right
                obstacle["biting"] = 0 <= distance_to_player <= BITE_DISTANCE
                if frame_count % 8 == 0:
                    frames = ENEMY_BITE_FRAMES if obstacle["biting"] else ENEMY_FRAMES
                    obstacle["frame_index"] = (obstacle["frame_index"] + 1) % len(frames)
                frames = ENEMY_BITE_FRAMES if obstacle["biting"] else ENEMY_FRAMES
                surf = frames[obstacle["frame_index"]]
                obstacle["rect"].bottom = GROUND_Y
                display_surface.blit(surf, obstacle["rect"])
                if show_hitboxes:
                    pygame.draw.rect(display_surface, (0, 255, 0), obstacle["rect"], 2)
            else:
                if frame_count % 10 == 0:
                    obstacle["frame_index"] = (obstacle["frame_index"] + 1) % len(FLYING_ENEMY_FRAMES)
                surf = FLYING_ENEMY_FRAMES[obstacle["frame_index"]]
                display_surface.blit(surf, obstacle["rect"])
                if show_hitboxes:
                    pygame.draw.rect(display_surface, (0, 0, 255), obstacle["rect"], 2)

        return [o for o in obstacle_list if o["rect"].right > -50]
    return []

def collisions(player, obstacles):
    for obstacle in obstacles:
        if player.colliderect(obstacle["rect"]):
            return True
    return False

def reset_game():
    global players_gravity_speed, score, frame_count, egg_speed
    global obstacle_list, bg_x, lives, hit_cooldown, double_jump
    global powerup_active, next_powerup_score, score_saved
    global boss_active, boss_defeated, boss_state, boss_cycles, boss_facing_left

    players_gravity_speed = 0
    score = 0
    frame_count = 0
    egg_speed = 5
    obstacle_list = []
    bg_x = 0
    hit_cooldown = 0
    double_jump = False
    powerup_active = False
    next_powerup_score = 50
    score_saved = False
    lives = 1 if game_mode == 1 else 3
    player_rect.bottomleft = (25, GROUND_Y)
    
    boss_active = False
    boss_defeated = False
    boss_state = 'hidden'
    boss_cycles = 0
    boss_facing_left = True

def handle_player_death():
    global lives, hit_cooldown, double_jump, is_playing, high_score, score_saved
    double_jump = False
    lives -= 1
    hit_cooldown = 60
    if lives <= 0:
        if int(score) > int(high_score): high_score = score
        is_playing = 0

def start_boss_fight():
    global is_playing, obstacle_list, intro_timer, boss_active
    is_playing = 8
    boss_active = True
    obstacle_list.clear()
    intro_timer = pygame.time.get_ticks()

def get_current_boss_sprite():
    global boss_facing_left
    
    # CHANGED: Turn towards character before jumping (tracks player while idle)
    if boss_state == 'idle':
        boss_facing_left = player_rect.centerx < boss_rect.centerx

    if boss_state == 'idle':
        surf = BOSS_SPRITES['idle1'] if (frame_count // 15) % 2 == 0 else BOSS_SPRITES['idle2']
    elif boss_state == 'jumping':
        surf = BOSS_SPRITES['jump_prep']
    elif boss_state == 'smash':
        surf = BOSS_SPRITES['falling']
    elif boss_state == 'telegraph_shockwave':
        surf = BOSS_SPRITES['smash']
    elif boss_state == 'shockwave':
        surf = BOSS_SPRITES['land']
    else:
        surf = BOSS_SPRITES['idle1']
        
    # Flip logic based on perspective tracking orientation
    if not boss_facing_left:
        surf = pygame.transform.flip(surf, True, False)
    return surf

# -------------- Main Game Loop -------------------------------
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if is_playing in [1, 9]:  
            mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                show_hitboxes = not show_hitboxes

            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or \
               (event.type == pygame.MOUSEBUTTONDOWN and not pause_rect.collidepoint(mouse_pos)):
                if player_rect.bottom >= GROUND_Y:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                elif double_jump:
                    players_gravity_speed = JUMP_GRAVITY_START_SPEED
                    double_jump = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                is_playing = 3
            if event.type == pygame.MOUSEBUTTONDOWN and pause_rect.collidepoint(mouse_pos):
                is_playing = 3

            if event.type == obstacle_timer and is_playing == 1:
                roll = randint(0, 2)
                if roll < 2:
                    rect = ENEMY_FRAMES[0].get_rect(bottomleft=(randint(850, 1050), GROUND_Y))
                    obstacle_list.append({"type": "ground", "rect": rect, "frame_index": 0, "biting": False, "passed": False})
                else:
                    rect = FLYING_ENEMY_FRAMES[0].get_rect(bottomleft=(randint(850, 1050), FLYING_ENEMY_HEIGHT))
                    obstacle_list.append({"type": "flying", "rect": rect, "frame_index": 0, "biting": False, "passed": False})

        elif is_playing == 0:
            mouse_pos = pygame.mouse.get_pos()
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE) or \
               (event.type == pygame.MOUSEBUTTONDOWN and start_rect.collidepoint(mouse_pos)):
                reset_game()
                is_playing = 1
            if event.type == pygame.MOUSEBUTTONDOWN and controls_rect.collidepoint(mouse_pos): is_playing = 4
            if event.type == pygame.MOUSEBUTTONDOWN and options_rect.collidepoint(mouse_pos): is_playing = 6 if game_mode == 1 else 5
            if event.type == pygame.MOUSEBUTTONDOWN and leaderboard_btn_rect.collidepoint(mouse_pos): is_playing = 7

        elif is_playing == 3: 
            mouse_pos = pygame.mouse.get_pos()
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or \
               (event.type == pygame.MOUSEBUTTONDOWN and resume_rect.collidepoint(mouse_pos)) or \
               (event.type == pygame.MOUSEBUTTONDOWN and not_pause_rect.collidepoint(mouse_pos)):
                is_playing = 1 if not boss_active else 9
            elif event.type == pygame.MOUSEBUTTONDOWN and exit_rect.collidepoint(mouse_pos):
                if int(score) > int(high_score): high_score = score
                is_playing = 0

        elif is_playing in [4, 5, 6, 7]:
            mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN and back_rect.collidepoint(mouse_pos):
                is_playing = 0
            if is_playing == 5 and event.type == pygame.MOUSEBUTTONDOWN and off_rect.collidepoint(mouse_pos):
                game_mode = 1; is_playing = 6
            if is_playing == 6 and event.type == pygame.MOUSEBUTTONDOWN and on_rect.collidepoint(mouse_pos):
                game_mode = 0; is_playing = 5

    # ---------------- Playing Mode (Normal) ----------------
    if is_playing == 1:
        frame_count += 1
        score += 0.05
        egg_speed = 5 + (score * 0.05)

        if score >= 100 and not boss_active and not boss_defeated:
            start_boss_fight()

        bg_x -= egg_speed * 0.5
        if bg_x <= -800: bg_x = 0
        
        display_surface.blit(BACKGROUND_SURF, (int(bg_x), 0))
        display_surface.blit(BACKGROUND_SURF, (int(bg_x) + 800, 0))
        display_surface.blit(GROUND_SURF, (0, GROUND_Y))
        display_surface.blit(pause_btn, pause_rect)
        draw_lives(lives)

        if score >= next_powerup_score and not powerup_active:
            powerup_active = True
            powerup_rect.bottomleft = (900, GROUND_Y)
            next_powerup_score += 50

        if powerup_active:
            powerup_rect.x -= int(egg_speed)
            display_surface.blit(POWERUP_SURF, powerup_rect)
            if powerup_rect.right < 0: powerup_active = False
            if player_rect.colliderect(powerup_rect):
                double_jump = True
                powerup_active = False

        obstacle_list = obstacle_movement(obstacle_list)
        for obstacle in obstacle_list:
            if not obstacle.get("passed", False) and obstacle["rect"].right < player_rect.left:
                obstacle["passed"] = True
                score += 10

        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        if player_rect.bottom > GROUND_Y:
            player_rect.bottom = GROUND_Y
            players_gravity_speed = 0

        player_animation()

        if hit_cooldown > 0:
            player_surf.set_alpha(128)
            hit_cooldown -= 1
        else:
            player_surf.set_alpha(255)
            
        display_surface.blit(player_surf, player_rect)
        if show_hitboxes: pygame.draw.rect(display_surface, (255, 0, 0), player_rect.inflate(-10, -10), 2)

        if collisions(player_rect.inflate(-10, -10), obstacle_list) and hit_cooldown == 0:
            handle_player_death()

        display_score()

    # ---------------- Boss Intro / Countdown ----------------
    elif is_playing == 8:
        frame_count += 1
        display_surface.blit(BACKGROUND_SURF, (int(bg_x), 0))
        display_surface.blit(BACKGROUND_SURF, (int(bg_x) + 800, 0))
        display_surface.blit(GROUND_SURF, (0, GROUND_Y))
        display_surface.blit(player_surf, player_rect)
        draw_lives(lives)
        display_score()

        current_time = pygame.time.get_ticks()
        elapsed = current_time - intro_timer

        overlay = pygame.Surface((800, 400), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        display_surface.blit(overlay, (0, 0))

        if elapsed < 3000:
            boss_msg = large_font.render('BOSS FIGHT', True, "Red")
            display_surface.blit(boss_msg, boss_msg.get_rect(center=(400, 150)))
            ctrl_msg = game_font.render('(A = Left | D = Right | SPACE = Jump)', True, "White")
            display_surface.blit(ctrl_msg, ctrl_msg.get_rect(center=(400, 200)))
        elif elapsed < 4000:
            num = large_font.render('3', True, "White")
            display_surface.blit(num, num.get_rect(center=(400, 200)))
        elif elapsed < 5000:
            num = large_font.render('2', True, "White")
            display_surface.blit(num, num.get_rect(center=(400, 200)))
        elif elapsed < 6000:
            num = large_font.render('1', True, "White")
            display_surface.blit(num, num.get_rect(center=(400, 200)))
        elif elapsed < 7000:
            screen_shake = 10
            num = large_font.render('GO!', True, "Red")
            display_surface.blit(num, num.get_rect(center=(400, 200)))
            
            boss_rect.centerx = 400
            boss_rect.y += 15 
            if boss_rect.bottom >= GROUND_Y:
                boss_rect.bottom = GROUND_Y
            display_surface.blit(BOSS_SPRITES['land'], boss_rect)
        else:
            is_playing = 9
            boss_state = 'idle'
            boss_timer = pygame.time.get_ticks()
            boss_cycles = 0

    # ---------------- Boss Fight Game Loop ----------------
    elif is_playing == 9:
        frame_count += 1
        display_surface.blit(BACKGROUND_SURF, (int(bg_x), 0))
        display_surface.blit(BACKGROUND_SURF, (int(bg_x) + 800, 0))
        display_surface.blit(GROUND_SURF, (0, GROUND_Y))
        display_surface.blit(pause_btn, pause_rect)
        draw_lives(lives)
        display_score()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: player_rect.x -= 6
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: player_rect.x += 6

        if player_rect.left < 0: player_rect.left = 0
        if player_rect.right > 800: player_rect.right = 800

        players_gravity_speed += 1
        player_rect.y += players_gravity_speed
        if player_rect.bottom > GROUND_Y:
            player_rect.bottom = GROUND_Y
            players_gravity_speed = 0

        player_animation()

        if hit_cooldown > 0:
            player_surf.set_alpha(128)
            hit_cooldown -= 1
        else:
            player_surf.set_alpha(255)
        display_surface.blit(player_surf, player_rect)
        if show_hitboxes: pygame.draw.rect(display_surface, (255, 0, 0), player_rect.inflate(-10, -10), 2)

        # --- Boss AI State Machine ---
        current_time = pygame.time.get_ticks()
        flicker_on = (current_time // 100) % 2 == 0

        if boss_state == 'idle':
            display_surface.blit(get_current_boss_sprite(), boss_rect)
            if current_time - boss_timer > 1500:
                boss_state = 'jumping'
                boss_timer = current_time

        elif boss_state == 'jumping':
            boss_rect.y -= 15
            display_surface.blit(get_current_boss_sprite(), boss_rect)
            if boss_rect.bottom < 0:
                boss_state = 'telegraph_landing'
                boss_timer = current_time
                landing_zone.centerx = player_rect.centerx
                
                if landing_zone.left < 0: landing_zone.left = 0
                if landing_zone.right > 800: landing_zone.right = 800

        elif boss_state == 'telegraph_landing':
            if flicker_on:
                pygame.draw.rect(display_surface, (255, 0, 0), landing_zone, 3)

            if current_time - boss_timer > 1200:
                boss_state = 'smash'
                boss_rect.centerx = landing_zone.centerx
                boss_rect.bottom = 0

        elif boss_state == 'smash':
            boss_rect.y += 25
            display_surface.blit(get_current_boss_sprite(), boss_rect)
            if boss_rect.bottom >= GROUND_Y:
                boss_rect.bottom = GROUND_Y
                screen_shake = 15
                boss_state = 'telegraph_shockwave'
                boss_timer = current_time
                
                # CHANGED: Now evaluates the newly resized, larger landing smash radius box
                if player_rect.colliderect(landing_zone) and hit_cooldown == 0:
                    handle_player_death()

        elif boss_state == 'telegraph_shockwave':
            display_surface.blit(get_current_boss_sprite(), boss_rect)
            shockwave_zone_l.update(0, GROUND_Y - 30, boss_rect.left, 30)
            shockwave_zone_r.update(boss_rect.right, GROUND_Y - 30, 800 - boss_rect.right, 30)
            
            if flicker_on:
                pygame.draw.rect(display_surface, (255, 50, 50), shockwave_zone_l, 3)
                pygame.draw.rect(display_surface, (255, 50, 50), shockwave_zone_r, 3)

            if current_time - boss_timer > 800:
                boss_state = 'shockwave'
                boss_timer = current_time

        elif boss_state == 'shockwave':
            display_surface.blit(get_current_boss_sprite(), boss_rect)
            pygame.draw.rect(display_surface, (200, 0, 0), shockwave_zone_l, 3)
            pygame.draw.rect(display_surface, (200, 0, 0), shockwave_zone_r, 3)
            
            if (player_rect.colliderect(shockwave_zone_l) or player_rect.colliderect(shockwave_zone_r)) and hit_cooldown == 0:
                handle_player_death()

            if current_time - boss_timer > 400:
                boss_cycles += 1
                if boss_cycles >= 5:
                    is_playing = 10
                    intro_timer = current_time
                else:
                    boss_state = 'idle'
                    boss_timer = current_time

        # CHANGED: Lose a life if walking into boss during grounded, active states
        if player_rect.colliderect(boss_rect) and hit_cooldown == 0 and boss_state not in ['hidden', 'jumping', 'telegraph_landing']:
            handle_player_death()

        # CHANGED: Toggle outline purple boundary around the boss using standard 'H' key tracking
        if show_hitboxes and boss_state != 'hidden':
            pygame.draw.rect(display_surface, (128, 0, 128), boss_rect, 2)

    # ---------------- Boss Defeated Sequence ----------------
    elif is_playing == 10:
        display_surface.blit(BACKGROUND_SURF, (int(bg_x), 0))
        display_surface.blit(BACKGROUND_SURF, (int(bg_x) + 800, 0))
        display_surface.blit(GROUND_SURF, (0, GROUND_Y))
        display_surface.blit(player_surf, player_rect)
        draw_lives(lives)
        display_score()

        current_time = pygame.time.get_ticks()
        if current_time - intro_timer < 3000:
            msg = large_font.render('BOSS DEFEATED!', True, "Green")
            display_surface.blit(msg, msg.get_rect(center=(400, 200)))
            boss_surf_copy = BOSS_SPRITES['smash'].copy()
            alpha = max(0, 255 - int((current_time - intro_timer) / 3000 * 255))
            boss_surf_copy.set_alpha(alpha)
            display_surface.blit(boss_surf_copy, boss_rect)
        else:
            boss_defeated = True
            boss_active = False
            is_playing = 1
            score += 100
            player_rect.bottomleft = (25, GROUND_Y)

    # ---------------- Pause Mode Rendering ----------------
    elif is_playing == 3:
        display_surface.blit(BACKGROUND_SURF, (int(bg_x), 0))
        display_surface.blit(BACKGROUND_SURF, (int(bg_x) + 800, 0))
        display_surface.blit(GROUND_SURF, (0, GROUND_Y))
        
        if boss_active:
            if boss_state != 'hidden' and boss_state != 'telegraph_landing':
                display_surface.blit(get_current_boss_sprite(), boss_rect)
        else:
            for obstacle in obstacle_list:
                if obstacle["type"] == "ground":
                    frames = ENEMY_BITE_FRAMES if obstacle["biting"] else ENEMY_FRAMES
                    display_surface.blit(frames[obstacle["frame_index"]], obstacle["rect"])
                else:
                    display_surface.blit(FLYING_ENEMY_FRAMES[obstacle["frame_index"]], obstacle["rect"])

        display_surface.blit(player_surf, player_rect)
        draw_lives(lives)
        display_score()

        overlay = pygame.Surface((800, 400), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        display_surface.blit(overlay, (0, 0))

        display_surface.blit(game_pause, game_pause_rect)
        display_surface.blit(not_pause_btn, not_pause_rect)
        display_surface.blit(resume_btn, resume_rect)
        display_surface.blit(exit_btn, exit_rect)

    # ---------------- Menus (0, 4, 5, 6, 7) ----------------
    else:
        display_surface.fill((94, 129, 162))
        if is_playing == 0:
            display_surface.blit(BACKGROUND_SURF, (0, 0))
            display_surface.blit(GROUND_SURF, (0, GROUND_Y))
            overlay = pygame.Surface((800, 400), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            display_surface.blit(overlay, (0, 0))
            display_surface.blit(game_name, game_name_rect)
            hi_text = game_font.render(f'Best: {int(high_score)}', True, "White")
            display_surface.blit(hi_text, hi_text.get_rect(center=(400, 135)))
            display_surface.blit(start_btn, start_rect)
            display_surface.blit(controls_btn, controls_rect)
            display_surface.blit(options_btn, options_rect)
            display_surface.blit(leaderboard_btn, leaderboard_btn_rect)
        elif is_playing == 4:
            display_surface.blit(back_btn, back_rect)
            display_surface.blit(controls_message, controls_message_rect)
            display_surface.blit(controls_message2, controls_message2_rect)
            display_surface.blit(controls_message3, controls_message3_rect)
        elif is_playing == 5:
            display_surface.blit(back_btn, back_rect)
            display_surface.blit(options_message, options_message_rect)
            display_surface.blit(off_btn, off_rect)
        elif is_playing == 6:
            display_surface.blit(back_btn, back_rect)
            display_surface.blit(options_message, options_message_rect)
            display_surface.blit(on_btn, on_rect)
        elif is_playing == 7:
            display_surface.blit(leaderboard_title, leaderboard_title_rect)
            display_surface.blit(back_btn, back_rect)

    # --- Apply Screen Shake & Render ---
    render_x = randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
    render_y = randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
    if screen_shake > 0: screen_shake -= 1

    screen.fill((0, 0, 0))
    screen.blit(display_surface, (render_x, render_y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()