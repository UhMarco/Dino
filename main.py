import pygame
import os
import random
from button import Button

pygame.init()
WIDTH, HEIGHT = 800, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
SCREEN = WIN.copy()
pygame.display.set_caption("Dino")

BG = (30, 30, 30)
FLOOR_COLOUR = (73, 73, 73)
TEXT_COLOUR = (200, 200, 200)

BUTTON_IMAGE = pygame.image.load(os.path.join('assets', 'UI', 'restart.png'))

PLAYER_HEIGHT = int(HEIGHT * 0.8)

clock = pygame.time.Clock()
FPS = 60

screen_shake = 0

MAIN_FONT = pygame.font.Font(os.path.join(
    'assets', 'UI', 'font', 'pixelmix.ttf'), 20)
BOLD_FONT = pygame.font.Font(os.path.join(
    'assets', 'UI', 'font', 'pixelmix_bold.ttf'), 32)

FLOOR = pygame.Rect(0, PLAYER_HEIGHT, WIDTH, 5)


class Dinosaur:
    def __init__(self, x, y, state='idle'):
        self.state = state

        self.animations = {}
        for folder in os.listdir(os.path.join('assets', 'dino')):
            animations = []
            for image in range(len(os.listdir(os.path.join('assets', 'dino', folder)))):
                img = pygame.image.load(os.path.join(
                    'assets', 'dino', folder, f'{folder}{image}.png')).convert_alpha()
                animations.append(img)
            self.animations[folder] = animations

        self.image = self.animations[self.state][0]

        self.rect = self.image.get_rect()
        self.animation_index = 0
        self.last_frame = pygame.time.get_ticks()
        self.rect.x = x
        self.rect.y = y - self.get_height() + 2
        self.gravity = 0
        self.jumping = False

    def jump(self):
        if self.jumping == False:
            self.jumping = True
            self.gravity = -14

    def animate(self):
        if ((pygame.time.get_ticks() - self.last_frame) / 1000 > 0.15):
            self.last_frame = pygame.time.get_ticks()
            self.animation_index += 1
            if self.animation_index >= len(self.animations[self.state]):
                self.animation_index = 0
            self.image = self.animations[self.state][self.animation_index]

    def draw(self):
        self.animate()

        if self.jumping:
            self.gravity += 0.85
            self.rect.y += self.gravity
            if self.rect.bottom > FLOOR.top:
                self.rect.bottom = FLOOR.top
                self.jumping = False
                self.gravity = 0

        SCREEN.blit(self.image, (self.rect.x, self.rect.y))

    def set_state(self, state):
        if self.state != state:
            self.state = state
            self.animation_index = 0
            self.animate()

    def get_width(self):
        return self.image.get_width()

    def get_height(self):
        return self.image.get_height()


class Cactus(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        path = os.path.join('assets', 'obstacles', 'cactus')
        img = pygame.image.load(os.path.join(
            'assets', 'obstacles', 'cactus', f'cactus{random.randint(0, len(os.listdir(path)) - 1)}.png'))
        self.image = pygame.transform.scale(
            img, (int(img.get_width() * 1.3), int(img.get_height() * 1.3)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y - self.get_height() + 5
        self.speed = 5

    def move(self):
        self.rect.x -= self.speed

    def draw(self):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))

    def off_screen(self):
        return self.rect.x < -50

    def get_width(self):
        return self.image.get_width()

    def get_height(self):
        return self.image.get_height()


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        path = os.path.join('assets', 'obstacles', 'bird')
        self.animations = []
        for i in range(len(os.listdir(path))):
            img = pygame.image.load(os.path.join(
                'assets', 'obstacles', 'bird', f'bird{i}.png'))
            self.animations.append(pygame.transform.scale(
                img, (int(img.get_width() * 0.7), int(img.get_height() * 0.7))))
        self.image = self.animations[0]
        self.animation_index = 0
        self.last_frame = pygame.time.get_ticks()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 7

    def move(self):
        self.rect.x -= self.speed
        if ((pygame.time.get_ticks() - self.last_frame) / 1000 > 0.15):
            self.last_frame = pygame.time.get_ticks()
            if self.animation_index == 0:
                self.animation_index = 1
                self.rect.y -= 7
            else:
                self.animation_index = 0
                self.rect.y += 7
            self.image = self.animations[self.animation_index]

    def draw(self):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))

    def off_screen(self):
        return self.rect.x < -50

    def get_width(self):
        return self.image.get_width()

    def get_height(self):
        return self.image.get_height()


