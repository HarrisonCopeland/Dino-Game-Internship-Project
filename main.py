"""Dino Game in Python

A game similar to the famous Chrome Dino Game, built using pygame-ce.
Made by intern: @bassemfarid, no one or nothing else. 🤖
"""

import pygame
import sprites

pygame.init()  # Initialize all pygame modules
screen = pygame.display.set_mode((800, 400))  # Create 800x400 window
pygame.display.set_caption("Dino Game")  # Set window title
clock = pygame.time.Clock()  # Controls FPS
running = True  # Main loop flag — False kills the game

# --- Game State ---
is_playing = False          # False = on menu/end screen, True = in game
GROUND_Y = 300              # Y-coordinate where ground level sits
JUMP_GRAVITY_START_SPEED = -20  # Negative = upward velocity on jump
players_gravity_speed = 0   # Current vertical speed (increases each frame)
score = 0                   # Current run score
high_score = 0              # Best score across all runs
frame_count = 0             # Counts frames, used to time animations
egg_speed = 5               # How fast the egg moves left (increases over time)

# --- Level Assets ---
SKY_SURF = pygame.image.load("graphics/level/sky.png").convert()      # Sky background
GROUND_SURF = pygame.image.load("graphics/level/ground.png").convert() # Ground strip

# --- Fonts ---
game_font = pygame.font.Font(pygame.font.get_default_font(), 30)  # UI / score text
large_font = pygame.font.Font(pygame.font.get_default_font(), 50) # Big titles (Game Over etc.)

# --- Player Sprites ---
PLAYER_WALK = [
    pygame.image.load("graphics/player/player_walk_1.png").convert_alpha(),  # Walk frame 1
    pygame.image.load("graphics/player/player_walk_2.png").convert_alpha(),  # Walk frame 2
]
PLAYER_JUMP = pygame.image.load("graphics/player/player_jump.png").convert_alpha()  # Jump pose

# --- Egg Sprites ---
EGG_FRAMES = [
    pygame.image.load("graphics/egg/egg_1.png").convert_alpha(),  # Egg animation frame 1
    pygame.image.load("graphics/egg/egg_2.png").convert_alpha(),  # Egg animation frame 2
]

# --- Animation State ---
walk_frame_index = 0   # Which walk frame is currently shown (0 or 1)
egg_frame_index = 0    # Which egg frame is currently shown (0 or 1)

# --- Initial (position + size of each sprite) ---
player_surf = PLAYER_WALK[0]
player_rect = player_surf.get_rect(bottomleft=(25, GROUND_Y))   # Player starts left, on ground

egg_surf = EGG_FRAMES[0]
egg_rect = egg_surf.get_rect(bottomleft=(800, GROUND_Y))        # Egg starts off-screen right


def reset_game():
    """Resets all so that your game can restart"""

    global players_gravity_speed, score, frame_count, egg_speed
    players_gravity_speed = 0   # Stop any residual vertical movement
    score = 0                   # Clear score
    frame_count = 0             # Restart animation counter
    egg_speed = 5               # Back to starting speed
    player_rect.bottomleft = (25, GROUND_Y)  # Return player to start
    egg_rect.left = 800                       # Push egg back off-screen


def draw_score():
    """Makes the score"""

    score_text = game_font.render(f"Score: {int(score)}", True, "Black")
    score_rect = score_text.get_rect(topright=(780, 15))                    # Anchor top-right
    pygame.draw.rect(screen, "#c0e8ec", score_rect.inflate(16, 8), border_radius=6)  # Background pill
    screen.blit(score_text, score_rect)


