import pygame
import sys
import os
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
from screeninfo import get_monitors

FPS = 20
TILES_SIZE = 50
WIDTH, HEIGHT = 500, 500
TOP, LEFT = 100, 100
get_monitors()

TILE_IMAGES = {'0': 'data\\floor.png', '1': 'data\\wall.png', '2': 'data\\stair.png', '3': 'data\\chest1.png'}

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
borders = pygame.sprite.Group()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
name = None


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


class BaseCharacter:
    def __init__(self, pos_x, pos_y, hp):
        self.pos_x, self.pos_y, self.hp = pos_x, pos_y, hp
        self.alive = 1

    def set_position(self, x, y):
        self.pos_x = x
        self.pos_y = y

    def is_alive(self):
        if self.hp <= 0:
            self.alive = 0
            return False
        else:
            return True

    def get_damage(self, amount):
        if self.is_alive():
            self.hp -= amount

    def get_cords(self):
        return self.pos_x, self.pos_y


class BaseEnemy(BaseCharacter):
    def __init__(self, pos_x, pos_y, name, hp, damage):
        super().__init__(hp)
        self.name = name
        self.damage = damage

    def hit(self, target):
        target.get_damage(self.damage)

    def get_info(self):
        return [f'Имя врага: {self.name}', f'Здоровье врага: {self.hp}', f'Сила удара: {self.damage}']


class MainHero(BaseCharacter, pygame.sprite.Sprite):
    image = load_image("data\\MH_stay.png")

    def __init__(self, pos_x, pos_y, hp, name):
        BaseCharacter.__init__(self, pos_x, pos_y, hp)
        pygame.sprite.Sprite.__init__(self)

        self.armor = []
        self.orientation = 1
        self.image = self.image_change()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos_x
        self.rect.y = pos_y - 20
        self.rect.height -= 20

        self.name = name
        self.bread = 0
        self.weapon = Weapon('Кулаки', 10)
        self.defence = 0

    def hit(self, target):
        self.weapon.hit(target)
        return

    def add_weapon(self, weapon):
        self.weapon = weapon
        print(f'Подобрал {weapon}')
        return

    def add_bread(self):
        self.bread += 1

    def add_armor(self, armor):
        self.armor.append(armor)
        self.defence += armor.defence

    def heal(self, amount):
        self.hp += amount
        self.hp = self.hp % 200 if self.hp != 200 else 200
        print('Полечился, теперь здоровья', self.hp)

    def check_chest(self, hero, chest):
        if chest.stuff:
            for i in chest.stuff:
                if i == 'Bread':
                    hero.add_bread(i)
                elif type(i) == Weapon:
                    hero.add_weapon(i)
                elif type(i) == Armor:
                    hero.add_armor(i)
            chest.stuff = []

    def set_position(self, x, y, k):
        self.rect.x = x
        self.rect.y = y
        if not pygame.sprite.spritecollideany(self, borders):
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

    def image_change(self):
        if self.orientation == 1:
            im = load_image('data\\MH_go.png')
            return pygame.transform.scale(im, (80, 160))
        elif self.orientation == 3:
            im = load_image('data\\MH_go.png')
            im = pygame.transform.flip(im, flip_x=True, flip_y=False)
            return pygame.transform.scale(im, (80, 160))
        elif self.orientation == 0:
            im = load_image(f'data\\MH_go{0}.png')
            return pygame.transform.scale(im, (60, 160))
        elif self.orientation == 2:
            im = load_image(f'data\\MH_go{2}.png')
            return pygame.transform.scale(im, (60, 160))


class Weapon:
    def __init__(self, name, damage):
        self.name, self.damage = name, damage

    def __str__(self):
        return self.name

    def hit(self, target):
        target.get_damage(self.damage)

    def render(self):
        pass


class Armor:
    def __init__(self, name, defence):
        self.name = name
        self.defence = defence

    def render(self):
        pass


class Chest(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, *stuff):
        super().__init__(all_sprites)
        self.stuff = list(stuff)
        image = load_image(TILE_IMAGES['3'])
        self.image = pygame.transform.scale(image, (TILES_SIZE, TILES_SIZE))
        self.rect = self.image.get_rect().move(
            TILES_SIZE * pos_x + TOP, TILES_SIZE * pos_y + LEFT)