player = Dinosaur(75, PLAYER_HEIGHT)
cacti = []
birds = []
fading = False
alpha = 0
restart_button = Button(
    WIDTH - BUTTON_IMAGE.get_width() - 10, 10, BUTTON_IMAGE, 1)


def main():
    global screen_shake, alpha  # I know D:

    cacti.append(Cactus(random.randint(
        WIDTH + 100, WIDTH + 700), PLAYER_HEIGHT))
    for i in range(10):
        cacti.append(Cactus(random.randint(
            cacti[-1].rect.x + 300, cacti[-1].rect.x + 1000), PLAYER_HEIGHT))

    birds.append(
        Bird(random.randint(WIDTH + 5000, WIDTH + 7000), PLAYER_HEIGHT - random.randint(100, 200)))

    lost = False
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                if event.key == pygame.K_SPACE:
                    if lost:
                        fade = pygame.Surface((WIDTH, HEIGHT))
                        fade.fill(BG)
                        fade.set_alpha(alpha)
                        SCREEN.blit(fade, (0, 0))
                        alpha += 10
                    else:
                        player.jump()

        render_offset = [0, 0]
        if screen_shake > 0:
            screen_shake -= 1
            render_offset[0] = random.randint(0, 8) - 4
            render_offset[1] = random.randint(0, 8) - 4

        SCREEN.fill(BG)
        pygame.draw.rect(SCREEN, FLOOR_COLOUR, FLOOR)
        player.draw()

        for cactus in cacti[:]:
            if not(lost):
                cactus.move()
            cactus.draw()
            if cactus.off_screen():
                cactus.kill()
                cacti.remove(cactus)
                if random.randint(0, 100) > 5:
                    birds.append(Bird(random.randint(
                        birds[-1].rect.x + 5000, birds[-1].rect.x + 7000), PLAYER_HEIGHT - random.randint(100, 200)))

                cacti.append(Cactus(random.randint(
                    cacti[-1].rect.x + 300, cacti[-1].rect.x + 1000), PLAYER_HEIGHT))

            elif cactus.rect.colliderect(player.rect) and not(lost):
                lost = True
                player.set_state('dead')
                screen_shake = 20

        for bird in birds:
            if not(lost):
                bird.move()
            bird.draw()
            if bird.off_screen():
                bird.kill()
                birds.remove(bird)

            elif bird.rect.colliderect(player.rect) and not(lost):
                lost = True
                player.set_state('dead')
                screen_shake = 20

        if lost:
            message = BOLD_FONT.render('You lost!', False, TEXT_COLOUR)
            SCREEN.blit(message, (WIDTH / 2 - message.get_width() /
                        2, HEIGHT / 2 - message.get_height()))
            if restart_button.draw(SCREEN) or alpha != 0:
                fade = pygame.Surface((WIDTH, HEIGHT))
                fade.fill(BG)
                fade.set_alpha(alpha)
                SCREEN.blit(fade, (0, 0))
                alpha += 10
                if alpha == 300:
                    alpha = 0
                    player.set_state("idle")
                    for cactus in cacti:
                        cactus.kill()
                    cacti.clear()
                    for bird in birds:
                        bird.kill()
                    birds.clear()
                    start()

        WIN.blit(SCREEN, render_offset)
        pygame.display.flip()

    pygame.quit()


def start():
    alpha = 300

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                if event.key == pygame.K_SPACE:
                    player.set_state('run')
                    player.jump()
                    main()

        SCREEN.fill(BG)
        pygame.draw.rect(SCREEN, FLOOR_COLOUR, FLOOR)
        player.draw()

        main_text = BOLD_FONT.render(
            'Press SPACE to jump...', False, TEXT_COLOUR)
        SCREEN.blit(main_text, (WIDTH / 2 - main_text.get_width() /
                    2, HEIGHT / 2 - main_text.get_height() / 2 - 20))

        sub_text = MAIN_FONT.render(
            'Let\'s gooooooo!', False, TEXT_COLOUR)
        SCREEN.blit(sub_text, (WIDTH / 2 - sub_text.get_width() / 2,
                    HEIGHT / 2 - sub_text.get_height() / 2 + 20))

        fade = pygame.Surface((WIDTH, HEIGHT))
        fade.fill(BG)
        fade.set_alpha(alpha)
        if alpha != 0:
            alpha -= 10
        SCREEN.blit(fade, (0, 0))

        WIN.blit(SCREEN, (0, 0))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    start()
