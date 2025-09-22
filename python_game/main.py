import pyglet
from pyglet import shapes
import math
import random
import os
import threading
try:
    import requests
except Exception:
    requests = None

WIDTH, HEIGHT = 900, 600
LANES_X = [WIDTH*0.25, WIDTH*0.5, WIDTH*0.75]
G = 900
JUMP_VY = -550
SPEED = 280

def ensure_assets():
    if requests is None:
        return
    base = os.path.join(os.path.dirname(__file__), 'assets', 'sfx')
    os.makedirs(base, exist_ok=True)
    hit_path = os.path.join(base, 'hit.wav')
    if not os.path.exists(hit_path):
        urls = [
            'https://raw.githubusercontent.com/oppenfuture/cc0-sfx/main/hit/hit1.wav',
            'https://raw.githubusercontent.com/keroserene/sfxr/master/examples/impact.wav',
        ]
        for u in urls:
            try:
                r = requests.get(u, timeout=10)
                if r.ok and len(r.content) > 1000:
                    with open(hit_path, 'wb') as f:
                        f.write(r.content)
                    break
            except Exception:
                pass

class Game:
    def __init__(self):
        self.win = pyglet.window.Window(WIDTH, HEIGHT, caption='Neon Runner (Python)')
        self.state = 'menu'
        self.score = 0
        self.batch = pyglet.graphics.Batch()
        self.fps_display = pyglet.window.FPSDisplay(self.win)

        self.player_x = LANES_X[1]
        self.player_y = HEIGHT*0.75
        self.vy = 0
        self.lane = 1
        self.obstacles = []
        self.hit_snd = None
        try:
            sfx = os.path.join(os.path.dirname(__file__), 'assets', 'sfx', 'hit.wav')
            if os.path.exists(sfx):
                self.hit_snd = pyglet.media.StaticSource(pyglet.media.load(sfx, streaming=False))
        except Exception:
            pass

        self.label_title = pyglet.text.Label('NEON RUNNER', font_name='Segoe UI', font_size=48,
                                             x=WIDTH//2, y=HEIGHT//3+60, anchor_x='center', color=(0,230,255,255))
        self.label_tip = pyglet.text.Label('Press ENTER to Start | ←/→ move | SPACE jump | ESC pause', font_name='Segoe UI', font_size=16,
                                           x=WIDTH//2, y=HEIGHT//3, anchor_x='center', color=(200,230,255,255))
        self.label_score = pyglet.text.Label('Score: 0', font_name='Segoe UI', font_size=18,
                                             x=20, y=HEIGHT-30, anchor_x='left', color=(0,230,255,255))

        @self.win.event
        def on_draw():
            self.win.clear()
            self.draw_bg()
            if self.state == 'menu':
                self.label_title.draw(); self.label_tip.draw()
            else:
                self.draw_obstacles(); self.draw_player(); self.label_score.draw()
                if self.state == 'paused':
                    self.draw_center_text('PAUSED', (255,255,120,255))
                elif self.state == 'gameover':
                    self.draw_center_text(f'GAME OVER\nScore: {self.score}\nR: Retry  ESC: Menu', (255,80,120,255))
            # self.fps_display.draw()  # enable if needed

        @self.win.event
        def on_key_press(symbol, modifiers):
            from pyglet.window import key
            if self.state == 'menu':
                if symbol == key.ENTER:
                    self.start()
            elif self.state == 'playing':
                if symbol in (key.LEFT, key.A):
                    self.lane = max(0, self.lane-1)
                if symbol in (key.RIGHT, key.D):
                    self.lane = min(2, self.lane+1)
                if symbol in (key.SPACE, key.UP):
                    self.jump()
                if symbol == key.ESCAPE:
                    self.state = 'paused'
            elif self.state == 'paused':
                if symbol == key.ESCAPE:
                    self.state = 'playing'
            elif self.state == 'gameover':
                if symbol == key.R:
                    self.reset(); self.state = 'playing'
                if symbol == key.ESCAPE:
                    self.reset(); self.state = 'menu'

        @self.win.event
        def on_mouse_press(x, y, button, modifiers):
            if self.state == 'menu':
                self.start()
            elif self.state == 'playing':
                if y > HEIGHT*0.65:
                    # bottom area -> lane switch
                    if x < WIDTH*0.5:
                        self.lane = max(0, self.lane-1)
                    else:
                        self.lane = min(2, self.lane+1)
                else:
                    self.jump()

        pyglet.clock.schedule_interval(self.update, 1/60)
        threading.Thread(target=ensure_assets, daemon=True).start()
        self.reset()

    def reset(self):
        self.score = 0
        self.lane = 1
        self.player_x = LANES_X[self.lane]
        self.player_y = HEIGHT*0.75
        self.vy = 0
        self.obstacles = []
        z = 0
        for i in range(50):
            lane = random.randint(0,2)
            self.obstacles.append({'x': LANES_X[lane], 'z': z})
            z -= random.randint(140, 220)

    def start(self):
        self.state = 'playing'

    def jump(self):
        if self.state == 'playing' and self.player_y >= HEIGHT*0.75:
            self.vy = JUMP_VY

    def update(self, dt):
        if self.state != 'playing':
            return
        target_x = LANES_X[self.lane]
        self.player_x += (target_x - self.player_x) * min(1, dt*10)
        self.vy += G*dt
        self.player_y = min(HEIGHT*0.75, self.player_y + self.vy*dt)
        if self.player_y >= HEIGHT*0.75:
            self.player_y = HEIGHT*0.75
            self.vy = 0

        for ob in self.obstacles:
            ob['z'] += SPEED*dt
            if ob['z'] > 60:
                ob['z'] -= 2000
                ob['x'] = LANES_X[random.randint(0,2)]

        for ob in self.obstacles:
            ob_y = HEIGHT*0.75 - ob['z']*0.12
            if abs(ob['x'] - self.player_x) < 40 and abs(ob_y - self.player_y) < 30 and ob['z'] > -20:
                self.state = 'gameover'
                if self.hit_snd:
                    try: self.hit_snd.play()
                    except Exception: pass
                break

        self.score += 1
        self.label_score.text = f'Score: {self.score}'

    def draw_bg(self):
        pyglet.gl.glClearColor(2/255, 8/255, 20/255, 1)
        # neon lanes
        for x in LANES_X:
            line = shapes.Line(x, 0, x, HEIGHT, 2, (0,255,255))
            line.opacity = 255
            line.draw()
        # scanlines
        for i in range(0, HEIGHT, 30):
            hline = shapes.Line(0, i, WIDTH, i, 1, (0,255,255))
            hline.opacity = 255
            hline.draw()

    def draw_player(self):
        rect = shapes.Rectangle(self.player_x-20, self.player_y-20, 40, 40, color=(0,255,255))
        rect.draw()

    def draw_obstacles(self):
        for ob in self.obstacles:
            ob_y = HEIGHT*0.75 - ob['z']*0.12
            size = max(8, 24 - int(ob['z']*0.05))
            rect = shapes.Rectangle(ob['x']-size//2, ob_y-size//2, size, size, color=(255,60,110))
            rect.draw()

    def draw_round_rect(self, x, y, w, h, col):
        # Deprecated helper (kept for reference); not used now.
        rect = shapes.Rectangle(x, y, w, h, color=col)
        rect.draw()

    def draw_center_text(self, txt, col):
        label = pyglet.text.Label(txt, font_name='Segoe UI', font_size=36,
                                  x=WIDTH//2, y=HEIGHT//2, anchor_x='center', anchor_y='center', color=col)
        label.draw()

    def run(self):
        pyglet.app.run()


if __name__ == '__main__':
    threading.Thread(target=ensure_assets, daemon=True).start()
    Game().run()
