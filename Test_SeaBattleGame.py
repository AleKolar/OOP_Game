'''
Здравствуйте, Две недели разбирал реализуции SeaBattleGame, и если с функциональным и процедурным программированием
становится со временем понятно, хотя и видно, для того чтобы получить такое локоничное и логичное решение - люди, прям вложились
и по времни и по интиллектуальным ресурсам.
Но реализация, именно, конструктора объектов - Фантастическая. Хотя в алгоритме к Проекту и прописан функционал классов.
Я бы сам не додумался! Я реализовал его по памяти, получилось так, что я его просто выучил, но вопросы остались.
Можно в принципе этими заученными, не знаю как назвать - "сниппетами", пользоваться как шаблонами (пока нет понимания)
И этот вариант очень тиражируемый - видимо много людей по нему училось.
Видиммо это действительно самый удачный вариант, т.к. расхождения минимальны и не принципиальны
'''

from random import randint, choice
from time import sleep


class BoardException(Exception):  # родительский класс, далее дочерние, если дочерние == нулевая ссылка, то возвращаем Родителя
    def __str__(self):
        return "Что-то не так с доской!"


class BoardWrongShipException(BoardException):  # пытаетесь выстрелить за доску
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardOutException(BoardException):
    def __str__(self):
        return 'Нельзя выстрелить за пределы доски!'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'В эту клетку вы уже стреляли!'


class Dot:  # При инициализации экземпляру передаются координаты x и y. Сравнении два экземпляра класса
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:
    def __init__(self, bow: Dot, length: int,
                 horizon: bool):  # Я впервые пробою аннотацию типов, оказывается IDE - ДЕЛАЕТ ЭТО НЕ ОСОЗНАННО, ну и понятно
        self.bow = bow
        self.length = length
        self.horizon = horizon
        self.lives = length

    @property  # очень удобно при позиционировании на доске, я сам не догадался
    def dots(self):
        ship_dots = []  # корабли в координатах (свойство класса)
        for i in range(self.length):
            curr_x = self.bow.x  # экземпляр Dot - координаты, и если Horizon == True собираем 'x'
            curr_y = self.bow.y  # Horizon == False, собираем 'y'
            if self.horizon:
                curr_x += i
            else:
                curr_y += i
            ship_dots.append(Dot(curr_x, curr_y))  # собрали коор-ты корабля
        return ship_dots

    def is_hit(self, dot) -> bool:
        return dot in self.dots  # фиксация попадания, коорд. выстрела в коорд. корабля


class Board:
    def __init__(self, size: int, hid=False):
        self.size = size
        self.hid = hid
        self.field = [['O'] * size for _ in range(size)]
        self.busy = []  # заняиость - коорд. вокруг
        self.ships = []  # заняиость  - кораблем
        self.last_hit = []  # коорд. раненого корабля
        self.count_destr_ships = 0  # счетчик уничтоженных кораблей

    def __str__(self):
        res = '  | ' + ' | '.join(map(str, range(1, self.size + 1))) + ' |'
        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' |'
        if self.hid:
            res = res.replace('■', 'O')
        return res

    def out(self, d: Dot) -> bool:  # проверяет: находится ли точка за пределами доски
        return not (0 <= d.x < self.size and 0 <= d.y < self.size)

    def contour(self, ship, visible=False):  # метод отмечает смежные клетки с кораблем(в условии(1 клетка))
        around = [(i, j) for i in range(-1, 2) for j in range(-1, 2)]
        for dot in ship.dots:
            for dx, dy in around:
                curr_dot = Dot(dot.x + dx, dot.y + dy)
                if not self.out(curr_dot) and curr_dot not in self.busy:
                    if visible:  # видимость контура
                        self.field[curr_dot.x][curr_dot.y] = '.'
                    self.busy.append(curr_dot)

    def add_ship(self, ship):  # проверяет что каждая точка корабля не выходт за границы и не занята
        for d in ship.dots:
            if d in self.busy or self.out(d):
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '■'  # если условие выполнено - то корабль, или часть корабля(палуба)
            self.busy.append(d)  # формируем список занятых
        self.ships.append(ship)  # формируем список занятых кораблем
        self.contour(ship)  # формируем контур из точек(занятость)

    def shot(self, d: Dot) -> bool:  # Тут вся статистика выстрелов и маркировка
        if d in self.busy:
            raise BoardUsedException()
        if self.out(d):
            raise BoardOutException()

        self.busy.append(d)

        for ship in self.ships:  # визуализация поподаний, промахов
            if ship.is_hit(d):
                self.field[d.x][d.y] = 'X'
                print('Попадание!')
                ship.lives -= 1
                if ship.lives == 0:
                    self.count_destr_ships += 1
                    self.contour(ship, visible=True)
                    print('Корабль уничтожен!')
                    self.last_hit = []
                    return False
                else:
                    print('Корабль ранен!')
                    self.last_hit.append(d)
                    return True

        self.field[d.x][d.y] = 'T'
        print('Мимо!')
        return False

    def begin(self):  # в начале игры - обнуляем занятость
        self.busy = []

    def defeat(self):  # фиксация подбития корабля
        return self.count_destr_ships == len(self.ships)


