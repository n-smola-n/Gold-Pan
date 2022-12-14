import pygame


TILES_SIZE = 50


class BaseCharacter:
    def __init__(self, pos_x, pos_y, hp):
        self.pos_x, self.pos_y, self.hp = pos_x, pos_y, hp
        self.alive = 1

    def move(self, delta_x, delta_y):
        self.pos_x += delta_x
        self.pos_y += delta_y

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

    def render(self, screen):
        center = self.pos_x * TILES_SIZE + TILES_SIZE // 2, self.pos_y * TILES_SIZE + TILES_SIZE // 2
        pygame.draw.circle(screen, (255, 0, 0), center, TILES_SIZE // 2)


class BaseEnemy(BaseCharacter):
    def __init__(self, pos_x, pos_y, weapon, hp):
        super().__init__(pos_x, pos_y, hp)
        self.weapon = weapon

    def hit(self, target):
        self.weapon.hit(self, target)

    def __str__(self):
        print(f'Враг на позиции ({self.pos_x}, {self.pos_y}) с оружием {self.weapon.name()}')


class MainHero(BaseCharacter):
    def __init__(self, pos_x, pos_y, hp, name):
        super().__init__(pos_x, pos_y, hp)
        self.name = name
        self.weapon = None
        self.Wlist = []

    def hit(self, target):
        if not self.weapon:
            print('Я безоружен')
            return
        else:
            self.weapon.hit(target)
            return

    def add_weapon(self, weapon):
        if type(weapon) == Weapon:
            if not self.Wlist:
                self.weapon = weapon
            self.Wlist.append(weapon)
            print(f'Подобрал {weapon}')
            return
        print('Это не оружие')

    def heal(self, amount):
        self.hp += amount
        self.hp = self.hp % 200 if self.hp != 200 else 200
        print('Полечился, теперь здоровья', self.hp)


class Weapon:
    def __init__(self, name, damage):
        self.name, self.damage = name, damage

    def __str__(self):
        return self.name

    def hit(self, target):
        target.get_damage(self.damage)


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
        self.colors = {'0': (0, 0, 0), '1': (255, 255, 255), '2': (0, 255, 0)}

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
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


def main():
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen.fill((255, 255, 255))
    board = Board(33, 18, 'map1.txt')
    hero = MainHero(10, 10, 50, 'chara')
    board.set_view(100, 100, TILES_SIZE)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event.pos)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    hero.move(0, -1)
                elif event.key == pygame.K_DOWN:
                    hero.move(0, 1)
                elif event.key == pygame.K_LEFT:
                    hero.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    hero.move(1, 0)
        board.render(screen)
        hero.render(screen)
        print(str(hero))
        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
