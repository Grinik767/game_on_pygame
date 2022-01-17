import pygame
from Const import const
from Sprites import Bullet, Apple
import pygame

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
throw = pygame.mixer.Sound("sounds/throw.wav")
throw.set_volume(0.3)


def set_cords_for_bullet(player):
    if player.facing == 1:
        x = player.rect.x + player.width // 2
        y = player.rect.y + player.height // 2
    else:
        x = player.rect.x + 100 - player.width // 2
        y = player.rect.y + player.height // 2
    return x, y


def set_facing(player):
    if player.lastMove == "right":
        player.facing = 1
    else:
        player.facing = -1


def add_bullet_with_range(player, bullet, dist=const.total_lvl_width):  # Перемещение пули с учетом границ окна
    if bullet.speed > 0:
        if bullet.rect.x - bullet.start_cords[0] < dist:
            bullet.rect.x += bullet.speed
        else:
            player.bullets.pop(player.bullets.index(bullet))
            bullet.kill()
    elif bullet.speed < 0:
        if bullet.start_cords[0] - bullet.rect.x < dist:
            bullet.rect.x += bullet.speed
        else:
            player.bullets.pop(player.bullets.index(bullet))
            bullet.kill()


def add_bullet_with_distance(player, x, y, dist=0):  # Устанока дистанции между выпущенными пулями
    if player in const.stickmans:
        bullet = Apple
    else:
        bullet = Bullet

    if player.lastMove == "right":
        if x + dist <= player.bullets[-1].rect.x or x - dist >= player.bullets[-1].rect.x and player.bullets[
            -1].speed < 0:
            player.bullets.append(bullet(all_bullets, (x, y), 25, player.facing))
    elif player.lastMove == "left":
        if x - dist >= player.bullets[-1].rect.x or x + dist <= player.bullets[-1].rect.x and player.bullets[
            -1].speed > 0:
            player.bullets.append(bullet(all_bullets, (x, y), 25, player.facing))


def check_over_wall_bullets(const, bullet, platforms):
    # Проверка выхода пули за границы экрана
    if 0 > bullet.rect.x or bullet.rect.x + bullet.radius > const.total_lvl_width:
        return True
    for pl in platforms:
        # Проверка на столкновение с платформой
        if (pl.rect.x < bullet.rect.x + bullet.radius * 2 < pl.rect.x + pl.width + bullet.radius * 2 and
                pl.rect.y < bullet.rect.y + bullet.radius * 2 < pl.rect.y + pl.height + bullet.radius * 2):
            return True
    return False


def check_in_wall_bullets(cords, platforms):
    x, y = cords
    for pl in platforms:
        if (pl.rect.x < x + 25 * 2 < pl.rect.x + pl.width + 25 * 2 and
                pl.rect.y < y + 25 * 2 < pl.rect.y + pl.height + 25 * 2):
            return True
    return False


def player_shooting(keys, player, platforms):
    if keys[pygame.K_SPACE]:
        set_facing(player)
        if len(player.bullets) < 10:  # Ограничение кол-ва пуль на экране
            x, y = set_cords_for_bullet(player)
            if not check_in_wall_bullets((x, y), platforms):
                flag = len(player.bullets)
                if bool(player.bullets):
                    # Добавление пули c некоторым расстоянием после поледней
                    add_bullet_with_distance(player, x, y,
                                             dist=37)
                else:
                    # Добавление первой пули
                    player.bullets.append(Bullet(all_bullets, (x, y), 25, player.facing))
                if flag < len(player.bullets):
                    throw.play()


def stickman_shooting(stickman, platforms):
    player = const.personages[0]
    set_facing(stickman)
    x, y = set_cords_for_bullet(stickman)

    if ((stickman.facing == -1 and player.rect.x + player.width * 3 > stickman.rect.x > player.rect.x or
         stickman.facing == 1 and stickman.rect.x + player.width * 3 > player.rect.x > stickman.rect.x) and
            (player.rect.y < y + 25 < player.rect.y + player.height - 25)):

        if len(stickman.bullets) < 5:  # Ограничение кол-ва пуль на экране
            if not check_in_wall_bullets((x, y), platforms):
                flag = len(stickman.bullets)

                if bool(stickman.bullets):
                    # Добавление пули c некоторым расстоянием после поледней
                    add_bullet_with_distance(stickman, x, y,
                                             dist=60)
                else:
                    # Добавление первой пули
                    stickman.bullets.append(Apple(all_bullets, (x, y), 25, stickman.facing))
                if flag < len(stickman.bullets):
                    throw.play()


def shooting(keys, player, platforms):
    for bullet in player.bullets:
        # Проверка выхода пули на столкновения
        if not check_over_wall_bullets(const, bullet, platforms):
            add_bullet_with_range(player, bullet, 700)
        else:
            player.bullets.pop(player.bullets.index(bullet))
            bullet.kill()

    if player.name == "player":
        player_shooting(keys, player, platforms)

    elif player.name == 'shooting stickman':
        stickman_shooting(player, platforms)


all_bullets = pygame.sprite.Group()
