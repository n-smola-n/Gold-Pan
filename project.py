import pygame
import sys
import os

TILES_SIZE = 50


def load_image(name, colorkey=None):
    fullname = name
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
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
    def __init__(self, pos_x, pos_y, weapon, hp):
        super().__init__(pos_x, pos_y, hp)
        self.weapon = weapon

    def hit(self, target):
        self.weapon.hit(self, target)

    def __str__(self):
        print(f'Враг на позиции ({self.pos_x}, {self.pos_y}) с оружием {self.weapon.name()}')


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
        self.rect.y = pos_y

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
            return pygame.transform.scale(im, (100, 180))
        elif self.orientation == 3:
            im = load_image('data\\MH_go.png')
            im = pygame.transform.flip(im, flip_x=True, flip_y=False)
            return pygame.transform.scale(im, (100, 180))
        elif self.orientation == 0:
            im = load_image(f'data\\MH_go{0}.png')
            return pygame.transform.scale(im, (70, 180))
        elif self.orientation == 2:
            im = load_image(f'data\\MH_go{2}.png')
            return pygame.transform.scale(im, (70, 180))



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


class Chest:
    def __init__(self, *stuff):
        self.stuff = list(stuff)

    def render(self):
        pass


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
        self.object_map = [[None] * width for _ in range(height)]
        self.board = []
        with open(filename) as f:
            for i in f:
                self.board.append(list(i.split()[0]))

        # значения по умолчанию
        self.left = 0
        self.top = 0
        self.cell_size = 20
        self.colors = {'0': (0, 0, 0), '1': (255, 255, 255), '2': (0, 255, 0), '3': (200, 200, 0)}

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        screen.fill((255, 255, 255))
        self.draw_rect(screen)
        for x in range(self.width):
            for y in range(self.height):
                pygame.draw.rect(screen, (30, 30, 30),
                                 (self.left + x * self.cell_size, self.top + y * self.cell_size,
                                  self.cell_size, self.cell_size), 1)

    def draw_rect(self, screen):
        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                pygame.draw.rect(screen, self.colors[self.board[y][x]],
                                 (self.left + x * self.cell_size, self.top + y * self.cell_size,
                                  self.cell_size, self.cell_size))

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

    def on_click(self, cell_coords):
        print(cell_coords)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        self.on_click(cell)


class Game:
    def __init__(self, board, hero):
        self.board = board
        self.hero = hero
        self.k = 1

    def update_hero(self):
        next_x, next_y = self.hero.get_cords()
        '''
        if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
            next_x -= 10
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
            next_x += 10
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            next_y -= 10
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            next_y += 10
            '''
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


all_sprites = pygame.sprite.Group()
borders = pygame.sprite.Group()


def main():
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    board = Board(33, 18, 'map1.txt')
    board.set_view(100, 100, TILES_SIZE)
    hero = MainHero(300, 300, 50, 'chara')
    all_sprites.add(hero)
    game = Game(board, hero)
    Border(board.left, board.top,
           board.left, TILES_SIZE * board.height + board.top)
    Border(board.left, board.top,
           TILES_SIZE * board.width + board.left, board.top)
    Border(board.left + TILES_SIZE * board.width, board.top,
           board.left + TILES_SIZE * board.width, TILES_SIZE * board.height + board.top)
    Border(board.left, board.top + TILES_SIZE * board.height,
           board.left + TILES_SIZE * board.width, board.top)

    running = True
    clock = pygame.time.Clock()
    i = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event.pos)
        game.update_hero()

        board.render(screen)

        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.flip()
        clock.tick(20)


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
