import pygame
import sys
import os
from random import randint
import pygame_widgets
from pygame_widgets.button import Button
from screeninfo import get_monitors

pygame.init()
FPS = 20
TILES_SIZE = 50
WIDTH, HEIGHT = 500, 500
TOP, LEFT = 100, 100
fight = False
# get_monitors()

TILE_IMAGES = {'0': 'data\\floor.png', '1': 'data\\wall.png', '2': 'data\\stair1.png',
               '3': 'пикс\\pixil-frame-0 (19).png', '4': 'data\\floor.png', '5': 'пикс\\pixil-frame-0 (16).png'}
ENEMIES = {'Бальтазар': [100, 70, 'пикс\\pixil-frame-0 (15).png'],
           'Мельхиор': [150, 90, 'пикс\\pixil-frame-0 (18).png'],
           'Каспар': [200, 100, 'пикс\\pixil-frame-0 (17).png'],
           'Дракон': [400, 160, 'пикс\\pixil-frame-0 (16).png']}

# создание групп спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
enemies = pygame.sprite.Group()
borders = pygame.sprite.Group()
stairs = pygame.sprite.Group()
hero_group = pygame.sprite.Group()
chests = pygame.sprite.Group()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
name = 'Alex'
MUSIC = ['data\\game.mp3', 'data\\game-over.mp3', 'data\\battle.mp3', 'data\\final.mp3', 'data\\bad_final.mp3']


class MessageHandler:  # Спасибо Егору Алтынову за помощь с простым выводом текста по очереди на экран
    def __init__(self):
        self.font = pygame.font.SysFont(None, 40)
        self.queue = []
        self.timer = 0
        self.frame_rate = 20
        self.message_time = 1.5

    def add_text(self, text, cords):
        color = (randint(100, 255), randint(100, 255), randint(100, 255))
        self.queue.append([text, cords, color])
        a = pygame.mixer.Sound('data/bonus.mp3')
        a.play()

    def blit_message(self):
        if not self.queue:
            return
        render = self.font.render(self.queue[0][0], True, self.queue[0][2])
        screen.blit(render, self.queue[0][1])

        self.timer += 1
        if self.timer >= self.frame_rate * self.message_time:
            self.timer = 0
            self.queue.pop(0)


screen_text = MessageHandler()  # элемент класса


def shoot(m, long=0):
    pygame.mixer.music.load(m)
    pygame.mixer.music.play(long)


def sweep():  # очистка групп спрайтов для работы/смены карт
    for i in all_sprites:
        i.kill()
    for i in enemies:
        i.kill()
    all_sprites.clear(screen, screen)
    tiles_group.clear(screen, screen)
    walls_group.clear(screen, screen)
    enemies.clear(screen, screen)
    stairs.clear(screen, screen)
    screen.fill((0, 0, 0))


def load_image(fname, colorkey=None):
    fullname = fname
    # если файл не существует, то выходим
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
        image = image.convert_alpha()
    return image


