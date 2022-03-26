from operator import ne
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

#-------------- Строковые константы ---------------------------------------
GAME = '☺'
WIN = 'Вы выиграли!'
LOSS = 'Вы проиграли!'


#---------------- Игра ---------------------------------------------------

def get_neighbours(arr:list, i, j, radius=1):            #функция для нахождения соседей (элементов) всех клеток в двухмерном списке(матрице)
        for y in range(i-radius, i + 1 + radius):
            for x in range(j-radius, j + 1 + radius):
                if y >= 0 and y < len(arr) and x >= 0 and x < len(arr[0]):
                     yield arr[y][x]

def get_neighbours_index(arr:list, i, j, radius=1):            #функция для нахождения индексов соседей всех клеток в двухмерном списке(матрице)
        for y in range(i-radius, i + 1 + radius):
            for x in range(j-radius, j + 1 + radius):
                if y >= 0 and y < len(arr) and x >= 0 and x < len(arr[0]):
                     yield (y, x)

#----------------------------------------------------------------------------

batch = pyglet.graphics.Batch()
game_window = Window(700, 700, "Сапёр", resizable=True)
game_window.set_minimum_size(320, 200)
pyglet.gl.glClearColor(173/255, 216/255, 230/255, 1)

#таймер для игры
class Timer(pyglet.text.Label):           
    def __init__(self, *args, **kwargs):
        super(Timer, self).__init__('00:00', *args, **kwargs)
        
        
    def start_timer(self):
        self.reset_timer()
        self.start_time = time.time()
        pyglet.clock.schedule_interval(self.update, 0.5)

    def reset_timer(self):
        self.stop_timer()
        self.text = '00:00'

    def stop_timer(self):
        pyglet.clock.unschedule(self.update)

    def update(self, dt):
        cur_time =  time.time() - self.start_time
        self.text = '{mins:0>2}:{secs:0>2}'.format(mins = int(cur_time / 60), secs = int(cur_time % 60))
        
