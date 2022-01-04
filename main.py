import pygame
import os
import sys
import random
import pygame_gui
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
# Большого Астероида
large_asteroid_size = load_image('large_asteroid.png').get_rect()[2:]

# группа выстрелов
shots_sprites = pygame.sprite.Group()
# группа метеоритов
meteorite_sprites = pygame.sprite.Group()
# группа корабля
ship_sprite = pygame.sprite.Group()
# группа аптечек
heal_sprites = pygame.sprite.Group()


# Список с числами, которые отображают размер метеорита (на разные уровни сложности - разные списки, т.к. на легком
# уровне сложности больших метеоритов должно быть меньше, чем на высоком
# Список для легкого уровня сложности
easy_meteorite_array = [1, 1, 1, 1, 2]
# Список для сложного уровня
hard_meteorite_array = [1, 2]

min_meteorite_speed_for_easy_level = 1
max_meteorite_speed_for_easy_level = 3

min_meteorite_speed_for_hard_level = 4
max_meteorite_speed_for_hard_level = 7
# Тестовая установка уровня сложности
level = 'hard'
if level == 'hard':
    meteorite_array = hard_meteorite_array
    min_meteorite_speed = min_meteorite_speed_for_hard_level
    max_meteorite_speed = max_meteorite_speed_for_hard_level
    generation_time = 1000
else:
    meteorite_array = easy_meteorite_array
    min_meteorite_speed = min_meteorite_speed_for_easy_level
    max_meteorite_speed = max_meteorite_speed_for_easy_level
    generation_time = 3000


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
    # Средний метеорит
    elif meteorite_size == 2:
        meteorite_x = random.randint(1, WIDTH - large_asteroid_size[0])
        meteorite_hp = 20
        meteorite_damage = 20
        meteorite_image = 'large_asteroid.png'

    new_meteorite = Meteorite(meteorite_x, meteorite_y, meteorite_speed,
                              meteorite_hp, meteorite_damage, meteorite_image)


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
        self.image = load_image('test_heal_image.png')
        self.heal_count = 20
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
        # скорость аптечки
        self.v = 10

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
        print('ship hp (update) -', self.hp)
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
    def __init__(self, x, y, speed, hp, damage, image) -> object:
        super().__init__(meteorite_sprites)
        self.image = load_image(image)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

        self.speed = speed
        self.max_hp = self.hp = hp
        self.damage = damage
        self.full_damage = True

    """Метод, для уменьшеня количества hp при попадании"""

    def minus_hp(self, value):
        self.hp -= value
        # степень прозрачности зависит от потерянного хп
        # self.image.set_alpha(255 * self.hp / self.max_hp)

        # когда метеорит разрушается то он удалается
        if self.hp <= 0:
            meteorite_sprites.remove(self)
            Heal(self.get_information()[0], self.get_information()[1])

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
            collision_sound.play()
            meteorite_sprites.remove(self)
            ship.change_heal_points('-', self.damage)

        if self.hp <= self.max_hp / 2:
            # Если метеорит разьился на мелкие кусочки, то его урон снижается вдвое
            if self.full_damage:
                self.damage //= 2
                self.full_damage = False
            self.image = load_image('asteroid_half_hp.png')


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

    pygame.display.flip()
    clock.tick(FPS)