import pyglet
from pyglet.window import key, Window
import random
import time
from cell import Cell

#TODO: открывание всех пустых клеток, соседних с открытой
#штука на среднюю кнопку мыши
#менюшки
#в конце показывать все бомбы
#запись рекордом по времени в сейв файл
#взрывы при проигранной игре

#-------------- Константы ------------------------------------------------
GAME = 'Игра'
WIN = 'Вы выиграли!'
LOSS = 'Вы проиграли!'


#---------------- Игра ---------------------------------------------------
batch = pyglet.graphics.Batch()
game_window = Window(450, 600, "Сапёр")

#таймер для игры
class Timer(pyglet.text.Label):           
    def __init__(self, *args, **kwargs):
        super(Timer, self).__init__('00:00', *args, **kwargs)
        
        
    def start_timer(self):
        self.text = '00:00'
        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 0.5)

    def stop_timer(self):
        pyglet.clock.unschedule(self.update)

    def update(self, dt):
        cur_time =  time.time() - self.start_time
        self.text = '{mins:0>2}:{secs:0>2}'.format(mins = int(cur_time / 60), secs = int(cur_time % 60))
        
#класс игры в сапер
class Main_game:
    def __init__(self):
        self.game_height = 10
        self.game_width = 10
        self.cell_size = 45
        self.game_state = GAME
        self.game_started = False
        self.game_timer = Timer(x=game_window.width // 2 - 200, y=game_window.height - 130, font_size=32, batch=batch)
        self.game_state_label = pyglet.text.Label(text=GAME, font_name = 'Consolas', bold=True, anchor_x='center', align='center', x=game_window.width // 2, y=game_window.height - 50, batch=batch)
        self.create_minesweeper_matrix()
        for row in self.minesweeper_matrix:
            print(*row)
        self.create_minefield()
        pyglet.clock.schedule_interval(self.update, 1/60)

        game_window.push_handlers(self)
        
    #создание двумерного списка(матрицы), в соответствии с которой создается 'минное поле'
    def create_minesweeper_matrix(self):
        self.mines_count = 0
        minesweeper_matrix = [[0] * (self.game_width + 2) for _ in range(self.game_height + 2)]
        self.minesweeper_matrix = [[0] * self.game_width for _ in range(self.game_height)]
        for i in range(1, self.game_height + 1):
            for j in range(1, self.game_width + 1):
                if random.random() < 0.15:
                    minesweeper_matrix[i][j] = 1
        for i in range(1, self.game_height + 1):
            for j in range(1, self.game_width + 1):
                if minesweeper_matrix[i][j] == 1:
                    self.minesweeper_matrix[i - 1][j - 1] = 'b'
                    self.mines_count += 1
                else:
                    neighbouring_cells = minesweeper_matrix[i - 1][j - 1] + minesweeper_matrix[i - 1][j] + minesweeper_matrix[i - 1][j + 1] + minesweeper_matrix[i][j - 1] + \
                minesweeper_matrix[i][j + 1] + minesweeper_matrix[i + 1][j - 1] + minesweeper_matrix[i + 1][j] + minesweeper_matrix[i + 1][j + 1]
                    self.minesweeper_matrix[i - 1][j - 1] = neighbouring_cells

    #создание 'минного поля' из спрайтов 
    def create_minefield(self):
        self.cells = []
        for y in range(0, self.game_width * self.cell_size, self.cell_size):
            row = []
            for x in range(0, self.game_width * self.cell_size, self.cell_size):
                value = self.minesweeper_matrix[self.game_height - y//self.cell_size - 1][x//self.cell_size]
                row.append(Cell(value=value, x=x, y=y, scale = self.cell_size / 30, batch=batch)) 
            self.cells.append(row)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_state == GAME:
            if button == pyglet.window.mouse.LEFT:
                try:
                    self.cells[y // self.cell_size][x // self.cell_size].open()  #лкм - открытие клетки
                    if not self.game_started:
                        self.game_start()                
                except IndexError: 
                    pass
            elif button == pyglet.window.mouse.RIGHT:
                try:
                    self.cells[y // self.cell_size][x // self.cell_size].on_rmb() #правая кнопка - переключение между закрытой клеткой, флагом и знаком вопроса
                    if not self.game_started:
                        self.game_start()
                except IndexError:
                    pass
    def on_key_press(self, symbol, modifiers):
        if symbol == key.C:  #читы - победа по нажатию кнопки
            for row in self.cells:
                for cell in row:
                    if cell.value != 'b':
                        cell.open()
        elif symbol == key.R: #ресет игры
            self.game_reset()

    def update(self, dt): #метод обновления состояния игры
        openned_counter = 0
        if self.game_state == GAME:
            for row in self.cells:
                for cell in row:
                    if cell.openned:
                        openned_counter += 1
                        if cell.value == 'b':
                            self.game_state = LOSS
                            return
            if openned_counter + self.mines_count == self.game_height * self.game_width:
                self.game_state = WIN
                
        else:                                                                      #конец игры
            self.game_state_label.text = self.game_state
            pyglet.clock.unschedule(self.update)
            self.game_timer.stop_timer()

    def game_start(self):
        self.game_started = True
        self.game_timer.start_timer()

    def game_reset(self): #название говорит само за себя
        self.game_state = GAME
        self.game_started = False
        self.game_state_label.text = self.game_state
        self.create_minesweeper_matrix()
        print('-' * 20)
        for row in self.minesweeper_matrix:
            print(*row)
        self.create_minefield()
        self.game_timer.start_timer()
        pyglet.clock.schedule_interval(self.update, 1/60)

main_game = Main_game()

@game_window.event
def on_draw():
    game_window.clear()
    batch.draw()



pyglet.app.run()