#класс игры в сапер
class Main_game:

    win = pyglet.media.load('win.wav')
    def __init__(self):
        self.game_height = 20
        self.game_width = 20
        self.mines_number = int(self.game_width * self.game_height * 0.15) #целевое кол-во мин
        self.cell_size = min(game_window.width, game_window.height) // 28
        self.game_offset_x = (game_window.width - self.game_width * self.cell_size) // 2
        self.game_state = GAME
        self.game_started = False
        self.game_timer = Timer(x=self.game_offset_x, y=57/70 * game_window.height, font_size=32, dpi = 150, color=(0,0,0,255), batch=batch)
        self.game_state_label = pyglet.text.Label(text=GAME, font_name = 'Consolas', color=(0,0,0,255), bold=True, font_size=32, dpi=150, anchor_x='center', align='center', x=game_window.width // 2, y=game_window.height * 13/14, batch=batch) 
        self.flag_number_label = pyglet.text.Label(text=f'*:{self.mines_number}', font_name = 'Consolas', color=(0,0,0,255), bold=True, font_size=32, dpi=150, anchor_x='right', align='right', x=self.game_offset_x + self.game_width * self.cell_size, y= 57/70 * game_window.height, batch=batch)
        self.minesweeper_matrix_clear()
        self.create_minefield()
        pyglet.clock.schedule_interval(self.update, 1/60)
        game_window.push_handlers(self)
    
    def minesweeper_matrix_clear(self):
        self.minesweeper_matrix = [[0] * self.game_width for _ in range(self.game_height)]
    #создание двумерного списка(матрицы), в соответствии с которой создается 'минное поле'
    def create_minesweeper_matrix(self, x:int=None, y:int=None):
        mines_count = 0
        generator_matrix = [[0] * (self.game_width) for _ in range(self.game_height)] #матрица с нулями и единицами
        self.minesweeper_matrix = [[0] * self.game_width for _ in range(self.game_height)] #матрица с числами и 'b'

        while mines_count < self.mines_number:                       #генерация нужного количества мин, исключая точку клика
            row = random.choice(generator_matrix)
            row[random.randrange(len(row))] = 1 
            for i, j in get_neighbours_index(generator_matrix, y, x):
                generator_matrix[i][j] = 0       

            mines_count = sum(sum(row) for row in generator_matrix)
        generator_matrix.reverse()

        for i in range(self.game_height ):                                #генерация матрицы со значениями клеток
            for j in range(self.game_width):
                if generator_matrix[i][j] == 1:
                    self.minesweeper_matrix[i][j] = 'b'
                else:
                    neighbouring_cells_sum = sum(get_neighbours(generator_matrix, i, j))
                    self.minesweeper_matrix[i][j] = neighbouring_cells_sum

    #создание 'минного поля' из спрайтов 
    def create_minefield(self):
        self.cells = []
        for y in range(0, self.game_width * self.cell_size, self.cell_size):
            row = []
            for x in range(0, self.game_width * self.cell_size, self.cell_size):
                value = self.minesweeper_matrix[self.game_height - y//self.cell_size - 1][x//self.cell_size]
                row.append(Cell(value=value, x=x + self.game_offset_x, y=y, scale = self.cell_size / 30, batch=batch)) 
            self.cells.append(row)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_state == GAME:
            if button == pyglet.window.mouse.LEFT:
                try:
                    self.cells[y // self.cell_size][(x - self.game_offset_x) // self.cell_size].open()  #лкм - открытие клетки 
                    if not self.game_started:
                        self.game_start((x - self.game_offset_x) // self.cell_size, y // self.cell_size)               
                except IndexError: 
                    pass
            elif button == pyglet.window.mouse.RIGHT and self.game_started:
                try:
                    self.cells[y // self.cell_size][(x - self.game_offset_x) // self.cell_size].on_rmb() #правая кнопка - переключение между закрытой клеткой, флагом и знаком вопроса
                except IndexError:
                    pass
        elif self.game_state == LOSS:
            pyglet.clock.unschedule(self.blow_up_field)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.C:  #читы - победа по нажатию кнопки
            for row in self.cells:
                for cell in row:
                    if cell.value != 'b':
                        cell.open()
        elif symbol == key.R: #ресет игры
            self.game_reset()
        elif symbol == key.F11:
            game_window.set_fullscreen(1 - game_window.fullscreen)
    def on_resize(self, width, height):
        self.cell_size = min(game_window.width, game_window.height) // 28
        scale = self.cell_size / 30
        self.game_offset_x = (game_window.width - self.game_width * self.cell_size) // 2
        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                cell.scale = scale
                cell.x = j * self.cell_size + self.game_offset_x
                cell.y = i * self.cell_size
        self.game_timer.x, self.game_timer.y, self.game_timer.font_size = self.game_offset_x, 57/70 * game_window.height, 32 * scale
        self.game_state_label.x, self.game_state_label.y, self.game_state_label.font_size = game_window.width // 2, game_window.height * 13/14, 32 * scale
        self.flag_number_label.x, self.flag_number_label.y, self.flag_number_label.font_size = self.game_offset_x + self.game_width * self.cell_size, 57/70 * game_window.height, 32 * scale


    def update(self, dt): #метод обновления состояния игры
        openned_counter = 0
        flagged = 0
        if self.game_state == GAME:
            for i, row in enumerate(self.cells):
                for j, cell in enumerate(row):
                    if cell.openned:
                        openned_counter += 1
                        if cell.value == 'b':
                            self.game_state = LOSS
                            cell.value = 'bb'
                            cell.explode(True)
                            return
                        elif cell.unchecked:
                            for y, x in get_neighbours_index(self.cells, i, j):
                                self.cells[y][x].open()
                            cell.unchecked = False
                    elif cell.rmb_state == 'f':
                        flagged += 1
            self.flag_number_label.text = f'*:{max(0, self.mines_number - flagged)}'

            if openned_counter + self.mines_number == self.game_height * self.game_width:
                self.game_state = WIN
                Main_game.win.play()                
        else:                                                                      #конец игры
            self.show_field()
            if self.game_state == LOSS:
                self.blown_up_counter = self.game_height * self.game_width - 1
                pyglet.clock.schedule_interval(self.blow_up_field, 0.03)
            self.game_state_label.text = self.game_state
            pyglet.clock.unschedule(self.update)
            self.game_timer.stop_timer()

    def game_start(self, x, y:tuple):
        self.game_started = True
        self.game_timer.start_timer()
        self.create_minesweeper_matrix(x, y)
        self.create_minefield()
        self.cells[y][x].open()

    def game_reset(self): #ресет игры
        self.game_state = GAME
        self.game_started = False
        self.game_state_label.text = self.game_state
        self.game_timer.reset_timer()
        pyglet.clock.unschedule(self.blow_up_field)
        self.minesweeper_matrix_clear()
        self.create_minefield()
        pyglet.clock.schedule_interval(self.update, 1/60)

    def show_field(self):
        for row in self.cells:
            for cell in row:
                cell.rmb_state = 'x'
                cell.open()
            
    def blow_up_field(self, dt):
        self.cells[self.blown_up_counter // self.game_width][self.game_width - 1 - self.blown_up_counter % self.game_width].explode()
        self.blown_up_counter -= 1
        if self.blown_up_counter <= 0:
            pyglet.clock.unschedule(self.blow_up_field)
                


main_game = Main_game()

@game_window.event
def on_draw():
    game_window.clear()
    batch.draw()



pyglet.app.run()