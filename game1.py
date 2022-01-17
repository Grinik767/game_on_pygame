import pygame
import sys
import os
import json
from random import randint, randrange
from Sprites import walkRight, walkRight_red, walkRight_blue, subjects, Subject, Heart, Barrel, all_platforms, \
    Personage, Stickman, create_particles, stars, Platform, Floor, Coin, ShootingStickman, BigShootingStickman
from Subjects import check_touching
from Const import Const
from Shooting import shooting, all_bullets
from Camera import Camera, camera_configure


def set_player_pos_with_considering_touchable(is_jump=False, is_discarding=False):
    touch, pl = check_touching(player, all_platforms)

    # Установка позиции для игрока, если он запрыгивает на платформу
    if is_jump:
        if touch == "Верх" and player.jumpCount < 1:
            set_default_jump_params(player)
            player.set_cords(player.rect.x, pl.rect.y - player.height + pl.height)

    # Установка позиции для игрока, если стикмен откидывает его на платформу
    elif is_discarding:
        if touch == "Верх" and player.discardingCount < 1:
            set_default_discarding_params(player)
            player.set_cords(player.rect.x, pl.rect.y - player.height + pl.height)

    else:
        # Установка позиции для игрока, если он ходит по платформе
        if touch == "Верх":
            player.set_cords(player.rect.x, pl.rect.y - player.height)

        # Установка позиции для игрока, если он падает
        elif touch == "Нет касания":
            player.set_cords(player.rect.x, player.rect.y + player.speed * 2)


# Прыжок стоя на месте (зажаты кнопки "A" и "D")
def stand_jump(player):
    if player.jumpCount < 0:
        player.set_cords(player.rect.x, player.rect.y + (player.jumpCount ** 2) / 3)
    else:
        player.set_cords(player.rect.x, player.rect.y - (player.jumpCount ** 2) / 3)
    player.jumpCount -= 1


# Прыжок, если игрок последний раз смотрел направо
def right_jump(player, dist=0):
    if player.jumpCount < 0:
        player.set_cords(player.rect.x + dist, player.rect.y + (player.jumpCount ** 2) / 3)
    else:
        player.set_cords(player.rect.x + dist, player.rect.y - (player.jumpCount ** 2) / 3)
    player.jumpCount -= 1


# Прыжок, если игрок последний раз смотрел налево
def left_jump(player, dist=0):
    if player.jumpCount < 0:
        player.set_cords(player.rect.x - dist, player.rect.y + (player.jumpCount ** 2) / 3)
    else:
        player.set_cords(player.rect.x - dist, player.rect.y - (player.jumpCount ** 2) / 3)
    player.jumpCount -= 1


def jump(player, dist):
    set_player_pos_with_considering_touchable(is_jump=True)
    if player.jumpCount >= -13:
        if player.stand:
            stand_jump(player)
        elif player.lastMove == "right":
            right_jump(player, dist)
        elif player.lastMove == "left":
            left_jump(player, dist)
    else:
        set_default_jump_params(player)
    check_over_wall(player)


pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
const = Const
pygame.mouse.set_visible(False)

# Создание окна
width = const.width
height = const.height
win = pygame.display.set_mode((width, height))

# Название окна
pygame.display.set_caption("Рейнджер-спасатель")


def move_stickmans():
    for stickman in const.stickmans:
        if check_over_wall_stickman(stickman) == "left":
            set_right(stickman)
        elif check_over_wall_stickman(stickman) == "right":
            set_left(stickman)

        if stickman.facing == 1:
            set_right(stickman)
            stickman.rect.x += stickman.speed
        else:
            set_left(stickman)
            stickman.rect.x -= stickman.speed


def move_player():
    if not check_key_r_and_l():
        check_key_r()
        check_key_l()

    if not player.isJump:
        set_player_pos_with_considering_touchable()

        if keys[pygame.K_w] and check_touching(player, all_platforms)[0] == "Верх":
            player.isJump = True
    else:
        jump(player, 5)
    check_over_wall(player)


def set_right(personage):
    personage.right = True
    personage.left = False
    personage.stand = False
    personage.lastMove = "right"
    personage.facing = 1


def set_left(personage):
    personage.right = False
    personage.left = True
    personage.stand = False
    personage.lastMove = "left"
    personage.facing = -1


def set_stand(personage):
    personage.stand = True
    personage.right = False
    personage.left = False


def set_default_jump_params(personage):
    personage.isJump = False
    personage.jumpCount = 13


def check_over_wall(personage):
    # Если игрок не пойми где находится за экраном
    if const.total_lvl_height < personage.rect.y and 0 > personage.rect.x > const.total_lvl_width:
        x, y = personage.lastpos
        personage.set_cords(x, y)

    # Если игрок пытается уйти за левую стену
    if personage.rect.x < 0:
        personage.set_cords(0, personage.rect.y)

    # Если игрок пытается уйти за правую стену
    elif personage.rect.x + personage.width > const.total_lvl_width:
        personage.set_cords(const.total_lvl_width - personage.width, personage.rect.y)

    # Если игрок пытается уйти вниз под экран
    elif personage.rect.y + personage.height > const.total_lvl_height:
        personage.set_cords(personage.rect.x, const.total_lvl_height - personage.height - Floor.height)


def check_over_wall_stickman(personage):
    x1, x2 = personage.left_border, personage.right_border

    if personage.rect.x < x1:  # Если стикмен пытается уйти за левую стену
        return "left"

    elif personage.rect.x > x2 - personage.width:  # Если стикмен пытается уйти за правую стену
        return "right"


def check_key_l():  # Установка позиции игрока, если нажата кнопка "A"
    if keys[pygame.K_a]:
        set_left(player)
        player.set_cords(player.rect.x - player.speed, player.rect.y)
    else:
        player.left = False