class BaseCharacter:  # родитель Героя и врагов
    def __init__(self, pos_x, pos_y, hp):
        self.pos_x, self.pos_y, self.hp = pos_x, pos_y, hp
        self.alive = 1

    def is_alive(self):
        if self.hp <= 0:
            self.alive = 0
            return False
        else:
            return True

    def get_damage(self, amount, defence=0):
        if self.is_alive():
            self.hp -= ((amount - defence) // 2)

    def get_cords(self):
        return self.pos_x, self.pos_y

    def get_name(self):
        return self.name

    def get_hp(self):
        return self.hp

    def get_bread(self):
        return self.bread

    def get_weapon(self):
        return self.weapon


class BaseEnemy(BaseCharacter, pygame.sprite.Sprite):  # класс врага спрайтом
    def __init__(self, pos_x, pos_y, ename, hp, damage, pict):
        pygame.sprite.Sprite.__init__(self)
        self.pos_x, self.pos_y, self.hp = pos_x, pos_y, hp
        self.image = pygame.Surface((TILES_SIZE, TILES_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos_x * TILES_SIZE + 100, pos_y * TILES_SIZE + 100
        self.alive = 1
        self.name = ename
        self.damage = damage
        self.pict = pict

    def get_info(self):
        return [f'Имя врага: {self.name}', f'Здоровье врага: {self.hp}', f'Сила удара: {self.damage}']

    def get_pict(self):
        return self.pict


class MainHero(BaseCharacter, pygame.sprite.Sprite):  # класс героя
    image = load_image("data\\MH_stay.png")

    def __init__(self, pos_x, pos_y, hp, name):
        BaseCharacter.__init__(self, pos_x, pos_y, hp)
        pygame.sprite.Sprite.__init__(self)

        self.armor = None
        self.orientation = 1
        self.image = self.image_change()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos_x
        self.rect.y = pos_y

        self.name = name
        self.bread = 0
        self.kills = 0
        self.weapon = Weapon('Кулаки', 40)
        self.defence = 0
        self.teleport_timer = 0

    def help(self):  # лечение
        if self.bread != 0:
            self.bread -= 1
            self.hp += 100
        screen_text.add_text(('Полечился, + 100 HP'), (100, 1000))

    def add_weapon(self, weapon):
        self.weapon = weapon
        screen_text.add_text(f'Подобрал {weapon}', (100, 1000))
        return

    def add_bread(self):
        self.bread += 1

    def add_armor(self, armor):
        self.armor = armor
        self.defence += armor.defence

    def get_armor(self):
        return self.armor.name if self.armor else '---'

    def check_chest(self, chest):  # проверка сундука и распределение содержимого
        if chest.stuff:
            for i in chest.stuff:
                if i == 'Bread':
                    self.add_bread()
                    screen_text.add_text('+1 хлеб', (100, 1000))
                elif type(i).__name__ == 'Weapon':
                    self.add_weapon(i)
                    screen_text.add_text(f'В инвентарь добавлено оружие: {i.name}', (100, 1000))
                elif type(i).__name__ == 'Armor':
                    self.add_armor(i)
                    screen_text.add_text(f'Вы экипировали доспех: {i.name}', (100, 1000))
            chest.stuff = []

    def set_position(self, x, y, k):  # смена координат игрока
        self.rect.x = x
        self.rect.y = y
        collide = pygame.sprite.spritecollideany(self, enemies)
        if collide:
            if collide.alive:
                return Fight(self, collide)

        collide = pygame.sprite.spritecollideany(self, chests)
        if collide:
            self.check_chest(collide)

        collide = pygame.sprite.spritecollideany(self, stairs)
        if collide and not self.teleport_timer:
            if collide.pos:
                self.rect.x = collide.pos[0]
                self.rect.y = collide.pos[1]
                self.pos_x = collide.pos[0]
                self.pos_y = collide.pos[1]
            self.teleport_timer = 20
            return collide.next_map

        if not pygame.sprite.spritecollideany(self, borders) and not pygame.sprite.spritecollideany(self, walls_group):
            if self.orientation != k and k != -1:
                self.orientation = k
                self.image = self.image_change()
            self.rect.x = x
            self.rect.y = y
            self.pos_x = x
            self.pos_y = y
            return

        self.rect.x = self.pos_x
        self.rect.y = self.pos_y

    def image_change(self):  # смена картинок в зависимости от направления игрока
        if self.orientation == 1:
            im = load_image('data\\MH_go.png')
            return pygame.transform.scale(im, (TILES_SIZE, TILES_SIZE))
        elif self.orientation == 3:
            im = load_image('data\\MH_go.png')
            im = pygame.transform.flip(im, flip_x=True, flip_y=False)
            return pygame.transform.scale(im, (TILES_SIZE, TILES_SIZE))
        elif self.orientation == 0:
            im = load_image(f'data\\MH_go{0}.png')
            return pygame.transform.scale(im, (TILES_SIZE - 15, TILES_SIZE))
        elif self.orientation == 2:
            im = load_image(f'data\\MH_go{2}.png')
            return pygame.transform.scale(im, (TILES_SIZE - 15, TILES_SIZE))


class Weapon:
    def __init__(self, name, damage):
        self.name, self.damage = name, damage

    def __str__(self):
        return self.name

    def render(self):
        pass


class Armor:
    def __init__(self, name, defence):
        self.name = name
        self.defence = defence

    def render(self):
        pass


class Chest(pygame.sprite.Sprite):  # инициализация сундука и содержимого
    def __init__(self, pos_x, pos_y, stuff):
        super().__init__(all_sprites, chests)
        self.stuff = [stuff[0]] + ['Bread'] * stuff[1]
        image = load_image(TILE_IMAGES['3'])
        self.image = pygame.transform.scale(image, (TILES_SIZE, TILES_SIZE))
        self.rect = self.image.get_rect().move(
            TILES_SIZE * pos_x + TOP, TILES_SIZE * pos_y + LEFT)


class Stair(pygame.sprite.Sprite):  # инициализация лестницы и места, куда она ведет
    def __init__(self, pos_x, pos_y, next_map, pos=None):
        super().__init__(tiles_group, all_sprites)
        self.next_map = next_map
        self.pos = pos
        image = load_image(TILE_IMAGES['2'])
        self.image = pygame.transform.scale(image, (TILES_SIZE, TILES_SIZE))
        self.rect = self.image.get_rect().move(
            TILES_SIZE * pos_x + TOP, TILES_SIZE * pos_y + LEFT)


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(borders)
        if x1 == x2:  # вертикальная стенка
            self.add(borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.image.fill((0, 0, 0))
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.image.fill((0, 0, 0))
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Board:
    # создание поля
    def __init__(self, width, height, filename):
        self.selected_map = None
        self.width = width
        self.height = height
        self.board = self.load_level(filename)

        # значения по умолчанию
        self.left = 0
        self.top = 0
        self.cell_size = 20

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # загрузка уровня
    def load_level(self, filename):
        filename = filename
        self.selected_map = filename
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        return level_map

    def create_borders(self):
        Border(self.left, self.top,
               self.left, TILES_SIZE * self.height + self.top)
        Border(self.left, self.top,
               TILES_SIZE * self.width + self.left, self.top)
        Border(self.left + TILES_SIZE * self.width, self.top,
               self.left + TILES_SIZE * self.width, TILES_SIZE * self.height + self.top)
        Border(self.left, self.top + TILES_SIZE * self.height,
               self.left + TILES_SIZE * self.width, self.top)

    # расшифровка карт и расположение объектов на карте
    def render(self, level):
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '0':
                    Tile('0', x, y)
                elif level[y][x] == '1':
                    walls_group.add(Tile('1', x, y))

                elif level[y][x] == 'q':
                    stairs.add(Stair(x, y, 'map1.txt'))

                elif level[y][x] == 'w':
                    stairs.add(Stair(x, y, 'map2.txt'))

                elif level[y][x] == 'e':
                    stairs.add(Stair(x, y, 'map3.txt'))

                elif level[y][x] == 'r':
                    stairs.add(Stair(x, y, 'map4.txt', pos=(200, 500)))

                elif level[y][x] == 'H':
                    Tile('0', x, y)
                    Chest(x, y, [Armor('Шлем', 30), randint(0, 2)])

                elif level[y][x] == 'V':
                    Tile('0', x, y)
                    Chest(x, y, [None, randint(0, 5)])

                elif level[y][x] == 'S':
                    Tile('0', x, y)
                    Chest(x, y, [Weapon('Меч', 60), randint(0, 2)])

                elif level[y][x] == 'P':
                    Tile('0', x, y)
                    Chest(x, y, [Weapon('Реликвия Злотая сковородка', 100), randint(0, 2)])

                elif level[y][x] == 'M':
                    enemies.add(BaseEnemy(x, y, 'Мельхиор', *ENEMIES['Мельхиор']))
                    Tile('0', x, y)

                elif level[y][x] == 'B':

                    enemies.add(BaseEnemy(x, y, 'Бальтазар', *ENEMIES['Бальтазар']))
                    Tile('0', x, y)

                elif level[y][x] == 'C':

                    enemies.add(BaseEnemy(x, y, 'Каспар', *ENEMIES['Каспар']))
                    Tile('0', x, y)

                elif level[y][x] == 'K':

                    enemies.add(BaseEnemy(x, y, 'Дракон', *ENEMIES['Дракон']))
                    Tile('0', x, y)
                    Tile('5', x, y)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(all_sprites)
        image = load_image(TILE_IMAGES[tile_type], colorkey=-1)
        self.image = pygame.transform.scale(image, (TILES_SIZE, TILES_SIZE))
        self.rect = self.image.get_rect().move(
            TILES_SIZE * pos_x + TOP, TILES_SIZE * pos_y + LEFT)


class Game:  # класс игры, основное действие тут
    def __init__(self, board, hero):
        self.exit_menu = False
        self.label_game = 'Новая игра'
        self.running = None
        self.board = board
        self.hero = hero
        self.k = 1

    def update_hero(self):
        if self.hero.teleport_timer:
            self.hero.teleport_timer -= 1
        next_x, next_y = self.hero.get_cords()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            next_x -= 10
            self.k = 3
        elif keys[pygame.K_RIGHT]:
            next_x += 10
            self.k = 1
        elif keys[pygame.K_UP]:
            next_y -= 10
            self.k = 0
        elif keys[pygame.K_DOWN]:
            next_y += 10
            self.k = 2

        action = self.hero.set_position(next_x, next_y, self.k)

        if type(action).__name__ == 'Fight':
            pass

        elif type(action).__name__ == 'str':
            pygame.display.flip()
            sweep()
            level = self.board.load_level(action)
            self.board.render(level)

    # проигрыш
    def game_over(self):
        shoot(MUSIC[1])
        hero_group.sprites()[0].kill()
        hero_group.clear(screen, screen)
        fon = pygame.transform.scale(load_image('пикс\\pixil-frame-0 (24).png'), screen.get_size())
        screen.blit(fon, (0, 0))
        my_font = pygame.font.SysFont(None, 110)
        my_font1 = pygame.font.SysFont(None, 270)
        text_surface = my_font1.render(f"GAME OVER!", False, (255, 0, 0))
        screen.blit(text_surface, (400, 150))
        text_surface = my_font.render(f"К сожалению у Вас осталось 0 hp!", False, (0, 0, 0))
        screen.blit(text_surface, (570, 500))
        text_surface = my_font.render(f"Попробуйте пройти игру еще раз!", False, (0, 0, 0))
        screen.blit(text_surface, (570, 700))
        self.running = True
        while self.running:
            events = pygame.event.get()
            for event in events:
                pygame_widgets.update(events)

                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    return
            pygame.display.flip()
            clock.tick(FPS)

    def menu(self):
        self.exit_menu = True

    # окно паузы & начальное меню
    def start_screen(self):
        self.exit_menu = False
        intro_text = ["Gold Pan", "", "",
                      "Правила игры",
                      "В режиме боя нажмите клавишу 'F' для атаки.",
                      "Для поднятия hp ешь хлеб! -> Нажми клавишу 'B'."]

        fon = pygame.transform.scale(load_image('data\\fon.jpg'), screen.get_size())

        load_button = Button(screen, 150, 550, 350, 100,
                             text=self.label_game,  # Text to display
                             fontSize=50,  # Size of font
                             margin=0,
                             inactiveColour=(0, 100, 255),
                             hoverColour=(255, 100, 30),
                             radius=50,  # Radius of border corners (leave empty for not curved)
                             onClick=lambda: self.menu()
                             )

        exit_button = Button(screen, 150, 700, 350, 100,
                             text='Выход из игры',  # Text to display
                             fontSize=50,  # Size of font
                             margin=0,
                             inactiveColour=(0, 100, 255),
                             hoverColour=(255, 100, 30),
                             radius=50,  # Radius of border corners (leave empty for not curved)
                             onClick=terminate
                             )

        button_group = [load_button, exit_button]

        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 50)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, True, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 70
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        self.running = True
        while self.running:
            events = pygame.event.get()
            for event in events:
                for i in button_group:
                    i.draw()
                    i.listen(events)
                pygame_widgets.update(events)
                if self.exit_menu:
                    self.label_game = 'Продолжить'
                    return

                if event.type == pygame.QUIT:
                    terminate()

            pygame.display.flip()
            clock.tick(FPS)


# класс специально для битвы
class Fight:
    def __init__(self, hero, enemy):
        self.running = None
        self.hero, self.enemy = hero, enemy
        self.fight = True
        self.live = True
        self.mix = MUSIC[2]
        self.x = 0
        if self.enemy.hp == 400:
            self.x = 1
        self.main()

    # удар игрока
    def clicked(self):
        self.enemy.get_damage(self.hero.weapon.damage)
        a = pygame.mixer.Sound('data/hit.mp3')
        a.play()
        my_font = pygame.font.SysFont(None, 100)
        text_surface = my_font.render(f"-{self.hero.weapon.damage}", False, (205, 0, 0))
        screen.blit(text_surface, (1100, 150))
        pygame.display.update()

        pygame.time.delay(500)

        if not self.enemy.is_alive():
            a = pygame.mixer.Sound('data/enemy_defeat.mp3')
            a.play()
            self.fight = False
            self.hero.kills += 1
            if self.x == 1:
                self.win()
            return

        self.hero.get_damage(self.enemy.damage, defence=self.hero.defence)
        text_surface = my_font.render(f"-{self.enemy.damage}", False, (205, 0, 0))
        screen.blit(text_surface, (500, 150))
        pygame.time.delay(500)

        if not self.hero.is_alive():
            self.fight = False
            self.hero.alive = 0

    # победа над драконом
    def win(self):
        shoot(MUSIC[1])
        fon = pygame.transform.scale(load_image('пикс\\pixil-frame-0 (24).png'), screen.get_size())
        screen.blit(fon, (0, 0))
        my_font = pygame.font.SysFont(None, 100)
        my_font1 = pygame.font.SysFont(None, 270)
        text_surface = my_font1.render(f"YOU WON!", False, (255, 0, 0))
        screen.blit(text_surface, (400, 150))
        text_surface = my_font.render(f"Поздравляем! Вы выиграли!", False, (0, 0, 0))
        screen.blit(text_surface, (570, 500))
        text_surface = my_font.render(f"Вы браво сражались.", False, (0, 0, 0))
        screen.blit(text_surface, (570, 700))
        my_font = pygame.font.SysFont(None, 100)
        text_surface = my_font.render(f"Вы убили ровно {self.hero.kills} врагов!", False, (0, 0, 0))
        screen.blit(text_surface, (570, 900))
        self.running = True

        while self.running:
            events = pygame.event.get()
            for event in events:
                pygame_widgets.update(events)
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    terminate()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    return
            pygame.display.flip()
            clock.tick(FPS)

    # сама битва
    def main(self):
        pygame.display.flip()
        screen.fill((0, 0, 0))
        my_font = pygame.font.SysFont(None, 100)
        shoot('data\\meet.mp3')
        text_surface = my_font.render('Вы наткнулись на врага!', False, (100, 0, 0))

        screen.blit(text_surface, (screen.get_width() // 2 - 400, screen.get_height() // 2 - 100))

        pygame.display.update()
        pygame.time.delay(1700)

        screen.fill((128, 128, 128))
        shoot(self.mix, -1)
        while self.fight:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    terminate()
                if pygame.key.get_pressed()[pygame.K_f]:
                    self.clicked()

            screen.fill((128, 128, 128))

            fon = pygame.transform.scale(load_image('пикс\\pixil-frame-0 (24).png'), screen.get_size())
            screen.blit(fon, (0, 0))
            hero = pygame.transform.scale(load_image('пикс\\pixil-frame-0 (8).png'), (700, 800))
            screen.blit(hero, (100, 50))
            enemy = pygame.transform.scale(load_image(self.enemy.pict), (400, 500))
            screen.blit(enemy, (1200, 150))
            my_font = pygame.font.SysFont(None, 40)
            text_surface = my_font.render(f"Осталось {self.hero.hp} hp!", False, (0, 0, 0))
            text_surface1 = my_font.render(f"Осталось {self.enemy.hp} hp!", False, (0, 0, 0))
            screen.blit(text_surface, (100, 900))
            screen.blit(text_surface1, (1200, 900))

            pygame.display.update()
            pygame.display.flip()
            clock.tick(20)
        shoot(MUSIC[0], -1)


def terminate():
    pygame.quit()
    sys.exit()


# помощник при создании новой игры
def new_game():
    sweep()
    screen.fill((0, 0, 0))
    hero = MainHero(150, 400, 100000, name)
    hero_group.add(hero)
    board = Board(33, 17, 'map4.txt')
    board.set_view(TOP, LEFT, TILES_SIZE)
    board.render(board.board)
    board.create_borders()
    game = Game(board, hero)
    return game


def main():
    shoot(MUSIC[0])

    # инициализация данной игры
    game = new_game()
    game.start_screen()

    running = True
    while running:
        for event in pygame.event.get():
            if not game.hero.alive:
                game.game_over()
                main()
                terminate()
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.start_screen()
            if pygame.key.get_pressed()[pygame.K_b]:
                game.hero.help()

        screen.fill((0, 0, 0))
        game.update_hero()

        borders.draw(screen)
        all_sprites.draw(screen)
        hero_group.draw(screen)
        text = pygame.transform.scale(load_image('пикс\\pixil-frame-0 (26).png'), (780, 150))
        my_font = pygame.font.SysFont(None, 40)
        screen.blit(text, (950, 800))
        text_surface = my_font.render(
            f'Name: {game.hero.get_name()}, HP: {game.hero.get_hp()}, Bread: {game.hero.get_bread()}',
            False, (0, 0, 0))
        text_surface1 = my_font.render(f' Weapon: {game.hero.get_weapon()}', False, (0, 0, 0))
        text_surface2 = my_font.render(f' Armor: {game.hero.get_armor()}', False, (0, 0, 0))
        screen.blit(text_surface, (1000, 850))
        screen.blit(text_surface1, (1000, 900))
        screen.blit(text_surface2, (1300, 900))
        screen_text.blit_message()

        pygame.display.update()
        clock.tick(20)


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
