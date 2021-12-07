import pygame
import random


# Класс корабля
class SpaceShip:
    def __init__(self, size, speed, bullet_speed, hp):
        self.size = size
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.bullet_speed = bullet_speed
        self.bullet_list = []
        self.x = 275
        self.y = 400

    """Метод отрисовки корабля"""
    def render(self):
        pygame.draw.rect(screen, pygame.Color('white'), (self.x, self.y, self.size, self.size))
        for bullet in self.bullet_list:
            pygame.draw.circle(screen, pygame.Color('red'), bullet, 5)
            bullet[1] -= self.bullet_speed
            if bullet[-1] <= 0:
                self.bullet_list.remove(bullet)

    """Метод для изменения координат корабля"""
    def move(self, movement_x, movement_y):
        self.x = self.x + self.speed * movement_x
        self.y = self.y + self.speed * movement_y

    """Метод, возвращяющий координаты корабля"""
    def get_cords(self):
        return self.x, self.y

    """Метод, возвращающий размер корабля"""
    def get_size(self):
        return self.size

    """Метод, устанавливающий координаты"""
    def set_cords(self, x, y):
        self.x = x
        self.y = y

    """Метод, позволяющий стрелять"""
    def shoot(self):
        self.bullet_x = self.x + self.size // 2
        self.bullet_y = self.y + self.size // 2
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


# Класс припятствий
class Meteorite:
    def __init__(self, x, y, rad, speed, hp):
        self.x = x
        self.y = y
        self.rad = rad
        self.speed = speed
        self.hp = hp
        self.damage = 10

    """Метод, для уменьшеня количества hp при попадании"""
    def minus_hp(self, value):
        self.hp -= value

    """Метод для получения информации о метеорите"""
    def get_information(self):
        return self.x, self.y, self.rad, self.speed, self.hp

    """Изменение положения метеорита"""
    def move(self):
        self.y += self.speed

    """Метод, наносящий урон"""
    def get_damage(self):
        return self.damage


if __name__ == '__main__':
    running = True
    pygame.init()
    pygame.display.set_caption('Сквозь миры со скоростью света')
    size = width, height = 400, 600
    screen = pygame.display.set_mode(size)
    # Создание экземпляра класса SpaceShip
    space_ship = SpaceShip(50, 3, 5, 100)
    movement_x = 0
    movement_y = 0
    fps = 60
    clock = pygame.time.Clock()
    # Список с метеоритами
    meteorite_list = []
    # Создание события при которм появляются метеориты
    METEORITEGENERATION = pygame.USEREVENT + 1
    pygame.time.set_timer(METEORITEGENERATION, 3000)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Обработка нажатий на клавиатуру
            if event.type == pygame.KEYDOWN:
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
            # Вызов функции, производящей выстрел
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                space_ship.shoot()
            # Создание метеорита с случайными положением, радиусом, скоростью и кол-вом hp
            if event.type == METEORITEGENERATION:
                new_meteorite = Meteorite(random.randint(40, 360), 0, random.randint(30, 50), random.randint(5, 20),
                                          random.randint(40, 70))
                meteorite_list.append(new_meteorite)
        # Условия, непозволяющие кораблю выйти за пределы поля
        if space_ship.get_cords()[0] <= 0:
            space_ship.set_cords(1, space_ship.get_cords()[1])
        if space_ship.get_cords()[1] <= 0:
            space_ship.set_cords(space_ship.get_cords()[0], 1)
        if space_ship.get_cords()[0] >= 400 - space_ship.get_size():
            space_ship.set_cords(400 - space_ship.get_size(), space_ship.get_cords()[1])
        if space_ship.get_cords()[1] >= 600 - space_ship.get_size():
            space_ship.set_cords(space_ship.get_cords()[0], 599 - space_ship.get_size())
        space_ship.move(movement_x, movement_y)
        screen.fill((0, 0, 0))
        # Отрисовка метеоритов и корабля
        for meteorite in meteorite_list:
            meteorite_x, meteorite_y, meteorite_rad, meteorite_speed, meteorite_hp = meteorite.get_information()
            pygame.draw.circle(screen, pygame.Color('grey'), (meteorite_x, meteorite_y), meteorite_rad)
            meteorite.move()
            if space_ship.get_cords()[1] == meteorite_y:
                space_ship.change_heal_points('-', meteorite.get_damage())
                print(space_ship.get_hp())
        space_ship.render()
        pygame.display.flip()
        clock.tick(fps)