def draw_end_screen():
    """Draws the start/game-over overlay on top of the frozen world."""
    overlay = pygame.Surface((800, 400), pygame.SRCALPHA)  # Full-screen transparent surface
    overlay.fill((0, 0, 0, 160))                           # Semi-transparent black tint
    screen.blit(overlay, (0, 0))

    # Show "DINO GAME" before first run, "GAME OVER" after dying
    title_text = "DINO GAME" if score == 0 else "GAME OVER"
    title_color = "White" if score == 0 else "Red"
    title = large_font.render(title_text, True, title_color)
    screen.blit(title, title.get_rect(center=(400, 130)))

    if score > 0:  # Only show last score if a run was actually played
        score_text = game_font.render(f"Score: {int(score)}", True, "White")
        screen.blit(score_text, score_text.get_rect(center=(400, 200)))

    hi_text = game_font.render(f"Best: {int(high_score)}", True, "Yellow")  # Your High score
    screen.blit(hi_text, hi_text.get_rect(center=(400, 240)))

    # Blink the prompt every 500 ms using the system timer
    if (pygame.time.get_ticks() // 500) % 2 == 0:
        prompt = game_font.render("Press SPACE to Play", True, "White")
        screen.blit(prompt, prompt.get_rect(center=(400, 300)))


# -------------- Main Game Loop -------------------------------
while running:

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # X button → exit
            running = False

        elif is_playing:
            # Jump on SPACE or mouse click — only when standing on the ground
            if (
                event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
                or event.type == pygame.MOUSEBUTTONDOWN
            ) and player_rect.bottom >= GROUND_Y:
                players_gravity_speed = JUMP_GRAVITY_START_SPEED  # Launch upward

        else:
            # Restart on SPACE or click from the menu/end screen
            if (
                event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE
                or event.type == pygame.MOUSEBUTTONDOWN
            ):
                reset_game()
                is_playing = True

    # --- Draw Background (always, even on end screen) ---
    screen.blit(SKY_SURF, (0, 0))       # Sky fills top portion
    screen.blit(GROUND_SURF, (0, GROUND_Y))  # Ground strip at GROUND_Y

    # ----------------- Active Gameplay ----------------------
    if is_playing:
        frame_count += 1          # Advance animation timer each frame
        score += 0.05             # ~3 points per second at 60 FPS
        egg_speed = 5 + int(score // 100) * 0.5  # Egg gets faster every 100 pts

        # --- Egg Movement & Animation ---
        egg_rect.x -= int(egg_speed)        # Move egg left each frame
        if egg_rect.right <= 0:             # Wrap back to right edge when off-screen
            egg_rect.left = 800

        if frame_count % 15 == 0:           # Switch egg frame every 15 frames (~4 fps)
            egg_frame_index = (egg_frame_index + 1) % len(EGG_FRAMES)
        egg_surf = EGG_FRAMES[egg_frame_index]
        screen.blit(egg_surf, egg_rect)

        # --- Player Physics ---
        players_gravity_speed += 1          # Gravity pulls player down each frame
        player_rect.y += players_gravity_speed  # Apply vertical speed to position
        if player_rect.bottom > GROUND_Y:   # Clamp to ground so player doesn't fall through
            player_rect.bottom = GROUND_Y
            players_gravity_speed = 0       # Stop falling once grounded

        # --- Player Animation ---
        is_airborne = player_rect.bottom < GROUND_Y  # True while in the air
        if is_airborne:
            player_surf = PLAYER_JUMP       # Show jump sprite while off the ground
        else:
            if frame_count % 10 == 0:       # Alternate walk frames every 10 frames (~6 fps)
                walk_frame_index = (walk_frame_index + 1) % len(PLAYER_WALK)
            player_surf = PLAYER_WALK[walk_frame_index]

        screen.blit(player_surf, player_rect)

        draw_score()  # Render score badge on top of everything

        # --- Collision Detection ---
        if egg_rect.colliderect(player_rect.inflate(-10, -10)):  # Shrink rect for forgiveness
            if int(score) > int(high_score):  # Update high score if beaten
                high_score = score
            is_playing = False  # End the run

    # --- End / Start Screen --------------------------------------------
    else:
        draw_end_screen()  # Overlay on top of the static background

    pygame.display.flip()  # Push everything drawn this frame to the screen
    clock.tick(60)         # Cap at 60 FPS

pygame.quit()  # Clean up pygame on exit
