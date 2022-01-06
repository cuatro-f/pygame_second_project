import time

import pygame
import os
import sys
import random
import pygame_gui
from math import sin, cos, radians
from pygame import mixer


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


# инициализация pygame
pygame.init()
# инициализация плеера
mixer.init()

# Устанавливаем лимит на каналы
pygame.mixer.set_num_channels(20)

# Звук выстрела
shot_sound = mixer.Sound('data\\sounds\\shot.mp3')
# Звук столкновения
collision_sound = mixer.Sound('data\\sounds\\collision.mp3')
# Главная тема
main_theme = mixer.Sound('data\\sounds\\main_theme.mp3')
main_theme.set_volume(0.2)

# шаг корабля за одно нажатие
step = 0.5

pygame.display.set_caption('Сквозь миры со скоростью света')
SIZE = WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode(SIZE)
FPS = 60
clock = pygame.time.Clock()
main_theme.play(loops=-1)

# менеджер для интерфейса
manager = pygame_gui.UIManager(SIZE)


# Класс заднего фона
class Background(pygame.sprite.Sprite):
    def __init__(self, image_file, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(image_file)
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = location


def terminate():
    pygame.quit()
    sys.exit()


# начальный экран
def start_screen():
    background = Background('start_fon_2.png', [0, 0])

    # ПОТОМ НАДО БУДЕТ СДЕЛАТЬ ВЫПАДАЮЩИЙ СПИСОК С ВЫБОРОМ УРОВНЯ
    # кнопка запускающая игру
    play_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 250), (150, 50)),
        text='ИГРАТЬ',
        manager=manager,
    )
    rating_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 305), (150, 30)),
        text='РЕЙТИНГ',
        manager=manager,
    )

    rules_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(((WIDTH - 150) // 2, 340), (150, 30)),
        text='ПРАВИЛА',
        manager=manager,
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == play_button:
                    return
            manager.process_events(event)

        # Отображения заднего фона
        screen.fill([255, 255, 255])
        screen.blit(background.image, background.rect)

        time_delta = clock.tick(FPS) / 1000.0
        manager.update(time_delta)
        manager.draw_ui(screen)

        pygame.display.flip()


# пауза
def pause_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return

        screen.blit(load_image('start_pause.png', -1), ((WIDTH - 128) // 2, (HEIGHT - 128) // 2))
        pygame.display.flip()


# вызов начального экрана
start_screen()


# Размеры астероидов
# Маленького астероида
small_asteroid_size = load_image('small_asteroid.png').get_rect()[2:]
# Среднего Астероида
medium_asteroid_size = load_image('medium_asteroid.png').get_rect()[2:]
# Большого астероида
large_asteroid_size = load_image('large_asteroid.png').get_rect()[2:]

# группа выстрелов
shots_sprites = pygame.sprite.Group()
# группа метеоритов
meteorite_sprites = pygame.sprite.Group()
# группа корабля
ship_sprite = pygame.sprite.Group()
# группа аптечек
heal_sprites = pygame.sprite.Group()
# группа препятствия сломанный корабль
broken_ship_sprites = pygame.sprite.Group()
# группа вустрелов сломанного корабля
shot_of_broken_ship_sprites = pygame.sprite.Group()


# Список с числами, которые отображают размер метеорита (на разные уровни сложности - разные списки, т.к. на легком
# уровне сложности больших метеоритов должно быть меньше, чем на высоком
# Список для легкого уровня сложности
easy_meteorite_array = [1, 1, 1, 1, 2, 2, 3]
# Список для сложного уровня
hard_meteorite_array = [1, 1, 2, 2, 2, 2, 3, 3]

min_meteorite_speed_for_easy_level = 90
max_meteorite_speed_for_easy_level = 110
# шанс на выпадения аптечки - 10%
easy_level_heal_drop = (1, 10)

min_meteorite_speed_for_hard_level = 110
max_meteorite_speed_for_hard_level = 150
# шанс на выпадения аптечки - 5%
hard_level_heal_drop = (1, 20)
# Тестовая установка уровня сложности
level = 'hardx'
if level == 'hard':
    meteorite_array = hard_meteorite_array
    min_meteorite_speed = min_meteorite_speed_for_hard_level
    max_meteorite_speed = max_meteorite_speed_for_hard_level
    generation_time = 1000
    first_point, second_point = hard_level_heal_drop
else:
    meteorite_array = easy_meteorite_array
    min_meteorite_speed = min_meteorite_speed_for_easy_level
    max_meteorite_speed = max_meteorite_speed_for_easy_level
    generation_time = 3000
    first_point, second_point = easy_level_heal_drop


# типы метеоритов
small = 'small'
meduim = 'medium'
large = 'large'

# Создание метеорита
def create_meteorite():
    meteorite_x = random.randint(1, WIDTH - 64)
    meteorite_y = 0
    meteorite_speed = random.randint(min_meteorite_speed, max_meteorite_speed)
    meteorite_size = random.choice(meteorite_array)
    # Самый маленький метеорит
    if meteorite_size == 1:
        meteorite_x = random.randint(1, WIDTH - small_asteroid_size[0])
        meteorite_hp = 10
        meteorite_damage = 10
        meteorite_image = 'small_asteroid.png'
        meteorite_type = small
        # опыт за разрушение астероида
        experience_for_kill = 100
    # Средний метеорит
    elif meteorite_size == 2:
        meteorite_x = random.randint(1, WIDTH - medium_asteroid_size[0])
        meteorite_hp = 20
        meteorite_damage = 20
        meteorite_image = 'medium_asteroid.png'
        meteorite_type = meduim
        # опыт за разрушение астероида
        experience_for_kill = 200
    elif meteorite_size == 3:
        meteorite_x = random.randint(1, WIDTH - large_asteroid_size[0])
        meteorite_hp = 50
        meteorite_damage = 30
        meteorite_image = 'large_asteroid.png'
        meteorite_type = large
        # опыт за разрушение астероида
        experience_for_kill = 300

    # new_meteorite = Meteorite(meteorite_x, meteorite_y, meteorite_speed,
    #                           meteorite_hp, meteorite_damage, meteorite_image,
    #                           experience_for_kill, meteorite_type)

    b_s = BrokenShip(meteorite_x, meteorite_y)




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


# Класс аптечек
class Heal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super(Heal, self).__init__(heal_sprites)
        self.image = load_image('heal.png')
        self.heal_count = 20
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
        # скорость аптечки
        self.v = 2

    def update(self):
        self.rect = self.rect.move(0, self.v)

        ship = pygame.sprite.spritecollideany(self, ship_sprite,
                                              collided=pygame.sprite.collide_mask)

        if not ship is None:
            heal_sprites.remove(self)
            ship.change_heal_points('+', self.heal_count)


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
    def __init__(self, x, y, speed, hp, damage, image, experience_for_kill, type):
        super().__init__(meteorite_sprites)
        self.image = load_image(image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

        self.type = type
        self.speed = speed
        self.max_hp = self.hp = hp
        self.damage = damage
        self.full_damage = True
        self.experience_for_kill = experience_for_kill

        # координата для движения (промежуточные)
        self.y_moving_coord = y

    def update(self):
        # движение корабля
        self.y_moving_coord += self.speed / FPS
        self.rect = self.rect.move(0, int(self.y_moving_coord - self.rect.y))

        # попадание выстрела корабля
        shot = pygame.sprite.spritecollideany(self, shots_sprites,
                                              collided=pygame.sprite.collide_mask)
        if not shot is None:
            shots_sprites.remove(shot)
            self.minus_hp(space_ship.get_damage())

        # столкновение с метеоритом корябля
        ship = pygame.sprite.spritecollideany(self, ship_sprite,
                                              collided=pygame.sprite.collide_mask)
        if not ship is None:
            collision_sound.play()
            meteorite_sprites.remove(self)
            ship.change_heal_points('-', self.damage)

        if self.hp <= self.max_hp / 2:
            # Если метеорит разьился на мелкие кусочки, то его урон снижается вдвое
            if self.full_damage:
                self.damage //= 2
                self.full_damage = False

            if self.type == large:
                self.image = load_image('large_asteroid_half_hp.png')
            else:
                self.image = load_image('asteroid_half_hp.png')
            self.mask = pygame.mask.from_surface(self.image)

    """Метод, для уменьшеня количества hp при попадании"""

    def minus_hp(self, value):
        self.hp -= value

        if self.hp <= 0:
            # выпадение хилки
            # first_point = second_point = 2  # 100% шанс
            if random.randint(first_point, second_point) == 2:
                # размер картинки хилки 40*40
                Heal((self.image.get_rect()[2] - 40) // 2 + self.rect.x, self.rect.y)

            # когда метеорит разрушается то он удалается
            meteorite_sprites.remove(self)

    """Метод для получения информации о метеорите"""

    def get_information(self):
        return self.rect.x, self.rect.y, self.speed, self.hp

    """Метод, наносящий урон"""

    def get_damage(self):
        return self.damage

    def get_experience(self):
        return self.experience_for_kill


class ShotOfBrokenShip(pygame.sprite.Sprite):
    def __init__(self, x, y, type_shot, ship_speed):
        super().__init__(shot_of_broken_ship_sprites)
        self.image = load_image(f'enemy_shot_round_{str(type_shot)}.png')
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 110
        # скорость корабля
        self.ship_speed = ship_speed
        # дамаг при попадании высрела
        self.damage = 10
        # тип выстрела (откуда идет)
        self.type_shot = type_shot

        # координата для движения
        self.y_moving_coord = y
        self.x_moving_coord = x

    def update(self):
        # движение
        if self.type_shot == 0:
            self.y_moving_coord -= self.speed / FPS

        elif self.type_shot == 1:
            self.y_moving_coord -= sin(radians(18)) * self.speed / FPS
            self.x_moving_coord += cos(radians(18)) * self.speed / FPS

        elif self.type_shot == 2:
            self.y_moving_coord -= sin(radians(-54)) * self.speed / FPS
            self.x_moving_coord += cos(radians(-54)) * self.speed / FPS

        elif self.type_shot == 3:
            self.y_moving_coord -= sin(radians(234)) * self.speed / FPS
            self.x_moving_coord += cos(radians(234)) * self.speed / FPS

        elif self.type_shot == 4:
            self.y_moving_coord -= sin(radians(162)) * self.speed / FPS
            self.x_moving_coord += cos(radians(162)) * self.speed / FPS

        if self.type_shot != 0:
            self.y_moving_coord += self.ship_speed / FPS  # учитывается скорость движения корабля
        self.rect = self.rect.move(int(self.x_moving_coord - self.rect.x), int(self.y_moving_coord - self.rect.y))

        # удаление
        if self.rect.x > WIDTH or self.rect.y > HEIGHT:
            shot_of_broken_ship_sprites.remove(self)

        # побадание в гг корябль
        ship = pygame.sprite.spritecollideany(self, ship_sprite,
                                              collided=pygame.sprite.collide_mask)
        if not ship is None:
            shot_of_broken_ship_sprites.remove(self)
            ship.change_heal_points('-', self.damage)


class BrokenShip(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(broken_ship_sprites)
        self.image = load_image('Broken_ship.png')
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.speed = 80
        self.hp = 55
        # дамаг при столкновениии с конструкцией
        self.damage = 40
        # координата y для движения
        self.y_moving_coord = y

        # отсчет выстрелов
        self.clock_self = pygame.time.Clock()
        self.shot_time = 1000  # каждые shot_time миллисекунд удет выстрел
        self.time_past = self.clock_self.tick()  # время прошло с предыдущего выстрела

        # определяет откуда стреляет
        # отсчитывается по часовой стрелки с верхней пушки - 0
        # всего их 5 => 0-4
        self.type_shot = random.randrange(1, 5)

    def update(self):
        # движение корабля
        self.y_moving_coord += self.speed / FPS
        self.rect = self.rect.move(0, int(self.y_moving_coord - self.rect.y))

        # отсчет выстрелов
        tick = self.clock_self.tick()
        self.time_past += tick
        if self.time_past // self.shot_time > 0:
            self.time_past = self.time_past % tick
            self.shoot(self.type_shot)
            self.type_shot = (self.type_shot + 1) % 5

        if self.rect.y > HEIGHT:
            broken_ship_sprites.remove(self)

        # побадание в гг корябль
        ship = pygame.sprite.spritecollideany(self, ship_sprite,
                                              collided=pygame.sprite.collide_mask)
        if not ship is None:
            broken_ship_sprites.remove(self)
            ship.change_heal_points('-', self.damage)


    # стрельба
    def shoot(self, type_shot):
        a = self.image.get_rect()[2]  # сторона картинки корабля

        if type_shot == 0:
            image_shot = load_image('enemy_shot_round_0.png')
            x_shot = self.rect.x + self.image.get_rect()[2] // 2 - image_shot.get_rect()[2] // 2
            y_shot = self.rect.y - image_shot.get_rect()[3]

        elif type_shot == 1:
            image_shot = load_image('enemy_shot_round_1.png')
            x_shot = self.rect.x + round(a * 88 / 90)
            y_shot = self.rect.y + round(a * 32 / 90) - round(image_shot.get_rect()[3] * 20 / 26)

        elif type_shot == 2:
            x_shot = self.rect.x + round(a * 72 / 90)
            y_shot = self.rect.y + round(a * 8 / 9)

        elif type_shot == 3:
            image_shot = load_image('enemy_shot_round_3.png')
            x_shot = self.rect.x + round(a * 2 / 9) - image_shot.get_rect()[2]
            y_shot = self.rect.y + round(a * 8 / 9)

        elif type_shot == 4:
            image_shot = load_image('enemy_shot_round_4.png')
            x_shot = self.rect.x + round(a * 4 / 90) - image_shot.get_rect()[2]
            y_shot = self.rect.y + round(a * 32 / 90) - round(image_shot.get_rect()[3] * 20 / 26)

        shot_of_broken_ship_sprites.add(ShotOfBrokenShip(x_shot, y_shot, self.type_shot, self.speed))



# Создание экземпляра класса SpaceShip
# Аргументы: Скоргость, hp, урон
space_ship = SpaceShip(10, 100, 5)
ship_sprite.add(space_ship)
movement_x = movement_y = 0

# Создание события при которм появляются метеориты
METEORITEGENERATION = pygame.USEREVENT + 1
pygame.time.set_timer(METEORITEGENERATION, generation_time)

running = True
while running:
    score = 0
    # Задний фон
    background = Background("space_1.png", [0, 0])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # пауза
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print('pause')
                pause_screen()
        # Создание метеорита с случайными положением, радиусом, скоростью и коd-dвом hp
        elif event.type == METEORITEGENERATION:
            '''new_meteorite = Meteorite(random.randint(1, WIDTH - 64), 0, random.randint(1, 6), random.randint(5, 15))
            meteorite_sprites.add(new_meteorite)'''
            create_meteorite()
        # Вызов функции, производящей выстрел
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            space_ship.shoot()
        # движение
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                movement_y = -step
            elif event.key == pygame.K_s:
                movement_y = step
            if event.key == pygame.K_d:
                movement_x = step
            elif event.key == pygame.K_a:
                movement_x = -step
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
    ship_sprite.update()

    heal_sprites.draw(screen)
    heal_sprites.update()

    broken_ship_sprites.draw(screen)
    broken_ship_sprites.update()

    shot_of_broken_ship_sprites.draw(screen)
    shot_of_broken_ship_sprites.update()

    pygame.display.flip()
    clock.tick(FPS)
