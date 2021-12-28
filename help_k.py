import pygame
import os
import sys


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)

    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image.convert_alpha()
    return image


pygame.init()
SIZE = 500, 500
clock = pygame.time.Clock()
FPS = 60
v = 50
fon_sprites = pygame.sprite.Group()


class Fon(pygame.sprite.Sprite):
    def __init__(self, image_name):
        super().__init__(fon_sprites)
        self.image = load_image(image_name)
        print(self.image.get_size())
        self.rect = self.image.get_rect()
        self.rect.x = self.rect.y = 0

    def update(self):
        self.rect = self.rect.move(-1, 0)

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption('Иницализация игры')

fon_sprites.add(Fon('space.png'))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))
    fon_sprites.draw(screen)
    fon_sprites.update()
    clock.tick(FPS)
    pygame.display.flip()

pygame.quit()
