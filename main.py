import pygame
import asyncio
import random
import math

pygame.init()

# ---------------- SETTINGS ----------------
WIDTH = 960
HEIGHT = 540
FPS = 60
TOP_BORDER = HEIGHT // 16

WHITE = (255,255,255)
RED = (220,20,60)
GREEN = (50,205,50)
YELLOW = (255,255,0)
ORANGE = (255,140,0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Beneath The Surface")

clock = pygame.time.Clock()
font_big = pygame.font.Font(None, 70)
font = pygame.font.Font(None, 40)

# ---------------- LOAD IMAGES ----------------
bg = pygame.transform.scale(pygame.image.load("ocean.png"), (WIDTH, HEIGHT))
player_img = pygame.transform.scale(pygame.image.load("nemogame.png"), (80,60))
food_img = pygame.transform.scale(pygame.image.load("dory.png"), (50,40))
shark_img = pygame.transform.scale(pygame.image.load("shark.png"), (120,80))
plastic_img = pygame.transform.scale(pygame.image.load("plastic.png"), (60,60))

# ---------------- MENU ----------------
def menu():
    options = ["EASY","MEDIUM","HARD"]
    selected = None

    while selected is None:
        screen.blit(bg,(0,0))
        mx,my = pygame.mouse.get_pos()

        for i,opt in enumerate(options):
            y = HEIGHT//2 - 80 + i*80
            text = font_big.render(opt, True, WHITE)
            rect = text.get_rect(center=(WIDTH//2,y))
            screen.blit(text, rect)

            if rect.collidepoint(mx,my):
                hover = font_big.render(opt, True, YELLOW)
                screen.blit(hover, rect)
                if pygame.mouse.get_pressed()[0]:
                    selected = opt.lower()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None

        pygame.display.update()
        clock.tick(FPS)

    return selected

# ---------------- GAME LOOP ----------------
async def game(difficulty):

    player = player_img.get_rect(center=(WIDTH//4, HEIGHT//2))
    health = 100
    energy = 100
    distance = 0

    base_speed = {"easy":2,"medium":2.4,"hard":2.8}[difficulty]

    sharks = []
    for _ in range(3):
        sharks.append({
            "rect": shark_img.get_rect(center=(random.randint(WIDTH,WIDTH+400),
                                               random.randint(TOP_BORDER+50,HEIGHT-50))),
            "base_y": random.randint(TOP_BORDER+50,HEIGHT-50),
            "phase": random.random()*100
        })

    plastics = []
    for _ in range(2):
        plastics.append({
            "rect": plastic_img.get_rect(center=(random.randint(WIDTH,WIDTH+600),
                                                 random.randint(TOP_BORDER+50,HEIGHT-50))),
            "angle":0
        })

    food = food_img.get_rect(center=(random.randint(WIDTH,WIDTH+300),
                                      random.randint(TOP_BORDER+50,HEIGHT-50)))

    running = True
    while running:
        dt = clock.tick(FPS) / 16
        distance += 0.2
        speed_scale = 1 + distance/5000

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return

        keys = pygame.key.get_pressed()

        energy -= 0.05 * dt
        if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]:
            energy -= 0.15 * dt

        energy = max(0, min(100, energy))
        move_speed = 5 * (energy/100) if energy > 0 else 1.5

        if keys[pygame.K_w] and player.top > TOP_BORDER:
            player.y -= move_speed * dt
        if keys[pygame.K_s] and player.bottom < HEIGHT:
            player.y += move_speed * dt
        if keys[pygame.K_a] and player.left > 0:
            player.x -= move_speed * dt
        if keys[pygame.K_d] and player.right < WIDTH:
            player.x += move_speed * dt

        screen.blit(bg,(0,0))

        for s in sharks:
            s["rect"].x -= base_speed * speed_scale * dt
            s["rect"].y = s["base_y"] + math.sin(pygame.time.get_ticks()*0.002 + s["phase"]) * 40

            if s["rect"].right < 0:
                s["rect"].x = random.randint(WIDTH,WIDTH+400)

            screen.blit(shark_img, s["rect"])

            if player.colliderect(s["rect"]):
                health -= random.randint(10,99)
                s["rect"].x = WIDTH + random.randint(0,200)

        for p in plastics:
            p["rect"].x -= 1.2 * speed_scale * dt
            p["angle"] += 3
            rotated = pygame.transform.rotate(plastic_img, p["angle"])
            new_rect = rotated.get_rect(center=p["rect"].center)

            if p["rect"].right < 0:
                p["rect"].x = random.randint(WIDTH,WIDTH+500)

            screen.blit(rotated,new_rect)

            if player.colliderect(new_rect):
                health -= 10
                p["rect"].x = WIDTH + random.randint(0,200)

        food.x -= 2 * speed_scale * dt
        if food.right < 0:
            food.x = random.randint(WIDTH,WIDTH+300)

        screen.blit(food_img, food)

        if player.colliderect(food):
            energy = min(100, energy+20)
            food.x = random.randint(WIDTH,WIDTH+300)

        pygame.draw.rect(screen, RED, (10,10,200,20))
        pygame.draw.rect(screen, GREEN, (10,10,2*max(health,0),20))

        pygame.draw.rect(screen, WHITE, (10,60,200,15))
        pygame.draw.rect(screen, GREEN, (10,60,2*max(energy,0),15))

        score_text = font.render(f"DISTANCE: {int(distance)}",True,WHITE)
        screen.blit(score_text,(WIDTH-200,20))

        screen.blit(player_img,player)

        if health <= 0:
            return death(distance)

        pygame.display.update()
        await asyncio.sleep(0)

# ---------------- DEATH SCREEN ----------------
def death(distance):
    while True:
        screen.blit(bg,(0,0))

        t1 = font_big.render("YOU DIED",True,RED)
        t2 = font.render(f"Distance: {int(distance)}",True,WHITE)

        screen.blit(t1,t1.get_rect(center=(WIDTH//2,HEIGHT//2-60)))
        screen.blit(t2,t2.get_rect(center=(WIDTH//2,HEIGHT//2)))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return

        pygame.display.update()
        clock.tick(FPS)

# ---------------- RUN ----------------
while True:
    difficulty = menu()
    if difficulty is None:
        break
    game(difficulty)