def check_key_r():  # Установка позиции игрока, если нажата кнопка "D"
    if keys[pygame.K_d]:
        set_right(player)
        player.set_cords(player.rect.x + player.speed, player.rect.y)
    else:
        player.right = False


def check_key_r_and_l():  # Установка позиции игрока, если нажаты кнопки "A" и "D" вместе
    if keys[pygame.K_d] and keys[pygame.K_a]:
        set_stand(player)
        return True
    else:
        player.stand = False
        return False


def set_last_pos():
    for per in const.personages:
        if per.rect.x > 0 and per.rect.y > 0:
            per.lastpos = (per.rect.x, per.rect.y)


def moves():
    move_stickmans()
    move_player()
    set_last_pos()


def terminate():
    with open('settings.json', 'w', encoding='utf-8') as f:
        if tick_sound:
            json_file['MUSIC'] = True
        else:
            json_file['MUSIC'] = False
        data = {'settings': json_file}
        json.dump(data, f)
    with open('stats.json', 'w', encoding='utf-8') as f:
        data = {'stats': stats}
        json.dump(data, f)
    pygame.quit()
    sys.exit()


def load_image(name):
    fullname = os.path.join('subjects', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def rotate(image, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    return rotated_image


background = load_image("background_menu_1.jpg")
font_menu = pygame.font.Font(pygame.font.match_font('impact'), 50)
with open('settings.json', 'r', encoding='utf-8') as f:
    json_file = json.load(f)['settings']
    tick_sound = json_file['MUSIC']

clock = pygame.time.Clock()


def good_time(secs):
    hours = str(int(secs // 3600)).rjust(2, '0')
    mins = str(int((secs % 3600) // 60)).rjust(2, '0')
    secs = str(int((secs % 3600) % 60)).rjust(2, '0')

    return f"{hours}:{mins}:{secs}"


def start_menu():
    all_sprites = pygame.sprite.Group()
    cursor = load_image("arrow.png")
    cur = pygame.sprite.Sprite(all_sprites)
    cur.image = cursor
    cur.rect = cur.image.get_rect()
    cur.rect.x = 0
    cur.rect.y = 0
    running = True

    font_title = pygame.font.Font(pygame.font.match_font('impact'), 100)
    text_title = font_title.render("Рейнджер-спасатель", True, (255, 255, 255))

    text_menu_1 = font_menu.render("Играть", True, (255, 255, 255))
    rect_m1 = pygame.Rect(80, 245, text_menu_1.get_width() + 40, text_menu_1.get_height() + 15)
    color1 = 3
    text_menu_2 = font_menu.render("Настройки", True, (255, 255, 255))
    rect_m2 = pygame.Rect(80, 345, text_menu_2.get_width() + 40, text_menu_2.get_height() + 15)
    color2 = 3
    text_menu_3 = font_menu.render("Выйти", True, (255, 255, 255))
    rect_m3 = pygame.Rect(80, 445, text_menu_3.get_width() + 40, text_menu_3.get_height() + 15)
    color3 = 3
    if tick_sound:
        pygame.mixer.music.load("sounds/menu.mp3")
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(loops=-1, fade_ms=10)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if pygame.mouse.get_focused():
                x, y = pygame.mouse.get_pos()
                if rect_m1.x <= x <= rect_m1.x + rect_m1.width and rect_m1.y <= y <= rect_m1.y + rect_m1.height:
                    text_menu_1 = font_menu.render("Играть", True, (0, 0, 255))
                    color1 = 10
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            choose_level()
                            if choosed_level != -1:
                                pygame.mixer.music.stop()
                                if tick_sound:
                                    pygame.mixer.music.load('sounds/level1.mp3')
                                    pygame.mixer.music.play(loops=-1, fade_ms=10)
                                return
                else:
                    text_menu_1 = font_menu.render("Играть", True, (255, 255, 255))
                    color1 = 3
                if rect_m2.x <= x <= rect_m2.x + rect_m2.width and rect_m2.y <= y <= rect_m2.y + rect_m2.height:
                    text_menu_2 = font_menu.render("Настройки", True, (0, 0, 255))
                    color2 = 10
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            menu_settings()
                            if tick_sound:
                                pygame.mixer.music.load("sounds/menu.mp3")
                                pygame.mixer.music.set_volume(0.35)
                                pygame.mixer.music.play(loops=-1, fade_ms=10)
                            else:
                                pygame.mixer.music.stop()
                else:
                    text_menu_2 = font_menu.render("Настройки", True, (255, 255, 255))
                    color2 = 3
                if rect_m3.x <= x <= rect_m3.x + rect_m3.width and rect_m3.y <= y <= rect_m3.y + rect_m3.height:
                    text_menu_3 = font_menu.render("Выйти", True, (0, 0, 255))
                    color3 = 10
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            terminate()
                else:
                    text_menu_3 = font_menu.render("Выйти", True, (255, 255, 255))
                    color3 = 3
        if pygame.mouse.get_focused():
            x, y = pygame.mouse.get_pos()
            if x < const.width - cursor.get_width() and y < const.height - cursor.get_height():
                cur.rect.x, cur.rect.y = pygame.mouse.get_pos()

        win.blit(background, (0, 0))

        win.blit(text_title, (50, 60))
        win.blit(text_menu_1, (100, 250))
        pygame.draw.rect(win, (255, 255, 255), rect_m1, color1)
        win.blit(text_menu_2, (100, 350))
        pygame.draw.rect(win, (255, 255, 255), rect_m2, color2)
        win.blit(text_menu_3, (100, 450))
        pygame.draw.rect(win, (255, 255, 255), rect_m3, color3)
        all_sprites.draw(win)
        pygame.display.flip()


with open('stats.json', 'r', encoding='utf-8') as f:
    stats = json.load(f)['stats']

lock = load_image("lock.png")
font_for_res = pygame.font.Font(pygame.font.match_font('impact'), 40)


def get_stats(level_name):
    if stats[level_name][0] > 0:
        return font_for_res.render(f"Рекорд: {stats[level_name][0]} | Время: {good_time(stats[level_name][1])}", True,
                                   (255, 255, 255))
    return font_for_res.render("", True, (255, 255, 255))


def choose_level():
    global player, choosed_level, start_ticks, pause_ticks
    running = True
    choosed_level = -1
    all_sprites = pygame.sprite.Group()
    cursor = load_image("arrow.png")
    cur = pygame.sprite.Sprite(all_sprites)
    cur.image = cursor
    cur.rect = cur.image.get_rect()
    cur.rect.x = 0
    cur.rect.y = 0
    text_menu_1 = font_menu.render("← Назад", True, (255, 255, 255))
    rect_m1 = pygame.Rect(90, 695, text_menu_1.get_width() + 40, text_menu_1.get_height() + 15)
    color1 = 3
    text_menu_2 = font_menu.render("Уровень 1", True, (255, 255, 255))
    rect_m2 = pygame.Rect(width // 2 - text_menu_2.get_width() // 2 - 20 - 500,
                          height // 2 - text_menu_2.get_height() * 4 - 10,
                          text_menu_2.get_width() + 40, text_menu_2.get_height() + 15)

    color2 = 3
    text_menu_3 = font_menu.render("Уровень 2", True, (255, 255, 255))
    rect_m3 = pygame.Rect(rect_m2.x,
                          rect_m2.y + 100,
                          text_menu_3.get_width() + 40, text_menu_3.get_height() + 15)
    color3 = 3
    text_menu_5 = font_menu.render("Финал", True, (255, 255, 255))
    rect_m5 = pygame.Rect(rect_m2.x,
                          rect_m2.y + 200,
                          text_menu_5.get_width() + 40, text_menu_5.get_height() + 15)
    color5 = 3
    text_menu_4 = font_menu.render("Результаты", True, (255, 255, 255))

    res1 = get_stats("Уровень 1")
    res2 = get_stats("Уровень 2")
    res3 = get_stats("Финал")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if pygame.mouse.get_focused():
                x, y = pygame.mouse.get_pos()
                if rect_m1.x <= x <= rect_m1.x + rect_m1.width and rect_m1.y <= y <= rect_m1.y + rect_m1.height:
                    text_menu_1 = font_menu.render("← Назад", True, (0, 0, 255))
                    color1 = 10
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            return
                else:
                    text_menu_1 = font_menu.render("← Назад", True, (255, 255, 255))
                    color1 = 3
                if rect_m2.x <= x <= rect_m2.x + rect_m2.width and rect_m2.y <= y <= rect_m2.y + rect_m2.height:
                    text_menu_2 = font_menu.render("Уровень 1", True, (0, 0, 255))
                    color2 = 10
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            choosed_level = 1
                            player = level_1()
                            intro()
                            pygame.mixer.music.stop()
                            start_ticks = pygame.time.get_ticks()
                            pause_ticks = 0
                            return
                else:
                    text_menu_2 = font_menu.render("Уровень 1", True, (255, 255, 255))
                    color2 = 3
                if (rect_m3.x <= x <= rect_m3.x + rect_m3.width and rect_m3.y <= y <= rect_m3.y + rect_m3.height) and \
                        stats['Уровень 1'][0] > 0:
                    text_menu_3 = font_menu.render("Уровень 2", True, (0, 0, 255))
                    color3 = 10
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            choosed_level = 2
                            player = level_2()
                            pygame.mixer.music.stop()
                            start_ticks = pygame.time.get_ticks()
                            pause_ticks = 0
                            return
                else:
                    text_menu_3 = font_menu.render("Уровень 2", True, (255, 255, 255))
                    color3 = 3
                if (rect_m5.x <= x <= rect_m5.x + rect_m5.width and rect_m5.y <= y <= rect_m5.y + rect_m5.height) and \
                        stats['Уровень 2'][0] > 0:
                    text_menu_5 = font_menu.render("Финал", True, (0, 0, 255))
                    color5 = 10
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            choosed_level = 3
                            player = level_3()
                            pygame.mixer.music.stop()
                            start_ticks = pygame.time.get_ticks()
                            pause_ticks = 0
                            return
                else:
                    text_menu_5 = font_menu.render("Финал", True, (255, 255, 255))
                    color5 = 3

        if pygame.mouse.get_focused():
            x, y = pygame.mouse.get_pos()
            if x < const.width - cursor.get_width() and y < const.height - cursor.get_height():
                cur.rect.x, cur.rect.y = pygame.mouse.get_pos()
        win.blit(background, (0, 0))
        win.blit(text_menu_1, (100, 700))
        pygame.draw.rect(win, (255, 255, 255), rect_m1, color1)
        win.blit(text_menu_2,
                 (width // 2 - text_menu_2.get_width() // 2 - 500, height // 2 - (text_menu_2.get_height()) * 4))
        pygame.draw.rect(win, (255, 255, 255), rect_m2, color2)
        win.blit(text_menu_3,
                 (width // 2 - text_menu_2.get_width() // 2 - 500, height // 2 - (text_menu_2.get_height()) * 4 + 100))
        pygame.draw.rect(win, (255, 255, 255), rect_m3, color3)
        win.blit(text_menu_5,
                 (width // 2 - text_menu_2.get_width() // 2 - 500, height // 2 - (text_menu_2.get_height()) * 4 + 200))
        pygame.draw.rect(win, (255, 255, 255), rect_m5, color5)
        win.blit(text_menu_4,
                 (width // 2 - text_menu_4.get_width() // 2, height // 2 - (text_menu_2.get_height()) * 4 - 100))
        win.blit(res1, (width // 2 - text_menu_4.get_width() // 2 - 200, height // 2 - (text_menu_2.get_height()) * 4))
        win.blit(res2,
                 (width // 2 - text_menu_4.get_width() // 2 - 200, height // 2 - (text_menu_2.get_height()) * 4 + 100))
        win.blit(res3,
                 (width // 2 - text_menu_4.get_width() // 2 - 200, height // 2 - (text_menu_2.get_height()) * 4 + 200))
        if stats['Уровень 1'][0] == 0:
            win.blit(lock, (rect_m2.x, rect_m2.y + 100))
        if stats['Уровень 2'][0] == 0:
            win.blit(lock, (rect_m5.x, rect_m5.y))

        all_sprites.draw(win)
        pygame.display.flip()


def menu_settings():
    global tick_sound
    if tick_sound:
        text_tick = font_menu.render("+", True, (0, 255, 0))
    else:
        text_tick = font_menu.render("", True, (0, 255, 0))
    running = True
    all_sprites = pygame.sprite.Group()
    cursor = load_image("arrow.png")
    cur = pygame.sprite.Sprite(all_sprites)
    cur.image = cursor
    cur.rect = cur.image.get_rect()
    cur.rect.x = 0
    cur.rect.y = 0
    text_1 = font_menu.render("Музыка в игре", True, (255, 255, 255))
    rect_1 = pygame.Rect(width // 2 - 70, height // 3, 60, 60)

    text_menu_1 = font_menu.render("← Назад", True, (255, 255, 255))
    rect_m1 = pygame.Rect(90, 495, text_menu_1.get_width() + 40, text_menu_1.get_height() + 15)
    color1 = 3
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if pygame.mouse.get_focused():
                x, y = pygame.mouse.get_pos()
                if rect_m1.x <= x <= rect_m1.x + rect_m1.width and rect_m1.y <= y <= rect_m1.y + rect_m1.height:
                    text_menu_1 = font_menu.render("← Назад", True, (0, 0, 255))
                    color1 = 10
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            return
                else:
                    text_menu_1 = font_menu.render("← Назад", True, (255, 255, 255))
                    color1 = 3
                if rect_1.x <= x <= rect_1.x + rect_1.width and rect_1.y <= y <= rect_1.y + rect_1.height:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if tick_sound:
                                text_tick = font_menu.render("", True, (0, 255, 0))
                                tick_sound = False
                            else:
                                text_tick = font_menu.render("+", True, (0, 255, 0))
                                tick_sound = True
        if pygame.mouse.get_focused():
            x, y = pygame.mouse.get_pos()
            if x < const.width - cursor.get_width() and y < const.height - cursor.get_height():
                cur.rect.x, cur.rect.y = pygame.mouse.get_pos()
        win.blit(background, (0, 0))
        win.blit(text_1, (width // 2, height // 3))
        pygame.draw.rect(win, (107, 107, 107), rect_1, 0)
        win.blit(text_tick, (width // 2 - 53, height // 3))
        win.blit(text_menu_1, (100, 500))
        pygame.draw.rect(win, (255, 255, 255), rect_m1, color1)
        all_sprites.draw(win)
        pygame.display.flip()


def intro():
    intro_win = pygame.display.set_mode((width, height))
    if tick_sound:
        pygame.mixer.music.load("sounds/intro.mp3")
    all_sprites = pygame.sprite.Group()
    pl1 = walkRight[3]
    pl2 = walkRight_red[3]
    pl3 = walkRight_blue[3]
    nlo1_i = load_image('NLO_1.png')
    nlo2_i = load_image('NLO_2.png')

    per1 = pygame.sprite.Sprite(all_sprites)
    per1.image = pl1
    per1.rect = per1.image.get_rect()
    per1.rect.x = 0
    per1.rect.y = height - 300 - 57
    per2 = pygame.sprite.Sprite(all_sprites)
    per2.image = pl2
    per2.rect = per2.image.get_rect()
    per2.rect.x = 210
    per2.rect.y = height - 300 - 57
    per3 = pygame.sprite.Sprite(all_sprites)
    per3.image = pl3
    per3.rect = per3.image.get_rect()
    per3.rect.x = 420
    per3.rect.y = height - 300 - 57
    nlo1 = pygame.sprite.Sprite(all_sprites)
    nlo1.image = nlo1_i
    nlo1.rect = per1.image.get_rect()
    nlo1.rect.x = -1500
    nlo1.rect.y = -270
    nlo2 = pygame.sprite.Sprite(all_sprites)
    nlo2.image = nlo2_i
    nlo2.rect = per1.image.get_rect()
    nlo2.rect.x = 800
    nlo2.rect.y = -270

    move_player = False
    angle2 = 0
    angle3 = 0
    finish = False
    f = False
    if tick_sound:
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(start=5)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return

        intro_win.blit(subjects[0].image, (0, 0))
        intro_win.blit(const.platforms[0].image, const.platforms[0].cords)
        if not finish:
            if nlo2.rect.x - 4 > -120:
                nlo2.rect.x -= 4
            else:
                nlo1.rect.x = -120
                nlo2.rect.x = -1500
                move_player = True
            if move_player:
                if per3.rect.y - 2 > 210:
                    per3.rect.y -= 2
                    x3, y3 = per3.rect.x, per3.rect.y
                    angle3 += 3
                    per3.kill()
                    per3 = pygame.sprite.Sprite(all_sprites)
                    per3.image = rotate(pl3, angle3)
                    per3.rect = per3.image.get_rect()
                    per3.rect.x = x3
                    per3.rect.y = y3
                else:
                    per3.kill()
                if per2.rect.y - 1 > 210:
                    per2.rect.y -= 1
                    x2, y2 = per2.rect.x, per2.rect.y
                    angle2 += 2
                    per2.kill()
                    per2 = pygame.sprite.Sprite(all_sprites)
                    per2.image = rotate(pl2, angle2)
                    per2.rect = per2.image.get_rect()
                    per2.rect.x = x2
                    per2.rect.y = y2
                else:
                    finish = True
                    per2.kill()
        else:
            if not f:
                nlo2.rect.x = nlo1.rect.x
                nlo1.kill()
                f = True
            if nlo2.rect.x + 4 < 800:
                nlo2.rect.x += 4
            else:
                pygame.mixer.music.stop()
                return
        all_sprites.draw(intro_win)
        pygame.display.flip()
        clock.tick(60)


def set_default_discarding_params(personage):
    personage.isDiscarding = False
    personage.discardingCount = 14


# Откидывание игрока влево
def left_discarding(personage, dist):
    if personage.discardingCount < 0:
        personage.set_cords(personage.rect.x - dist, personage.rect.y + (personage.discardingCount ** 2) / 3)
    else:
        personage.set_cords(personage.rect.x - dist, personage.rect.y - (personage.discardingCount ** 2) / 3)
    personage.discardingCount -= 1


# Откидывание игрока вправо
def right_discarding(personage, dist):
    if personage.discardingCount < 0:
        personage.set_cords(personage.rect.x + dist, personage.rect.y + (personage.discardingCount ** 2) / 3)
    else:
        personage.set_cords(personage.rect.x + dist, personage.rect.y - (personage.discardingCount ** 2) / 3)
    personage.discardingCount -= 1


# Откидывание игрока
def discarding(personage, dist):
    set_player_pos_with_considering_touchable(is_discarding=True)
    if not player.isJump:
        if personage.discardingCount >= -14:
            if personage.discardingNapr == "right":
                right_discarding(personage, dist)
            elif personage.discardingNapr == "left":
                left_discarding(personage, dist)
        else:
            set_default_discarding_params(personage)
    check_over_wall(personage)


def check_hp():
    # Удаление персонажа, если у него нет hp
    for per in const.personages:
        if per.hp <= 0:
            const.personages.pop(const.personages.index(per))
            if per not in const.stickmans:
                per.kill()
            if per in const.stickmans:
                const.stickmans.pop(const.stickmans.index(per))
                for bullet in per.bullets:
                    bullet.kill()
                player.points += 12
                per.kill()
            if const.stickmans == [] and choosed_level == 3:
                pygame.mixer.music.stop()
                finish_game()
                finish_level("Финал")
                return

    # Вывод кол-во hp игрока, а также кол-ва очков
    font = pygame.font.Font(pygame.font.match_font('impact'), 45)
    hp_text = font.render(str(player.hp), True, (255, 255, 255))
    score_text = font.render(f"Score: {player.points}", True, (255, 255, 255))
    win.blit(hp_text, (10, 10))
    win.blit(score_text, (1600 - score_text.get_width(), 10))
    win.blit(heart.image, (70, 0))


def hits_register():
    # Попадание пули в стикмена
    for stickman in const.stickmans:
        if check_touching(stickman, player.bullets)[1]:
            bullet_hit.play()

        if check_touching(player, stickman.bullets)[1]:
            apple_hit.play()

    # Столкновение игрока со стикменом
    if not player.isDiscarding:
        player.discardingNapr, is_discarding = check_touching(player, const.stickmans)
        if is_discarding:
            damage.play()
            player.isDiscarding = True
    else:
        set_default_jump_params(player)
        discarding(player, 10)

    if check_touching(player, all_hearts)[1]:
        hp.play()

    if check_touching(player, all_coins)[1]:
        money.play()

    if check_touching(player, all_barrels)[1]:
        if choosed_level == 1:
            finish_level("Уровень 1")
        elif choosed_level == 2:
            finish_level("Уровень 2")


def finish_level(level_name):
    global player, choosed_level, start_ticks, pause_ticks

    seconds = (pygame.time.get_ticks() - start_ticks - pause_ticks) / 1000
    pygame.mixer.music.stop()
    win_s.play()
    all_sprites = pygame.sprite.Group()
    cursor = load_image("arrow.png")
    cur = pygame.sprite.Sprite(all_sprites)
    cur.image = cursor
    cur.rect = cur.image.get_rect()
    cur.rect.x = 0
    cur.rect.y = 0
    pygame.time.delay(150)
    background = load_image("background.jpg")
    text1 = font_menu.render("← Меню", True, (255, 255, 255))
    rect1 = pygame.Rect(width // 2 - 440, 710, text1.get_width() + 40, text1.get_height() + 15)
    color1 = 3

    text2 = font_menu.render("Перезапуск", True, (255, 255, 255))
    rect2 = pygame.Rect(rect1.x + rect1.width + 10, 710, text2.get_width() + 40, text2.get_height() + 15)
    color2 = 3

    text3 = font_menu.render("Сл. уровень→", True, (255, 255, 255))
    rect3 = pygame.Rect(rect2.x + rect2.width + 10, 710, text3.get_width() + 40, text3.get_height() + 15)
    color3 = 3

    rect = pygame.Rect(width // 2 - 450, 200, 905, 600)

    player.points += 50
    player.points += player.hp
    level_text = font_menu.render(f"{level_name} пройден!", True, (255, 255, 255))
    now_text = font_menu.render(f"Результат: {player.points}", True, (255, 255, 255))
    best_text = font_menu.render(f"Рекорд: {stats[level_name][0]}", True, (255, 255, 255))
    time_text = font_menu.render(f"Время: {good_time(seconds)}", True, (255, 255, 255))
    if player.points > stats[level_name][0]:
        new_record = font_menu.render("Новый рекорд!", True, (255, 255, 255))
        stats[level_name][0] = player.points
        stats[level_name][1] = seconds
    else:
        new_record = font_menu.render("", True, (255, 255, 255))
    running = True
    k = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if pygame.mouse.get_focused():
                x, y = pygame.mouse.get_pos()
                if rect1.x <= x <= rect1.x + rect1.width and rect1.y <= y <= rect1.y + rect1.height:
                    text1 = font_menu.render("← Меню", True, (255, 255, 255))
                    color1 = 10
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            win_s.stop()
                            pygame.mixer.music.stop()
                            start_menu()
                            return
                else:
                    text1 = font_menu.render("← Меню", True, (255, 255, 255))
                    color1 = 3
                if rect2.x <= x <= rect2.x + rect2.width and rect2.y <= y <= rect2.y + rect2.height:
                    text2 = font_menu.render("Перезапуск", True, (255, 255, 255))
                    color2 = 10
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            win_s.stop()
                            if level_name == 'Уровень 1':
                                player = level_1()
                            elif level_name == 'Уровень 2':
                                player = level_2()
                            else:
                                player = level_3()
                            if tick_sound:
                                pygame.mixer.music.play(loops=-1)
                            start_ticks = pygame.time.get_ticks()
                            pause_ticks = 0
                            return
                else:
                    text2 = font_menu.render("Перезапуск", True, (255, 255, 255))
                    color2 = 3
                if rect3.x <= x <= rect3.x + rect3.width and rect3.y <= y <= rect3.y + rect3.height and choosed_level != 3:
                    text3 = font_menu.render("Сл. уровень→", True, (255, 255, 255))
                    color3 = 10
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            win_s.stop()
                            if level_name == 'Уровень 1':
                                player = level_2()
                                choosed_level = 2

                            elif level_name == 'Уровень 2':
                                player = level_3()
                                choosed_level = 3
                            if tick_sound:
                                pygame.mixer.music.play(loops=-1)
                            start_ticks = pygame.time.get_ticks()
                            pause_ticks = 0
                            return
                else:
                    text3 = font_menu.render("Сл. уровень→", True, (255, 255, 255))
                    color3 = 3
        cur.rect.x, cur.rect.y = pygame.mouse.get_pos()

        if k < 60:
            create_particles((width // 2, 230))
            k += 1

        # Эффект паузы
        win.blit(background, (0, 0))
        animation()

        stars.draw(win)
        stars.update()

        win.blit(level_text, (width // 2 - level_text.get_width() // 2, 220))
        win.blit(now_text, (width // 2 - now_text.get_width() // 2, height // 2 - now_text.get_height() + 20))
        win.blit(best_text, (width // 2 - now_text.get_width() // 2, height // 2 + best_text.get_height()))
        win.blit(time_text, (width // 2 - now_text.get_width() // 2, height // 2 - now_text.get_height() - 80))
        win.blit(new_record, (width // 2 - new_record.get_width() // 2, 700 - new_record.get_height()))
        win.blit(text1, (width // 2 - 430, 720))

        pygame.draw.rect(win, (255, 255, 255), rect1, color1)
        win.blit(text2, (width // 2 - 430 + text1.get_width() + 60, 720))
        pygame.draw.rect(win, (255, 255, 255), rect2, color2)

        pygame.draw.rect(win, (255, 255, 255), rect, 5)
        if choosed_level != 3:
            win.blit(text3, (rect3.x + 15, 720))
            pygame.draw.rect(win, (255, 255, 255), rect3, color3)

        all_sprites.draw(win)
        pygame.display.flip()
        clock.tick(60)


def animation():
    if camera_on:
        for bullet in all_bullets:
            win.blit(bullet.image, camera.apply(bullet))

        for pl in all_platforms:
            win.blit(pl.image, camera.apply(pl))

        for coin in all_coins:
            win.blit(coin.image, camera.apply(coin))

        for heart in all_hearts:
            win.blit(heart.image, camera.apply(heart))

        for barrel in all_barrels:
            win.blit(barrel.image, camera.apply(barrel))

        for stickman in all_stickmans:
            win.blit(stickman.image, camera.apply(stickman))

        for player in all_personages:
            win.blit(player.image, camera.apply(player))

    else:
        all_platforms.draw(win)
        all_coins.draw(win)
        all_hearts.draw(win)
        all_barrels.draw(win)
        all_stickmans.draw(win)
        all_personages.draw(win)
        all_bullets.draw(win)

    all_stickmans.update()
    all_personages.update()
    all_bullets.update()


all_hearts = pygame.sprite.Group()

all_barrels = pygame.sprite.Group()

all_personages = pygame.sprite.Group()

all_stickmans = pygame.sprite.Group()

all_coins = pygame.sprite.Group()


def clean_lvl():
    for player in all_personages:
        player.kill()

    for stickman in all_stickmans:
        stickman.kill()

    for barrel in all_barrels:
        barrel.kill()

    for heart in all_hearts:
        heart.kill()

    for pl in all_platforms:
        pl.kill()

    for coin in all_coins:
        coin.kill()

    for bullet in all_bullets:
        bullet.kill()


def lvl_1_add_platforms():
    Floor(all_platforms, (0, Const.height - 60))
    Floor(all_platforms, (1000, Const.height - 200))
    Floor(all_platforms, (-800, Const.height - 350))
    Floor(all_platforms, (1000, Const.height - 500))
    Floor(all_platforms, (-800, Const.height - 650))
    Floor(all_platforms, (1000, Const.height - 800))


def lvl_1_add_items():
    Heart(all_hearts, (1000, 200))
    Heart(all_hearts, (0, 400))

    Barrel(all_barrels, (1200, 200))

    for i in range(3):
        Coin(all_coins, (1250 + i * (Coin.width // 2), 620))
        Coin(all_coins, (460 + i * (Coin.width // 2), 470))
        Coin(all_coins, (1225 + i * (Coin.width // 2), 20))


def lvl_1_add_personages():
    player = Personage(all_personages, cords=(0, height - Personage.height - Floor.height), speed=10)

    stickman1 = ShootingStickman(all_stickmans, cords=(randrange(1000, 1400), 450), speed=5, left_border=1000)
    stickman2 = Stickman(all_stickmans, cords=(randrange(0, 600), 300), speed=6, right_border=800)
    stickman3 = Stickman(all_stickmans, cords=(randrange(1000, 1400), 150), speed=6, left_border=1000)
    stickman4 = Stickman(all_stickmans, cords=(randrange(0, 600), 0), speed=6, right_border=800)
    stickman5 = Stickman(all_stickmans, cords=(randrange(1000, 1400), -150), speed=6, left_border=1000)

    const.personages = [player, stickman1, stickman2, stickman3, stickman4, stickman5]
    const.stickmans = [stickman1, stickman2, stickman3, stickman4, stickman5]

    return player


def level_1():
    global camera
    clean_lvl()
    lvl_1_add_platforms()
    lvl_1_add_items()

    player = lvl_1_add_personages()

    const.total_lvl_width = 1600
    const.total_lvl_height = 900
    camera = Camera(camera_configure, const.total_lvl_width, const.total_lvl_height)
    return player


def lvl_2_add_platforms():
    Floor(all_platforms, (0, Const.height - 60))
    Floor(all_platforms, (1600, Const.height - 60))
    Floor(all_platforms, (3200, Const.height - 60))
    Floor(all_platforms, (4800, Const.height - 60))

    Platform(all_platforms, (500, Const.height - 300))
    Platform(all_platforms, (1250, Const.height - 450))
    Platform(all_platforms, (1950, Const.height - 250))
    Platform(all_platforms, (2000, Const.height - 600))
    Platform(all_platforms, (2600, Const.height - 400))
    Platform(all_platforms, (3310, Const.height - 250))
    Platform(all_platforms, (3950, Const.height - 200))
    Platform(all_platforms, (3950, Const.height - 450))
    Platform(all_platforms, (4550, 250))

    Floor(all_platforms, (2760, Const.height - 740))


def lvl_2_add_items():
    Heart(all_hearts, (2800, 400))

    Barrel(all_barrels, (3580, 80))

    for i in range(3):
        Coin(all_coins, (2100 + i * (Coin.width // 2), 230))
        Coin(all_coins, (635 + i * (Coin.width // 2), 520))

    for i in range(4):
        Coin(all_coins, (3385 + i * (Coin.width // 2), 570))

    for i in range(6):
        Coin(all_coins, (4000 + i * (Coin.width // 2), 370))


def lvl_2_add_personages():
    player = Personage(all_personages, cords=(240, 590), speed=10)
    stickman1 = ShootingStickman(all_stickmans, cords=(randint(955, 1925), height - Stickman.height - 60), speed=5,
                                 left_border=955, right_border=1925)

    stickman2 = Stickman(all_stickmans, cords=(randint(1900, 2400), 400), speed=5, left_border=1900, right_border=2400)
    stickman3 = ShootingStickman(all_stickmans, cords=(randint(3910, 4400), 450), speed=5, left_border=3910,
                                 right_border=4400)
    stickman4 = Stickman(all_stickmans, cords=(4300, -90), speed=5, left_border=2704, right_border=4360)
    stickman5 = ShootingStickman(all_stickmans, cords=(2704, -90), speed=5, left_border=2704, right_border=4360)

    const.personages = [player, stickman1, stickman2, stickman3, stickman4, stickman5]
    const.stickmans = [stickman1, stickman2, stickman3, stickman4, stickman5]

    return player


def level_2():
    global camera
    clean_lvl()
    lvl_2_add_platforms()
    lvl_2_add_items()

    player = lvl_2_add_personages()

    const.total_lvl_width = 4800
    const.total_lvl_height = 900
    camera = Camera(camera_configure, const.total_lvl_width, const.total_lvl_height)

    return player


def lvl_3_add_platforms():
    Floor(all_platforms, (0, Const.height - 60))
    Platform(all_platforms, (0, Const.height - 300))
    Platform(all_platforms, (570, Const.height - 450))
    Platform(all_platforms, (1140, Const.height - 600))
    Platform(all_platforms, (width // 2 - Platform.width // 2, Const.height - 800))


def lvl_3_add_items():
    Heart(all_hearts, (1480, Const.height - 600 - Heart.height))
    Heart(all_hearts, (100, Const.height - 300 - Heart.height))
    Heart(all_hearts, (width // 2 - Platform.width // 2 + 100, Const.height - 800 - Heart.height))
    for i in range(9):
        Coin(all_coins, (width // 2 - Platform.width // 2 + i * (Coin.width // 2), Const.height - 800 - Coin.height))


def lvl_3_add_personages():
    player = Personage(all_personages, cords=(width // 2, Const.height - 450 - Personage.height), speed=10)

    stickman1 = BigShootingStickman(all_stickmans,
                                    cords=(1200, height - BigShootingStickman.height - Floor.height),
                                    speed=10, hp=1200, damage=50)
    stickman2 = ShootingStickman(all_stickmans, cords=(1300, Const.height - 600 - ShootingStickman.height), speed=5,
                                 left_border=1140)
    stickman3 = ShootingStickman(all_stickmans, cords=(200, Const.height - 300 - ShootingStickman.height), speed=7,
                                 right_border=450)
    stickman4 = Stickman(all_stickmans,
                         cords=(width // 2 - Platform.width // 2 + 100, Const.height - 800 - Stickman.height), speed=5,
                         left_border=(width // 2 - Platform.width // 2),
                         right_border=(width // 2 - Platform.width // 2 + 450))
    stickman5 = ShootingStickman(all_stickmans, cords=(1200, height - ShootingStickman.height - Floor.height), speed=5)
    const.personages = [player, stickman1, stickman2, stickman3, stickman4, stickman5]
    const.stickmans = [stickman1, stickman2, stickman3, stickman4, stickman5]

    return player


def level_3():
    global camera
    clean_lvl()
    lvl_3_add_platforms()
    lvl_3_add_items()

    player = lvl_3_add_personages()

    const.total_lvl_width = 1600
    const.total_lvl_height = 900
    camera = Camera(camera_configure, const.total_lvl_width, const.total_lvl_height)
    return player


def finish_game():
    intro_win = pygame.display.set_mode((width, height))
    if tick_sound:
        pygame.mixer.music.load("sounds/final.mp3")
    all_sprites = pygame.sprite.Group()
    pl1 = walkRight[3]
    pl2 = walkRight_red[3]
    pl3 = walkRight_blue[3]
    nlo1_i = load_image('NLO_1.png')
    nlo2_i = load_image('NLO_2.png')

    per1 = pygame.sprite.Sprite(all_sprites)
    per1.image = pl1
    per1.rect = per1.image.get_rect()
    per1.rect.x = 700
    per1.rect.y = height - 300 - 57
    per2 = pygame.sprite.Sprite(all_sprites)
    per2.image = pl2
    per2.rect = per2.image.get_rect()
    per2.rect.x = 2000
    per2.rect.y = 0
    per3 = pygame.sprite.Sprite(all_sprites)
    per3.image = pl3
    per3.rect = per3.image.get_rect()
    per3.rect.x = 2500
    per3.rect.y = 0
    nlo1 = pygame.sprite.Sprite(all_sprites)
    nlo1.image = nlo1_i
    nlo1.rect = per1.image.get_rect()
    nlo1.rect.x = -1500
    nlo1.rect.y = -270
    nlo2 = pygame.sprite.Sprite(all_sprites)
    nlo2.image = nlo2_i
    nlo2.rect = per1.image.get_rect()
    nlo2.rect.x = 800
    nlo2.rect.y = -270

    move_player = False
    finish = False
    f = False
    if tick_sound:
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(start=20)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return

        intro_win.blit(subjects[0].image, (0, 0))
        intro_win.blit(const.platforms[0].image, const.platforms[0].cords)
        if not finish:
            if nlo2.rect.x - 4 > -120:
                nlo2.rect.x -= 4
            else:
                nlo1.rect.x = -120
                nlo2.rect.x = -1500
                move_player = True
            if move_player:
                if not f:
                    per2.rect.x = 0
                    per3.rect.x = 300 + per2.rect.width
                    per2.rect.y = 310
                    per3.rect.y = 310
                    f = True
                else:
                    if per2.rect.y + 2 < height - 300 - 57:
                        per2.rect.y += 2
                    if per3.rect.y + 1 < height - 300 - 57:
                        per3.rect.y += 1
                        finish = False
                    else:
                        finish = True
        else:
            pygame.time.wait(3000)
            pygame.mixer.music.stop()
            return

        all_sprites.draw(intro_win)
        pygame.display.flip()
        clock.tick(60)


def set_pause():
    global pause, pause_ticks
    pause_ticks = pygame.time.get_ticks()
    if tick_sound:
        pygame.mixer.music.set_volume(0.1)
    pause = True
    animation()
    win.blit(text_pause1, (400, height // 3))
    win.blit(text_pause2, (400, height // 3 + text_pause1.get_height() + 40))
    pygame.display.update()


money = pygame.mixer.Sound("sounds/получение монеток.wav")
bullet_hit = pygame.mixer.Sound("sounds/rock_hit.wav")
damage = pygame.mixer.Sound("sounds/damage.wav")
apple_hit = pygame.mixer.Sound("sounds/apple_hit.wav")
win_s = pygame.mixer.Sound("sounds/win.wav")
hp = pygame.mixer.Sound("sounds/help.wav")
damage.set_volume(0.3)
bullet_hit.set_volume(0.3)
apple_hit.set_volume(0.3)
hp.set_volume(0.05)
win_s.set_volume(0.1)

start_menu()

heart = Subject(load_image("heart_1.png"), (70, 0), (100, 100))
run = True
bg = load_image('background.jpg')
text_pause1 = font_menu.render("Чтобы выйти в меню нажмите Esc", True,
                               (255, 255, 255))
text_pause2 = font_menu.render("Чтобы продолжить игру нажмите Пробел", True,
                               (255, 255, 255))
pause = False
camera_on = True

piece = height // 3
camera = Camera(camera_configure, const.total_lvl_width, const.total_lvl_height)
while run:
    win.blit(bg, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            terminate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not pause:
                set_pause()
            elif event.key == pygame.K_SPACE and pause:
                pause_ticks = pygame.time.get_ticks() - pause_ticks
                pause = False
                if tick_sound:
                    pygame.mixer.music.set_volume(0.35)
            elif event.key == pygame.K_ESCAPE and pause:
                pause = False
                pygame.mixer.music.stop()
                start_menu()

    if not pause:
        keys = pygame.key.get_pressed()
        shooting(keys, player, all_platforms)  # Механика стрельбы
        for st in const.stickmans:
            shooting(keys, st, all_platforms)

        moves()  # Движения игрока и стикменов
        if camera_on:
            camera.update(player)
        hits_register()  # Проверка на столкновения
        animation()  # Анимация спрайтов
        check_hp()  # Проверка здоровья
        if player.hp <= 0:
            start_ticks = pygame.time.get_ticks()
            pause_ticks = 0
            if choosed_level == 1:
                player = level_1()
            elif choosed_level == 2:
                player = level_2()
            elif choosed_level == 3:
                player = level_3()
        pygame.display.update()
        clock.tick(60)
