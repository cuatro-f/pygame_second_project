@@ -1,6 +1,13 @@
import pygame
from pygame import mixer
import random

# инициализация плеера
mixer.init()

# звук выстрела
shot_sound = mixer.Sound('sounds\\shot.mp3')


# Класс корабля
class SpaceShip:
@@ -15,39 +22,57 @@ def __init__(self, size, speed, bullet_speed, hp):
        self.y = 400

    """Метод отрисовки корабля"""
    def render(self):

    def render(self, meteorite_arr):
        pygame.draw.rect(screen, pygame.Color('white'), (self.x, self.y, self.size, self.size))
        for bullet in self.bullet_list:
            pygame.draw.circle(screen, pygame.Color('red'), bullet, 5)
            bullet[1] -= self.bullet_speed
            for meteor in meteorite_arr:
                meteor_x, meteor_y, meteor_rad, meteor_speed, meteor_hp = meteor.get_information()
                if meteor_y - meteor_rad <= bullet[1] <= meteor_y + meteor_rad and \
                        (meteor_x - meteor_rad <= bullet[0] <= meteor_x + meteor_rad or
                            meteor_x - meteor_rad <= bullet[0] + 4 <= meteor_x + meteor_rad):
                    meteor.minus_hp(10)
                    if meteor.get_hp() <= 0:
                        meteorite_arr.remove(meteor)
                    self.bullet_list.remove(bullet)
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
        # воспроизведение звука выстрела
        shot_sound.play()

    """Метод, изменяющий hp"""

    def change_heal_points(self, action, value):
        if action == '+':
            if self.hp == self.max_hp:
@@ -60,7 +85,7 @@ def change_heal_points(self, action, value):
            self.hp -= value

    def get_hp(self):
        print(self.hp)
        return self.hp


# Класс припятствий
@@ -72,23 +97,31 @@ def __init__(self, x, y, rad, speed, hp):
        self.speed = speed
        self.hp = hp
        self.damage = 10
        self.damage_ability = True

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

    def get_hp(self):
        return self.hp


if __name__ == '__main__':
    running = True
@@ -97,7 +130,7 @@ def get_damage(self):
    size = width, height = 400, 600
    screen = pygame.display.set_mode(size)
    # Создание экземпляра класса SpaceShip
    space_ship = SpaceShip(50, 3, 5, 100)
    space_ship = SpaceShip(50, 10, 5, 100)
    movement_x = 0
    movement_y = 0
    fps = 60
@@ -135,7 +168,7 @@ def get_damage(self):
                space_ship.shoot()
            # Создание метеорита с случайными положением, радиусом, скоростью и кол-вом hp
            if event.type == METEORITEGENERATION:
                new_meteorite = Meteorite(random.randint(40, 360), 0, random.randint(30, 50), random.randint(5, 20),
                new_meteorite = Meteorite(random.randint(40, 360), 0, random.randint(30, 50), random.randint(2, 3),
                                          random.randint(40, 70))
                meteorite_list.append(new_meteorite)
        # Условия, непозволяющие кораблю выйти за пределы поля
@@ -154,9 +187,20 @@ def get_damage(self):
            meteorite_x, meteorite_y, meteorite_rad, meteorite_speed, meteorite_hp = meteorite.get_information()
            pygame.draw.circle(screen, pygame.Color('grey'), (meteorite_x, meteorite_y), meteorite_rad)
            meteorite.move()
            if space_ship.get_cords()[1] == meteorite_y:
                space_ship.change_heal_points('-', meteorite.get_damage())
                print(space_ship.get_hp())
        space_ship.render()
            if meteorite_y - meteorite_rad >= 600:
                meteorite_list.remove(meteorite)
            # проверяем, столкнулся ли корабль с метеоритом
            if meteorite_x - meteorite_rad <= space_ship.get_cords()[0] + space_ship.get_size() <= \
                    meteorite_x + meteorite_rad or meteorite_x - meteorite_rad <= space_ship.get_cords()[0] <= \
                    meteorite_x + meteorite_rad:
                if meteorite_y - meteorite_rad <= space_ship.get_cords()[1] <= meteorite_y + meteorite_rad or \
                        meteorite_y - meteorite_rad <= space_ship.get_cords()[1] + space_ship.get_size() <= \
                        meteorite_y + meteorite_rad:
                    # вычитаем из hp корабля damage метеорита
                    space_ship.change_heal_points('-', meteorite.get_damage())
                    # метеорит раскололся после столкновения с кораблем
                    meteorite_list.remove(meteorite)
                    print(space_ship.get_hp())
        space_ship.render(meteorite_list)
        pygame.display.flip()
        clock.tick(fps)