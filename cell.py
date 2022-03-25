import pyglet

class Cell(pyglet.sprite.Sprite):
    unopenned_image = pyglet.image.load('images/unopenned.png')
    bomb_image = pyglet.image.load('images/bomb.png')
    zero_image = pyglet.image.load('images/zero.png')
    one_image = pyglet.image.load('images/one.png')
    two_image = pyglet.image.load('images/two.png')
    three_image = pyglet.image.load('images/three.png')
    four_image = pyglet.image.load('images/four.png')
    five_image = pyglet.image.load('images/five.png')
    six_image = pyglet.image.load('images/six.png')
    seven_image = pyglet.image.load('images/seven.png')
    eight_image = pyglet.image.load('images/eight.png')
    flag_image = pyglet.image.load('images/flag.png')
    values_dict = {0:zero_image, 1:one_image, 2:two_image, 3:three_image, 4:four_image, 5:five_image, 6:six_image, 7:seven_image, 8:eight_image, 'b':bomb_image}

    def __init__(self, value=0, x=0, y=0, scale=1, batch=None, group=None):
        self.value = value
        self.openned = False 
        self.flagged = False
        super(Cell, self).__init__(Cell.unopenned_image, x=x, y=y, batch=batch, group=group)
        self.scale = scale

    def open(self):
        print(f'cell {self.x, self.y} has been opened')
        self.openned = True
        self.image = Cell.values_dict[self.value]

    def flag(self):
        if not self.openned:
            self.flagged = 1 - self.flagged
            if self.flagged:
                self.image = Cell.flag_image
            else:
                self.image = Cell.unopenned_image