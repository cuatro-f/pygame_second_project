import pygame
import os
import sys
import random
from pygame import mixer


# инициализация pygame
pygame.init()
# инициализация плеера
mixer.init()

# звук выстрела
shot_sound = mixer.Sound('data\\sounds\\shot.mp3')


# Загрузка изображения
def load_image(name, colorkey=None):
    fullname = os.path.join('data\\images', name)
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


pygame.display.set_caption('Сквозь миры со скоростью света')
SIZE = WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode(SIZE)
FPS = 144
clock = pygame.time.Clock()


# группа выстрелов
shots_sprites = pygame.sprite.Group()
# группа метеоритов
meteorite_sprites = pygame.sprite.Group()


# класс выстрелов
class Shot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(shots_sprites)
        self.image = load_image('shot_0.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
        # скорость выстрела
        self.v = -10

    def update(self):
        self.rect = self.rect.move(0, self.v)


# группа корабля
ship_sprite = pygame.sprite.Group()


# Класс корабля
class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, speed, hp, damage):
        super().__init__(ship_sprite)
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.damage = damage

        self.image = load_image('ship.png')
        self.rect = self.image.get_rect()
        self.rect.x = 275
        self.rect.y = 400
        self.mask = pygame.mask.from_surface(self.image)

    """ Метод для изменения координат корабля """
    def move(self, movement_x, movement_y):
        self.rect = self.rect.move(self.speed * movement_x, self.speed * movement_y)

    """ Метод, возвращяющий координаты корабля """
    def get_cords(self):
        return self.rect.x, self.rect.y

    """ Метод, возвращающий размер корабля """
    def get_size(self):
        return self.image.get_rect()[2:]

    """ Метод, устанавливающий координаты """
    def set_cords(self, x, y):
        self.rect.x = x
        self.rect.y = y

    """ Метод, позволяющий стрелять """
    def shoot(self):
        bullet_x = self.rect.x
        bullet_y = self.rect.y
        shots_sprites.add(Shot(bullet_x, bullet_y))
        shot_sound.play()

    """ Метод, изменяющий hp """
    def change_heal_points(self, action, value):
        if action == '+':
            if self.hp == self.max_hp:
                pass
            else:
                self.hp += value
                if self.hp > self.max_hp:
                    self.hp = self.max_hp
        elif action == '-':
            self.hp -= value

    """ Метод, непозволяющий кораблю вылететь за пределы карты """
    def update(self, *args):
        print('ship hp (update) -', self.hp)
        print(self.get_size())
        if self.get_cords()[0] <= 0:
            self.set_cords(1, self.get_cords()[1])
        if self.get_cords()[1] <= 0:
            self.set_cords(self.get_cords()[0], 1)
        if self.get_cords()[0] >= WIDTH - self.get_size()[0]:
            self.set_cords(WIDTH - self.get_size()[0], self.get_cords()[1])
        if self.get_cords()[1] >= HEIGHT - self.get_size()[1]:
            self.set_cords(self.get_cords()[0], HEIGHT - 1 - self.get_size()[1])

    """ Метод, возвращающий урон, который наносит корабль """
    def get_damage(self):
        return self.damage


# Класс припятствий
class Meteorite(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, hp) -> object:
        super().__init__(meteorite_sprites)
        self.image = load_image('asteroid_b2.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

        self.speed = speed
        self.max_hp = self.hp = hp
        self.damage = 10

    """Метод, для уменьшеня количества hp при попадании"""
    def minus_hp(self, value):
        self.hp -= value
        # степень прозрачности зависит от потерянного хп
        # self.image.set_alpha(255 * self.hp / self.max_hp)

        # когда метеорит разрушается то он удалается
        if self.hp <= 0:
            meteorite_sprites.remove(self)

    """Метод для получения информации о метеорите"""
    def get_information(self):
        return self.rect.x, self.rect.y, self.speed, self.hp

    """Метод, наносящий урон"""
    def get_damage(self):
        return self.damage

    def update(self):
        """движение метеорита"""
        self.rect = self.rect.move(0, self.speed)

        # попадание выстрела
        shot = pygame.sprite.spritecollideany(self, shots_sprites,
                                                   collided=pygame.sprite.collide_mask)
        if not shot is None:
            shots_sprites.remove(shot)
            self.minus_hp(space_ship.get_damage())

        # столкновение с метеоритом
        ship = pygame.sprite.spritecollideany(self, ship_sprite,
                                                   collided=pygame.sprite.collide_mask)
        if not ship is None:
            meteorite_sprites.remove(self)
            ship.change_heal_points('-', self.damage)


# Класс заднего фона
class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


# Создание экземпляра класса SpaceShip
# Аргументы: Скоргость, hp, урон
space_ship = SpaceShip(5, 100, 5)
ship_sprite.add(space_ship)
movement_x = movement_y = 0

# Создание события при которм появляются метеориты
METEORITEGENERATION = pygame.USEREVENT + 1
pygame.time.set_timer(METEORITEGENERATION, 3000)

running = True
while running:
    # Задний фон
    background = Background("space.png", [0, 0])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Создание метеорита с случайными положением, радиусом, скоростью и кол-вом hp
        elif event.type == METEORITEGENERATION:
            new_meteorite = Meteorite(random.randint(1, WIDTH - 64), 0, random.randint(1, 6), random.randint(5, 15))
            meteorite_sprites.add(new_meteorite)
        # Вызов функции, производящей выстрел
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            space_ship.shoot()
        # движение
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                movement_y = -1
            elif event.key == pygame.K_s:
                movement_y = 1
            if event.key == pygame.K_d:
                movement_x = 1
            elif event.key == pygame.K_a:
                movement_x = -1
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                movement_y = 0
            elif event.key == pygame.K_s:
                movement_y = 0
            if event.key == pygame.K_d:
                movement_x = 0
            elif event.key == pygame.K_a:
                movement_x = 0
    space_ship.move(movement_x, movement_y)

    # Отображения заднего фона
    screen.fill([255, 255, 255])
    screen.blit(background.image, background.rect)

    meteorite_sprites.draw(screen)
    meteorite_sprites.update()

    shots_sprites.draw(screen)
    shots_sprites.update()

    ship_sprite.draw(screen)
    ship_sprite.update(event)

    pygame.display.flip()
    clock.tick(FPS)
