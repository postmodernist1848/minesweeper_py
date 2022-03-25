import pyglet

class Cell(pyglet.sprite.Sprite):
    unopenned = pyglet.image.load('images/unopenned.png')
    bomb = pyglet.image.load('images/bomb.png')
    zero = pyglet.image.load('images/zero.png')
    one = pyglet.image.load('images/one.png')
    two = pyglet.image.load('images/two.png')
    three = pyglet.image.load('images/three.png')
    four = pyglet.image.load('images/four.png')
    five = pyglet.image.load('images/five.png')
    six = pyglet.image.load('images/six.png')
    seven = pyglet.image.load('images/seven.png')
    eight = pyglet.image.load('images/eight.png')
    values_dict = {0:zero, 1:one, 2:two, 3:three, 4:four, 5:five, 6:six, 7:seven, 8:eight, 'b':bomb}



    def __init__(self, value=0, x=0, y=0, scale=1, batch=None, group=None):
        self.openned = False 
        self.value = value

        super(Cell, self).__init__(Cell.unopenned, x=x, y=y, batch=batch, group=group)
        self.scale = scale

    def open(self):
        print(f'cell {self.x, self.y} has been opened')
        self.openned = True
        self.image = Cell.values_dict[self.value]

    def flag(self):
        print(f'cell {self.x, self.y} has been flagged')