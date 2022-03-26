from typing import Deque
import pyglet
from pyglet.image import load
from collections import deque

class Cell(pyglet.sprite.Sprite):
    explosion_frames = load('images/expl1.png'), load('images/expl2.png'), load('images/expl3.png'), load('images/expl4.png'), load('images/expl5.png'), load('images/expl6.png'), load('images/expl7.png'), load('images/expl8.png')
    expl_ani = pyglet.image.Animation.from_image_sequence(explosion_frames, duration=0.2, loop=False)
    explosion = pyglet.media.load('explosion.wav', streaming=False)
    unopenned_image = load('images/unopenned.png')
    bomb_image = load('images/bomb.png')
    bomb_blownup_image = load('images/bomb_blownup.png')
    zero_image = load('images/zero.png')
    one_image = load('images/one.png')
    two_image = load('images/two.png')
    three_image = load('images/three.png')
    four_image = load('images/four.png')
    five_image = load('images/five.png')
    six_image = load('images/six.png')
    seven_image = load('images/seven.png')
    eight_image = load('images/eight.png')
    flag_image = load('images/flag.png')
    question_mark_image = load('images/question_mark.png')
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