class Player:
    def __init__(self, board: Board, enemy: Board):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    '''
    С этим я до конца не разобрался: В определяемых пользователем базовых классах абстрактные методы должны вызывать это исключение
    т.е. его вызываем у AI и User, т.е. если у Player нет игровых полей Игрока и AI ... , или обязательно должен быть реализован Player ?
     - почему именно, такая реализация, Я прочитал документацию и как по Канту: предел познания человеческого разума
    '''

    def move(self) -> bool:  # Пока попадаем - стреляем
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                sleep(1)  # Это для наглядности
                return repeat
            except BoardException as excep:
                print(excep)


class AI(Player):
    def ask(self) -> Dot:
        last = self.enemy.last_hit
        while True:
            if last:  # добивание раненого корабля
                if len(last) == 1:
                    near = ((0, 1), (0, -1), (1, 0), (-1, 0))  #
                else:
                    if last[0].x == last[-1].x:
                        near = ((0, 1), (0, -1))
                    else:
                        near = ((1, 0), (-1, 0))
                dx, dy = choice(near)
                d = choice((Dot(last[-1].x + dx, last[-1].y + dy), Dot(last[0].x + dx, last[0].y + dy)))
            else:
                d = Dot(randint(0, 5), randint(0, 5))
            if d not in self.enemy.busy and not self.enemy.out(d):
                break
        sleep(0.1 * randint(15, 50))  # Это для наглядности, имитация "мыслительной работы"
        print(f'Ход компьютера: {d.x + 1} {d.y + 1}')
        return d


class User(Player):
    def ask(self) -> Dot:
        while True:
            coords = input('Введите координаты выстрела:\t').split()
            if len(coords) != 2:
                print('Введите 2 координаты')
                continue
            x, y = coords
            if not all((x.isdigit(), y.isdigit())):
                print('Координаты должны быть числами')
                continue
            return Dot(int(x) - 1, int(y) - 1)


class Game:
    def __init__(self, size=6):
        self.lens = (3, 2, 2, 1, 1, 1, 1)
        self.size = size
        ai_board = self.random_board()
        user_board = self.random_board()
        ai_board.hid = True

        self.ai = AI(ai_board, user_board)
        self.pl = User(user_board, ai_board)

    def try_gen_board(
            self):  # Раставляем корабли, генерируем координаты расположения в цикле while, если попыток > 2000 - НЕ ПЛУЧИЛОСЬ - exc
        attempts = 0
        board = Board(size=self.size)
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), (randint(0, self.size))), l, bool(randint(0, 1)))  # !!! Вот так надо было мне делать с самого начала генерируем переменную ship, расставляем, и все это в классе Game
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException as exc:
                    print(exc)

        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_gen_board()
        return board

    @staticmethod
    def greet():
        print('-------------------')
        print('  Приветсвуем вас  ')
        print('      в игре       ')
        print('    морской бой    ')
        print('-------------------')
        print(' формат ввода: x y ')
        print(' x - номер строки  ')
        print(' y - номер столбца ')
        print('-------------------')

    def print_boards(self):  # вывод двух досок рядом по горизонтали
        print('-' * self.size * 10)
        print('Ваша доска:'.ljust((self.size + 1) * 4 - 1) + ' ' * self.size + 'Доска компьютера:')
        for s1, s2 in zip(self.pl.board.__str__().split('\n'), self.ai.board.__str__().split('\n')):
            print(s1 + ' ' * self.size + s2)

    def loop(self):  # Реализация - Вот, то же для меня стало 'камнем преткновения'
        step = 0
        while True:
            self.print_boards()
            if step % 2 == 0:
                print('Ваш ход!')
                repeat = self.pl.move()  # Этот момент - что через вот так - можно!
            else:
                print('Ходит компьютер!')
                repeat = self.ai.move()
            if repeat:
                step -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print('Вы выиграли!')
                break
            if self.pl.board.defeat():
                self.print_boards()
                print('Компьютер выиграл!')
                break
            step += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
