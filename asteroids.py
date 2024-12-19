import pygame
import random
from pygame import Vector2
from pygame.transform import rotozoom
from pygame.mixer import Sound
from button import Button


PROTOCOLS = ["UDP", "TCP", "ICMP", "HTTP", "DNS"]
level = 1
levels = ["Shoot only Layer 4 OSI protocols", "Shoot only Layer 3 OSI protocols", "Shoot only Layer 7 OSI protocols"]
level_answers = {"level1": ["UDP", "TCP"], "level2": ["ICMP"], "level3": ["HTTP", "DNS"]}
MAX_ASTEROID_Y = 600
MIN_ASTEROID_X = 400

def blit_rotated(position, image, forward, screen):
    angle = forward.angle_to(Vector2(0, -1))
    rotated_surface = rotozoom(image, angle, 1.0)
    rotated_surface_size = Vector2(rotated_surface.get_size())
    blit_position = position - rotated_surface_size // 2
    screen.blit(rotated_surface, blit_position)

def wrap_position(position, screen):
    x, y = position
    w, h = screen.get_size()
    return Vector2(x % w, y % h)


class Ship:
    def __init__(self, position):
        self.position = Vector2(position)
        self.image = pygame.image.load('static/images/ship.png')
        self.forward = Vector2(0, -1)
        self.bullets = []
        self.can_shoot = 0
        self.drift = (0, 0)
        self.shoot = Sound('static/shoot.wav')

    def update(self):
        is_key_pressed = pygame.key.get_pressed()
        if is_key_pressed[pygame.K_UP]:
            self.position += self.forward
            self.drift = (self.drift + self.forward) / 1.5
        if is_key_pressed[pygame.K_LEFT]:
            self.forward = self.forward.rotate(-1)
        if is_key_pressed[pygame.K_RIGHT]:
            self.forward = self.forward.rotate(1)
        if is_key_pressed[pygame.K_SPACE] and self.can_shoot == 0:
            self.bullets.append(Bullet(Vector2(self.position), self.forward * 10))
            self.shoot.play()
            self.can_shoot = 500
        self.position += self.drift
        if self.can_shoot > 0:
            self.can_shoot -= clock.get_time()
        else:
            self.can_shoot = 0


    def draw(self, screen):
        self.position = wrap_position(self.position, screen)
        blit_rotated(self.position, self.image, self.forward, screen)


class Bullet:
    def __init__(self, position, velocity):
        self.position = position
        self.velocity = velocity

    def update(self):
        self.position += self.velocity

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), [self.position.x, self.position.y, 5, 5])

class Asteroid:
    def __init__(self, position, protocol):
        self.position = Vector2(position)
        self.protocol_text = protocol
        self.velocity = Vector2(random.randint(-3, 3), random.randint(-3, 3))
        self.image = pygame.image.load(f'static/images/{protocol}asteroid.png')
        self.radius = self.image.get_width() // 2
        self.explode = Sound('static/explode.mp3')

    def update(self):
        self.position += self.velocity

    def draw(self, screen):
        self.position = wrap_position(self.position, screen)
        blit_rotated(self.position, self.image, self.velocity, screen)

    def hit(self, position):
        if self.position.distance_to(position) <= self.radius:
            self.explode.play()
            return True
        return False
    
    

pygame.init()
screen = pygame.display.set_mode((1280, 600))
pygame.display.set_caption("'Roids")
background = pygame.image.load('static/images/space.png')
game_over = False
ship = Ship((100, 700))
asteroids = []
correct_asteroids = []
out_of_bounds = [-150, -150, 1430, 1430]


