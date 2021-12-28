import pygame
import os
import sys
import random


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
pygame.display.set_caption('Сквозь миры со скоростью света')
SIZE = WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode(SIZE)
FPS = 60

ship_sprite = pygame.sprite.Group()


# Класс корабля
class SpaceShip(pygame.sprite.Sprite):
    def __init__(self, speed, bullet_speed, hp):
        super().__init__(ship_sprite)
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.bullet_speed = bullet_speed
        self.bullet_list = []

        self.image = load_image('ship.png')
        self.rect = self.image.get_rect()
        self.rect.x = 275
        self.rect.y = 400

    """Метод для изменения координат корабля"""
    def move(self, movement_x, movement_y):
        self.rect = self.rect.move(self.speed * movement_x, self.speed * movement_y)

    """Метод, возвращяющий координаты корабля"""
    def get_cords(self):
        return self.rect.x, self.rect.y

    """Метод, возвращающий размер корабля"""
    def get_size(self):
        return self.image.get_rect()

    """Метод, устанавливающий координаты"""
    def set_cords(self, x, y):
        self.rect.x = x
        self.rect.y = y

    """Метод, позволяющий стрелять"""
    def shoot(self):
        self.bullet_x = self.rect.x + self.get_size()[0] // 2
        self.bullet_y = self.rect.y + self.get_size()[1] // 2
        self.bullet_list.append([self.bullet_x, self.bullet_y])

    """Метод, изменяющий hp"""
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

    def get_hp(self):
        print(self.hp)

    def update(self, *args):
        # Вызов функции, производящей выстрел
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.shoot()
        # Условия, непозволяющие кораблю выйти за пределы поля
        if self.get_cords()[0] <= 0:
            self.set_cords(1, self.get_cords()[1])
        if self.get_cords()[1] <= 0:
            self.set_cords(self.get_cords()[0], 1)
        if self.get_cords()[0] >= WIDTH - self.get_size()[0]:
            self.set_cords(WIDTH - self.get_size()[0], self.get_cords()[1])
        if self.get_cords()[1] >= HEIGHT - self.get_size()[1]:
            self.set_cords(self.get_cords()[0], HEIGHT - 1 - self.get_size()[1])


meteorite_sprites = pygame.sprite.Group()

# Класс припятствий
class Meteorite(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, hp):
        super().__init__(meteorite_sprites)
        self.image = load_image('asteroid_b2.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
        self.hp = hp
        self.damage = 10

    """Метод, для уменьшеня количества hp при попадании"""
    def minus_hp(self, value):
        self.hp -= value

    """Метод для получения информации о метеорите"""
    def get_information(self):
        return self.rect.x, self.rect.y, self.speed, self.hp

    """Метод, наносящий урон"""
    def get_damage(self):
        return self.damage

    def update(self):
        """движение метеорита"""
        self.rect = self.rect.move(0, self.speed)


# Создание экземпляра класса SpaceShip
space_ship = SpaceShip(3, 5, 100)
ship_sprite.add(space_ship)
movement_x = movement_y = 0
clock = pygame.time.Clock()

# Создание события при которм появляются метеориты
METEORITEGENERATION = pygame.USEREVENT + 1
pygame.time.set_timer(METEORITEGENERATION, 3000)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Создание метеорита с случайными положением, радиусом, скоростью и кол-вом hp
        elif event.type == METEORITEGENERATION:
            new_meteorite = Meteorite(random.randint(40, 360), 0, random.randint(5, 20), random.randint(40, 70))
            meteorite_sprites.add(new_meteorite)
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

    screen.fill((0, 0, 0))
    meteorite_sprites.draw(screen)
    meteorite_sprites.update()
    ship_sprite.draw(screen)
    ship_sprite.update()
    pygame.display.flip()
    clock.tick(FPS)
