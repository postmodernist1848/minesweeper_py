from typing import Deque
import pyglet
from collections import deque
from pyglet.resource import image
pyglet.resource.path = ['images', 'sounds']

#класс клетки на минном поле
class Cell(pyglet.sprite.Sprite):
    explosion_frames = image('0.png'), image('1.png'), image('2.png'), image('3.png'), image('4.png'), image('5.png')
    expl_ani = pyglet.image.Animation.from_image_sequence(explosion_frames, duration=0.2, loop=False)
    explosion = pyglet.resource.media('explosion.wav', streaming=False)
    unopenned_image = image('unopenned.png')
    bomb_image = image('bomb.png')
    bomb_blownup_image = image('bomb_blownup.png')
    zero_image = image('zero.png')
    one_image = image('one.png')
    two_image = image('two.png')
    three_image = image('three.png')
    four_image = image('four.png')
    five_image = image('five.png')
    six_image = image('six.png')
    seven_image = image('seven.png')
    eight_image = image('eight.png')
    flag_image = image('flag.png')
    question_mark_image = image('question_mark.png')
    values_dict = {0:zero_image, 
                    1:one_image, 
                    2:two_image, 
                    3:three_image, 
                    4:four_image, 
                    5:five_image, 
                    6:six_image, 
                    7:seven_image, 
                    8:eight_image, 
                    'b':bomb_image,
                    'bb':bomb_blownup_image} 
    rmb_states_dict = {'x':unopenned_image, 
                        'f':flag_image, 
                        '?':question_mark_image}

    def __init__(self, value=0, x=0, y=0, scale=1, batch=None, group=None):
        self.value = value
        self.unchecked = not value
        self.openned = False 
        self.rmb_state = 'x'
        self.rmb_states_deque = deque(['x', 'f', '?'])
        super(Cell, self).__init__(Cell.unopenned_image, x=x, y=y, batch=batch, group=group)
        self.scale = scale

    def open(self):
        if self.rmb_state == 'x':
            self.openned = True
            self.image = Cell.values_dict[self.value]

    def on_rmb(self):
        if not self.openned:
            self.rmb_states_deque.rotate(-1)
            self.rmb_state = self.rmb_states_deque[0]
            self.image = self.rmb_states_dict[self.rmb_states_deque[0]]
            
    def explode(self, force:bool=False):
        if self.value == 'b' or force:
            explosion_sprite = pyglet.sprite.Sprite(img=Cell.expl_ani, x=self.x, y=self.y, batch=self.batch)
            explosion_sprite.scale = self.scale
            Cell.explosion.play()


