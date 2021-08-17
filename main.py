import pygame
import os
import time
import random
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 750, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Merdeka Corona")
#Lany
#load button images
start_img = pygame.image.load(os.path.join("assets", "start_btn.png"))
exit_img = pygame.image.load(os.path.join("assets", "exit_btn.png"))

# Load images
RED_CORONAVIRUS = pygame.image.load(os.path.join("assets", "cov_red.png"))
GREEN_CORONAVIRUS = pygame.image.load(os.path.join("assets", "cov_green.png"))
BLUE_CORONAVIRUS = pygame.image.load(os.path.join("assets", "cov_blue.png"))

# Player player
YELLOW_ANTIBODY = pygame.image.load(os.path.join("assets", "girl2.1.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "antibody.png"))

# Background
BGA = pygame.transform.scale(pygame.image.load(os.path.join("assets", "ba.jpeg")), (WIDTH, HEIGHT))
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bd.jpeg")), (WIDTH, HEIGHT))
font=pygame.font.Font('freesansbold.ttf',32)
textX = 10
textY = 60

score_value = 0
def show_score(x,y):
    score = font.render("score :" + str(score_value),True,(0,0,0))
    WIN.blit(score,(textX,textY))

#Dania
class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action
        
#create button instances
start_button = Button(100, 350, start_img, 0.8)
exit_button = Button(450, 350, exit_img, 0.8)
#Anisa
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)
#Anisa
class Cell:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.cell_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.cell_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.cell_img.get_width()

    def get_height(self):
        return self.cell_img.get_height()
        #Dania
class Player(Cell):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.cell_img = YELLOW_ANTIBODY
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.cell_img)
        self.max_health = health
        #score
        self.score = 0

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        #Lany scoring
                        self.score += 100
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.cell_img.get_height() + 10, self.cell_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.cell_img.get_height() + 10, self.cell_img.get_width() * (self.health/self.max_health), 10))
#Dania
class Enemy(Cell):
    COLOR_MAP = {
                "red": (RED_CORONAVIRUS, RED_LASER),
                "green": (GREEN_CORONAVIRUS, GREEN_LASER),
                "blue": (BLUE_CORONAVIRUS, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.cell_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.cell_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
#Almas
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None
#Esther
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1 #jika value enemy_vel kecil maka gerak dari musuh akan melambat, begitupun sebaliknya

    player_vel = 5 #jika value player_vel kecil maka gerak dari antibodi akan melambat, begitupun sebaliknya
    laser_vel = 5 #jika value laser_vel kecil maka akan menghasilkan pergerakan laser yang lambat, begitupun sebaliknya.

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (0,0,0))
        level_label = main_font.render(f"Level: {level}", 1, (0,0,0))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

    while run:
        # music = pygame.mixer.music.load(os.path.join("assets", "Instrumen Maju Tak Gentar.mp3"))
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        #Show score
        player.move_lasers(-laser_vel, enemies)
        score = font.render("Score: " + str(player.score),True,(0,0,0))
        WIN.blit(score,(textX,textY))
        pygame.display.update()

#Dania
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    musik = pygame.mixer.Sound(r"D:\Games\assets\Instrumen Maju Tak Gentar.mp3")
    musik.play()
    run = True
    while run:
        WIN.blit(BGA, (0,0))
        if start_button.draw(WIN):
            main()
        if exit_button.draw(WIN):
            run = False
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
    pygame.quit()


main_menu()