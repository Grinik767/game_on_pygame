import pygame
import os
import sys
import random
from Const import Const


def load_image(name):
    fullname = os.path.join('subjects', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def set_equal_len_sprites(cords, res, cols, rows, image, sp):
    x1, y1 = cords
    width, height = res

    for y in range(cols):
        x1 = cords[0]
        for x in range(rows):
            sp.append(image.subsurface(pygame.Rect(x1, y1, width, height)))
            x1 += width
        y1 += height


class Subject:
    def __init__(self, image, cords, res):
        self.name = None
        self.x_cord, self.y_cord = cords
        self.cords = cords
        self.width, self.height = res
        self.image = image


class Heart(pygame.sprite.Sprite):
    name = 'heart'
    image = load_image("hp.png")
    width = image.get_width()
    height = image.get_height()

    def __init__(self, group, cords, hp=50):
        super().__init__(group)
        self.image = Heart.image
        self.rect = self.image.get_rect()

        self.rect.x, self.rect.y = cords
        self.hp = hp


class Coin(pygame.sprite.Sprite):
    name = 'coin'
    image = load_image("coin.png")
    width = image.get_width()
    height = image.get_height()

    def __init__(self, group, cords, count=5):
        super().__init__(group)
        self.image = Coin.image
        self.rect = self.image.get_rect()

        self.rect.x, self.rect.y = cords
        self.count = count


class Barrel(pygame.sprite.Sprite):
    name = 'barrel'
    image = load_image("barrel.png")
    width = image.get_width()
    height = image.get_height()

    def __init__(self, group, cords):
        # НЕОБХОДИМО вызвать конструктор родительского класса Sprite.
        # Это очень важно !!!
        super().__init__(group)
        self.image = Barrel.image
        self.rect = self.image.get_rect()

        self.rect.x, self.rect.y = cords


class Platform(pygame.sprite.Sprite):
    name = 'platform'
    image = load_image("platform.png")
    width = image.get_width()
    height = image.get_height()

    def __init__(self, group, cords):
        super().__init__(group)
        self.image = Platform.image
        self.rect = self.image.get_rect()

        self.rect.x, self.rect.y = cords


class Floor(Platform):
    name = 'floor'
    image = load_image("floor.png")
    width = image.get_width()
    height = image.get_height()

    def __init__(self, group, cords):
        super().__init__(group, cords)
        self.image = Floor.image


class Bullet(pygame.sprite.Sprite):
    name = 'bullet'
    sprites = []
    rocks = pygame.image.load('animation/apple_animation/pngegg.png')
    set_equal_len_sprites((0, 0), (60, 60), 4, 4, rocks, sprites)

    width = sprites[0].get_width()
    height = sprites[0].get_height()

    def __init__(self, group, cords, radius=25, facing=1, speed=12, bullet_count=0, damage=25):
        super().__init__(group)
        self.bullet_count = bullet_count
        self.image = Bullet.sprites[bullet_count]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = cords
        self.start_cords = cords

        self.radius = radius
        self.facing = facing
        self.speed = speed * facing
        self.damage = damage

    def update(self):
        if self.bullet_count + 1 >= 32:
            self.bullet_count = 0
        self.image = self.sprites[self.bullet_count // 2]
        self.bullet_count += 1


class Apple(Bullet):
    name = "apple"

    sprites = []
    huge_apples = pygame.image.load('animation/apple_animation/spin_huge_apple_right.png')
    set_equal_len_sprites((0, 0), (60, 60), 1, 17, huge_apples, sprites)

    width = sprites[0].get_width()
    height = sprites[0].get_height()


class Personage(pygame.sprite.Sprite):
    name = 'player'
    # Создание списков с фреймами
    right_sprites = []
    left_sprites = []

    walk_right = pygame.image.load('animation/walk_animation/player_right_mini.png')
    set_equal_len_sprites((0, 0), (166.666666666666, 250), 1, 8, walk_right, right_sprites)

    walk_left = pygame.image.load('animation/walk_animation/player_left_mini.png')
    set_equal_len_sprites((0, 0), (166.666666666666, 250), 1, 8, walk_left, left_sprites)

    width = left_sprites[0].get_width()
    height = left_sprites[0].get_height()

    def __init__(self, group, cords, speed, anim_count=12, hp=100):
        super().__init__(group)
        self.anim_count = anim_count
        self.image = Personage.right_sprites[7]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = cords
        self.start_cords = cords
        self.lastpos = cords
        self.speed = speed
        self.points = 0
        self.hp = hp
        self.coins = 0

        self.left = False
        self.right = False
        self.stand = True

        self.lastMove = "right"
        self.facing = 1

        self.isJump = False
        self.jumpCount = 13

        self.isDiscarding = False
        self.discardingNapr = "right"
        self.discardingCount = 14

        # Список с пулями
        self.bullets = []

    def set_cords(self, x, y):
        self.rect.x, self.rect.y = x, y

    def walk_animation(self):
        if self.left:
            self.image = self.left_sprites[self.anim_count // 6]
            self.anim_count += 1

        elif self.right:
            self.image = self.right_sprites[self.anim_count // 6]
            self.anim_count += 1

        else:
            if self.lastMove == "right":
                self.image = self.right_sprites[7]

            elif self.lastMove == "left":
                self.image = self.left_sprites[7]

    def jump_animation(self):
        if self.lastMove == "right":
            self.image = self.right_sprites[4]

        elif self.lastMove == "left":
            self.image = self.left_sprites[4]

    def update(self):
        if self.anim_count + 1 >= 48:
            self.anim_count = 0

        if self.isJump:  # Анимация при прыжке
            self.jump_animation()
        else:
            self.walk_animation()


class Stickman(Personage):
    name = 'stickman'
    # Создание списков с фреймами
    right_sprites = []
    left_sprites = []

    walk_right = pygame.image.load('animation/walk_animation/stickman_right_mini.png')
    set_equal_len_sprites((0, 0), (166.666666666666, 250), 1, 8, walk_right, right_sprites)

    walk_left = pygame.image.load('animation/walk_animation/stickman_left_mini.png')
    set_equal_len_sprites((0, 0), (166.666666666666, 250), 1, 8, walk_left, left_sprites)

    width = left_sprites[0].get_width()
    height = left_sprites[0].get_height()

    def __init__(self, group, cords, speed=8, damage=25, left_border=0, right_border=1600):
        super().__init__(group, cords, speed)
        self.damage = damage
        self.left_border = left_border
        self.right_border = right_border


class ShootingStickman(Stickman):
    name = 'shooting stickman'
    # Создание списков с фреймами
    right_sprites = []
    left_sprites = []

    walk_right = pygame.image.load('animation/walk_animation/stickman_right_minicap.png')
    set_equal_len_sprites((0, 0), (166.666666666666, 250), 1, 8, walk_right, right_sprites)

    walk_left = pygame.image.load('animation/walk_animation/stickman_left_minicap.png')
    set_equal_len_sprites((0, 0), (166.666666666666, 250), 1, 8, walk_left, left_sprites)

    width = left_sprites[0].get_width()
    height = left_sprites[0].get_height()


class BigShootingStickman(Stickman):
    name = 'shooting stickman'
    # Создание списков с фреймами
    right_sprites = []
    left_sprites = []

    walk_right = pygame.image.load('animation/walk_animation/stickman_right_boss.png')
    set_equal_len_sprites((0, 0), (216.6125, 325), 1, 8, walk_right, right_sprites)

    walk_left = pygame.image.load('animation/walk_animation/stickman_left_boss.png')
    set_equal_len_sprites((0, 0), (216.6125, 325), 1, 8, walk_left, left_sprites)

    width = left_sprites[0].get_width()
    height = left_sprites[0].get_height()

    def __init__(self, group, cords, speed=8, damage=25, left_border=0, right_border=1600, hp=100):
        super().__init__(group, cords, speed)
        self.damage = damage
        self.left_border = left_border
        self.right_border = right_border
        self.hp = hp


screen_rect = (Const.width // 2 - 450, 200, 900, 550)
stars = pygame.sprite.Group()


class Particle(pygame.sprite.Sprite):
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(stars)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = Const.gravity

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    particle_count = 30
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


# Список спрайтов анимации игрока ходьбы влево
walkRight = []
player_right = pygame.image.load('animation/walk_animation/player_right.png')
set_equal_len_sprites((0, 0), (200, 300), 1, 8, player_right, walkRight)

walkRight_red = []
player_right_red = pygame.image.load('subjects/player_right_red.png')
set_equal_len_sprites((0, 0), (200, 300), 1, 8, player_right_red, walkRight_red)

walkRight_blue = []
player_right_blue = pygame.image.load('subjects/player_right_blue.png')
set_equal_len_sprites((0, 0), (200, 300), 1, 8, player_right_blue, walkRight_blue)

# Список спрайтов анимации игрока ходьбы вправо
walkLeft = []
player_left = pygame.image.load('animation/walk_animation/player_left.png')
set_equal_len_sprites((0, 0), (200, 300), 1, 8, player_left, walkLeft)

# Список спрайтов больших яблок
# huge_apples = []
# spin_huge_apple_right = pygame.image.load('animation/apple_animation/spin_huge_apple_right.png')
# set_equal_len_sprites((0, 0), (60, 60), 17, spin_huge_apple_right, huge_apples)

# Список спрайтов маленьких яблок
tiny_apples = []
spin_tiny_apple_right = pygame.image.load('animation/apple_animation/spin_tiny_apple_right.png')
set_equal_len_sprites((0, 0), (24, 24), 1, 18, spin_tiny_apple_right, tiny_apples)

# Список спрайтов анимации ходьбы стикмана вправо
stickman_right = []
stickman_r = pygame.image.load('animation/walk_animation/stickman_right.png')
set_equal_len_sprites((0, 0), (200, 300), 1, 8, stickman_r, stickman_right)

# Список спрайтов анимации ходьбы стикмана влево
stickman_left = []
stickman_l = pygame.image.load('animation/walk_animation/stickman_left.png')
set_equal_len_sprites((0, 0), (200, 300), 1, 8, stickman_l, stickman_left)

# Др. объекты
subjects = [load_image('floor.png'), load_image('background.jpg')]

bg = Subject(subjects[1], (0, 0), (1600, 900))
all_platforms = pygame.sprite.Group()
floor = Subject(subjects[0], (0, Const.height - 60), (1600, 60))

floor1 = Subject(subjects[0], (1000, Const.height - 200), (1600, 60))

floor2 = Subject(subjects[0], (-800, Const.height - 350), (1600, 60))

floor3 = Subject(subjects[0], (1000, Const.height - 500), (1600, 60))

floor4 = Subject(subjects[0], (-800, Const.height - 650), (1600, 60))

floor5 = Subject(subjects[0], (1000, Const.height - 800), (1600, 60))

subjects = [bg, floor, floor1, floor2, floor3, floor4, floor5]

Const.platforms = [floor, floor1, floor2, floor3, floor4, floor5]

hearts = []
