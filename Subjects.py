from Const import Const

const = Const


# Возвращает направление в котором объект 1 соприкасается с объектом 2
def check_touching(subject, platforms):
    flag = False
    for pl in platforms:
        if subject in const.personages:
            # Проверка столкновения с пулями
            if pl.name in ['bullet', 'apple']:
                if (subject.rect.x < pl.rect.x + pl.radius * 2 < subject.rect.x + subject.width + pl.radius * 2 and
                        subject.rect.y < pl.rect.y + pl.radius * 2 < subject.rect.y + subject.height + pl.radius * 2):
                    platforms.pop(platforms.index(pl))
                    pl.kill()
                    subject.hp -= pl.damage
                    return "Пуля попала", True

            # Проверка столкновения со стикменами
            elif pl in const.stickmans:
                if (pl.rect.x + pl.width // 2 > subject.rect.x + subject.width > pl.rect.x + pl.width // 3 and
                        pl.rect.y + pl.height // 5 < subject.rect.y + subject.height < pl.rect.y + pl.height + subject.height):
                    subject.hp -= pl.damage
                    return "left", True

                elif (pl.rect.x + pl.width - pl.width // 3 > subject.rect.x > pl.rect.x + pl.width // 2 and
                      pl.rect.y + pl.height // 5 < subject.rect.y + subject.height < pl.rect.y + pl.height + subject.height):
                    subject.hp -= pl.damage
                    return "right", True

            elif pl.name in ('heart', 'barrel', 'coin'):
                if (subject.rect.x + subject.width // 2 < pl.rect.x + pl.width < subject.rect.x + subject.width and
                        subject.rect.y < pl.rect.y + pl.height < subject.rect.y + subject.height + pl.height):

                    if pl.name == 'coin':
                        subject.points += pl.count
                        pl.kill()
                        return "+монетка", True

                    elif pl.name == 'heart':
                        if subject.hp < 100:
                            if subject.hp + 50 <= 100:
                                subject.hp += pl.hp
                            else:
                                subject.hp = 100
                            pl.kill()
                            return "Здоровье повысилось", True

                    elif pl.name == 'barrel':
                        pl.kill()
                        return "Победа", True

            elif pl.name in ('platform', 'floor'):
                if (subject.lastMove == "right" and (
                        pl.rect.x < subject.rect.x + subject.width // 3 < pl.rect.x + pl.width +
                        subject.width // 3 and
                        pl.rect.y - 15 < subject.rect.y + subject.height < pl.rect.y + 20) or
                        subject.lastMove == "left" and (
                                pl.rect.x < subject.rect.x + subject.width // 1.3 < pl.rect.x + pl.width +
                                subject.width // 3 and
                                pl.rect.y - 15 < subject.rect.y + subject.height < pl.rect.y + 20)):
                    return "Верх", pl

                elif (pl.rect.x > subject.rect.x + subject.width - 100 or
                      pl.rect.x + pl.width < subject.rect.x):
                    flag = True
    if flag:
        return "Нет касания", None
    else:
        return None, None