class Stair(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, next_room):
        super().__init__(tiles_group, all_sprites)
        self.next_room = next_room
        image = load_image(TILE_IMAGES['2'])
        self.image = pygame.transform.scale(image, (TILES_SIZE, TILES_SIZE))
        self.rect = self.image.get_rect().move(
            TILES_SIZE * pos_x + TOP, TILES_SIZE * pos_y + LEFT)


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            self.add(borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.image.fill((255, 0, 0))
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.image.fill((255, 0, 0))
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Board:
    # создание поля
    def __init__(self, width, height, filename):
        self.width = width
        self.height = height
        self.board = self.load_level(filename)
        self.object_map = {}

        # значения по умолчанию
        self.left = 0
        self.top = 0
        self.cell_size = 20
        self.colors = {'0': (0, 0, 0), '1': (255, 255, 255), '2': (255, 255, 0), '3': (100, 100, 100)}

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size
    '''

    def get_cell(self, mouse_pos):
        if self.left < mouse_pos[0] < self.cell_size * self.width + self.left and \
                self.top < mouse_pos[1] < self.cell_size * self.height + self.top:
            for y in range(self.height):
                for x in range(self.width):
                    xf = self.left + x * self.cell_size
                    yf = self.top + y * self.cell_size
                    if xf < mouse_pos[0] < self.cell_size + xf and \
                            yf < mouse_pos[1] < self.cell_size + yf:
                        return x, y
        return None
'''
    def load_level(self, filename):
        filename = filename
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        return level_map

    def render(self, level):
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '0':
                    Tile('0', x, y)
                elif level[y][x] == '1':
                    Tile('1', x, y)
                elif level[y][x] == '2':
                    Stair(x, y, 'название след. карты')
                elif level[y][x] == '3':
                    Chest(x, y, [])

    def on_click(self, cell_coords):
        print(cell_coords)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        image = load_image(TILE_IMAGES[tile_type], colorkey=-1)
        self.image = pygame.transform.scale(image, (TILES_SIZE, TILES_SIZE))
        self.rect = self.image.get_rect().move(
            TILES_SIZE * pos_x + TOP, TILES_SIZE * pos_y + LEFT)


class Game:
    def __init__(self, board, hero):
        self.running = None
        self.board = board
        self.hero = hero
        self.k = 1

    def update_hero(self):
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
        self.hero.set_position(next_x, next_y, self.k)

    def action_new_game(self):
        self.running = False
        #  +- Проверка на существование прогресса, предупреждение о том, что та игра будет стерта
        screen.fill((0, 0, 0))
        textbox = TextBox(screen, 100, 100, 800, 80, fontSize=50,
                          borderColour=(255, 0, 0), textColour=(0, 200, 0),
                          radius=10, borderThickness=5)
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.hero.name = textbox.getText()
                    return
            screen.fill((0, 0, 0))

            textbox.listen(events)
            textbox.draw()
            pygame.display.update()

    def action_load_button(self):
        pass

    def action_options(self):
        pass

    def start_screen(self):
        intro_text = ["Gold Pan", "",
                      "Правила игры",
                      "Если в правилах несколько строк,",
                      "приходится выводить их построчно"]

        fon = pygame.transform.scale(load_image('data\\fon.jpg'), screen.get_size())
        new_game_button = Button(screen, 150, 400, 350, 100,
                                 text='Новая игра',  # Text to display
                                 fontSize=50,  # Size of font
                                 margin=0,
                                 inactiveColour=(0, 100, 255),
                                 hoverColour=(255, 100, 30),
                                 pressedColour=(0, 255, 0),  # Colour of button when not being interacted with
                                 radius=50,  # Radius of border corners (leave empty for not curved)
                                 onClick=lambda: self.action_new_game())

        load_button = Button(screen, 150, 550, 350, 100,
                             text='Загрузить игру',  # Text to display
                             fontSize=50,  # Size of font
                             margin=0,
                             inactiveColour=(0, 100, 255),
                             hoverColour=(255, 100, 30),
                             pressedColour=(0, 0, 0),  # Colour of button when not being interacted with
                             radius=50,  # Radius of border corners (leave empty for not curved)
                             onClick=lambda: terminate
                             )

        options_button = Button(screen, 150, 700, 350, 100,
                                text='Опции',  # Text to display
                                fontSize=50,  # Size of font
                                margin=0,
                                inactiveColour=(0, 100, 255),
                                hoverColour=(255, 100, 30),
                                pressedColour=(0, 255, 0),  # Colour of button when not being interacted with
                                radius=50,  # Radius of border corners (leave empty for not curved)
                                onClick=lambda: terminate
                                )

        exit_button = Button(screen, 150, 850, 350, 100,
                             text='Выход из игры',  # Text to display
                             fontSize=50,  # Size of font
                             margin=0,
                             inactiveColour=(0, 100, 255),
                             hoverColour=(255, 100, 30),
                             pressedColour=(0, 255, 0),  # Colour of button when not being interacted with
                             radius=50,  # Radius of border corners (leave empty for not curved)
                             onClick=terminate
                             )

        button_group = [new_game_button, load_button, options_button, exit_button]

        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        self.running = True
        while self.running:
            for event in pygame.event.get():
                for i in button_group:
                    i.draw()
                    i.listen(event)

                pygame_widgets.update(event)
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    return
            pygame.display.flip()
            clock.tick(FPS)


class Fight:
    pass


def terminate():
    pygame.quit()
    sys.exit()


def main():
    screen.fill((0, 0, 0))
    hero = MainHero(300, 300, 50, name)
    board = Board(33, 17, 'map1.txt')

    game = Game(board, hero)
    Game.start_screen(game)
    board.set_view(TOP, LEFT, TILES_SIZE)
    board.render(board.board)
    all_sprites.add(hero)

    Border(board.left, board.top,
           board.left, TILES_SIZE * board.height + board.top)
    Border(board.left, board.top,
           TILES_SIZE * board.width + board.left, board.top - hero.rect.height)
    Border(board.left + TILES_SIZE * board.width, board.top,
           board.left + TILES_SIZE * board.width, TILES_SIZE * board.height + board.top)
    Border(board.left, board.top + TILES_SIZE * board.height,
           board.left + TILES_SIZE * board.width, board.top)

    running = True
    i = 0
    fight = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game.start_screen()
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event.pos)
            if fight:
                pass

        screen.fill((0, 0, 0))
        game.update_hero()

        all_sprites.draw(screen)
        all_sprites.update()

        pygame.display.flip()
        clock.tick(20)


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
