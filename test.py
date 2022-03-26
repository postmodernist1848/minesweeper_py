import pyglet

window = pyglet.window.Window()
batch = pyglet.graphics.Batch()
sprite_sheet = pyglet.resource.image('images/bomb.png')
image_grid = pyglet.image.ImageGrid(sprite_sheet, rows=1, columns=2)

ani = pyglet.image.Animation.from_image_sequence(image_grid, duration=0.5)

pyglet.sprite.Sprite(ani, batch=batch)
@window.event
def on_draw():
    window.clear()
    batch.draw()
pyglet.app.run()