##end game loss text
font = pygame.font.Font('static/Alien.ttf', 80)
text_loser = font.render("You Lost!", True, (255, 255, 255))
text_loser_position = ( (screen.get_width() - text_loser.get_width()) // 2,
                        (screen.get_height() - text_loser.get_height()) // 2)
#end game win text
font2 = pygame.font.Font('static/Alien.ttf', 80)
text_winner = font2.render("You Won!", True, (255, 255, 255))
text_winner_position = ( (screen.get_width() - text_winner.get_width()) // 2,
                        (screen.get_height() - text_winner.get_height()) // 2)

#end level win text
font3 = pygame.font.Font('static/Alien.ttf', 80)
next_level_text_winner = font3.render("Level Complete!", True, (255, 255, 255))
next_level_text_winner_position = ( (screen.get_width() - text_winner.get_width() - 270) // 2,
                        (screen.get_height() - text_winner.get_height()) // 2)
#level display text
font4 = pygame.font.Font('static/Alien.ttf', 40)

#restart button
restart_buton_img = pygame.image.load('static/button_restart.png')
restart_buton = Button(text_loser_position[0], text_loser_position[1] + text_loser.get_height(), image=restart_buton_img)

next_level_buton_img = pygame.image.load('static/images/nextlevel.png')
next_level_buton = Button(text_loser_position[0], text_loser_position[1] + text_loser.get_height(), image=next_level_buton_img)

clock = pygame.time.Clock()


def loadAsteroids():
    total_asteroids = 6
    correct_asteroids_count = 2
    incorrect_answers = []
    
    for i in range(correct_asteroids_count):
        correct_asteroids.append(Asteroid((random.randint(MIN_ASTEROID_X, screen.get_width()),
                                  random.randint(0, MAX_ASTEROID_Y)), level_answers[f"level{level}"][random.randrange(len(level_answers[f"level{level}"]))]))
    for i in range(total_asteroids - correct_asteroids_count):
        for protocol in PROTOCOLS:
         if level_answers[f"level{level}"].__contains__(protocol):
            continue
         else:
                if not incorrect_answers.__contains__(protocol):
                    incorrect_answers.append(protocol)
    for i in range(total_asteroids - correct_asteroids_count):
        asteroids.append(Asteroid((random.randint(MIN_ASTEROID_X, screen.get_width()),
                                   random.randint(0, MAX_ASTEROID_Y)), incorrect_answers[random.randrange(len(incorrect_answers))]))

    
    

loadAsteroids()
#main game loop
while not game_over:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
    screen.blit(background, (0, 0))
    level_text = font4.render(levels[level -1], True, (255,255,255))
    screen.blit(level_text, ((screen.get_width() - level_text.get_width()) // 2, 0))

    #checks for is ship has been destroyed and ends game
    if ship is None:
        screen.blit(text_loser, text_loser_position)
        if restart_buton.draw(screen):
            level = 1
            ship = Ship((100,700))
            asteroids.clear()
            correct_asteroids.clear()
            loadAsteroids()
        pygame.display.update()
        continue

    if len(correct_asteroids) == 0 and level == len(levels):
            screen.blit(text_winner, text_winner_position)
            if restart_buton.draw(screen):
                level = 1
                ship = Ship((100,700))
                asteroids.clear()
                correct_asteroids.clear()
                loadAsteroids()
            pygame.display.update()
            continue
    if len(correct_asteroids) == 0:
            screen.blit(next_level_text_winner, next_level_text_winner_position)
            if next_level_buton.draw(screen):
                level +=1
                ship = Ship((100,700))
                asteroids.clear()
                correct_asteroids.clear()
                loadAsteroids()
            pygame.display.update()
            continue
    

    ship.update()
    ship.draw(screen)
    #updates asteroids and checks for ship collision
    for a in correct_asteroids:
        a.update()
        a.draw(screen)
        if a.hit(ship.position):
            ship = None
            break
    if ship != None:
        for a in asteroids:
            a.update()
            a.draw(screen)
            if a.hit(ship.position):
                ship = None
                break

    if ship is None:
        continue

    deadbullets = []
    deadasteroids = []

    for b in ship.bullets:
        b.update()
        b.draw(screen)

       
        if b.position.x < out_of_bounds[0] or \
            b.position.x > out_of_bounds[2] or \
            b.position.y < out_of_bounds[1] or \
            b.position.y > out_of_bounds[3]:
            if not deadbullets.__contains__(b):
                deadbullets.append(b)

        for a in asteroids:
            if a.hit(b.position):
                if not deadbullets.__contains__(b):
                    deadbullets.append(b)
                if not deadasteroids.__contains__(a):
                    if level_answers[f"level{level}"].__contains__(a.protocol_text):
                        deadasteroids.append(a)
                    else:
                        ship = None
                        break
        for a in correct_asteroids:
            if a.hit(b.position):
                if not deadbullets.__contains__(b):
                    deadbullets.append(b)
                if not deadasteroids.__contains__(a):
                    deadasteroids.append(a)
                   

    if ship != None:
        for b in deadbullets:
            ship.bullets.remove(b)

        for a in deadasteroids:
            correct_asteroids.remove(a)


    pygame.display.update()
pygame.quit()