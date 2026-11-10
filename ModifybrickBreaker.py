import random
import math
import tkinter as tk

# Kelas dasar untuk objek yang digambar dan digerakkan di canvas.
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)

# Bola memantul dari dinding dan objek lain di dalam permainan.
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 11
        self.piercing_remaining = 0
        self.overlapping_bricks = set()
        item = canvas.create_oval(x-self.radius, y-self.radius, x+self.radius, y+self.radius, fill='white')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        # Balikkan arah bola saat menyentuh sisi atau bagian atas canvas.
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        # Hindari menghitung benturan berulang selama bola masih menempel pada balok.
        current_bricks = {brick.item: brick for brick in game_objects if isinstance(brick, Brick)}
        new_bricks = [brick for item, brick in current_bricks.items() if item not in self.overlapping_bricks]
        self.overlapping_bricks = set(current_bricks)
        if not new_bricks:
            return []

        # Bola memantul saat kapasitas tembus tidak cukup untuk balok berikutnya.
        bounced = False

        def bounce_from_bricks():
            if len(new_bricks) > 1:
                self.direction[1] *= -1
            else:
                ball_center = (self.get_position()[0] + self.get_position()[2]) * 0.5
                brick_coords = new_bricks[0].get_position()
                if ball_center > brick_coords[2]:
                    self.direction[0] = 1
                elif ball_center < brick_coords[0]:
                    self.direction[0] = -1
                else:
                    self.direction[1] *= -1

        if self.piercing_remaining <= 0:
            bounce_from_bricks()
            bounced = True

        destroyed_bricks = []
        for brick in new_bricks:
            coords = brick.get_position()
            brick_cost = 2 if brick.hits > 1 else 1
            if brick_cost == 2:
                if not bounced:
                    bounce_from_bricks()
                    bounced = True
                self.piercing_remaining = max(0, self.piercing_remaining - brick_cost)
            elif self.piercing_remaining > 0:
                self.piercing_remaining -= brick_cost
            else:
                if not bounced:
                    bounce_from_bricks()
                    bounced = True
            if brick.hit():
                destroyed_bricks.append(((coords[0] + coords[2]) * 0.5, (coords[1] + coords[3]) * 0.5))
        return destroyed_bricks

    def bounce_from_paddle(self, paddle):
        # Pantulkan hanya dari sisi atas, dengan sudut sesuai posisi bola pada platform.
        ball_coords = self.get_position()
        paddle_coords = paddle.get_position()
        if self.direction[1] <= 0:
            return False
        if ball_coords[1] >= paddle_coords[1] or ball_coords[3] < paddle_coords[1]:
            return False
        if ball_coords[2] < paddle_coords[0] or ball_coords[0] > paddle_coords[2]:
            return False

        ball_center = (ball_coords[0] + ball_coords[2]) * 0.5
        paddle_center = (paddle_coords[0] + paddle_coords[2]) * 0.5
        relative_hit = (ball_center - paddle_center) / (paddle.width * 0.5)
        relative_hit = max(-1, min(1, relative_hit))
        angle = math.radians(relative_hit * 70)
        self.direction = [math.sin(angle), -math.cos(angle)]
        self.move(0, paddle_coords[1] - ball_coords[3])
        return True

# Platform yang dikendalikan pemain untuk memantulkan bola.
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 6
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2, x + self.width / 2, y + self.height / 2, fill='yellow')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        # Batasi platform di dalam canvas dan ikutkan bola sebelum permainan dimulai.
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)

# Bata yang hilang setelah menerima jumlah benturan yang diperlukan.
class Brick(GameObject):
    COLORS = {1: '#e74c3c', 2: '#3498db', 3: '#222222'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2, y - self.height / 2, x + self.width / 2, y + self.height / 2, fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        # Perbarui warna bata atau hapus saat ketahanannya habis.
        self.hits -= 1
        if self.hits == 0:
            self.delete()
            return True
        else:
            self.canvas.itemconfig(self.item, fill=Brick.COLORS[self.hits])
            return False


class PowerUp(GameObject):
    TYPES = {
        'triple': ('3x', '#e67e22'),
        'extra': ('+1', '#27ae60'),
        'pierce': ('P3', '#168aad'),
        'clear': ('ROW', '#8e44ad'),
    }

    def __init__(self, canvas, x, y, power_type):
        self.power_type = power_type
        self.speed = 3
        label, color = self.TYPES[power_type]
        item = canvas.create_rectangle(x - 14, y - 10, x + 14, y + 10, fill=color, outline='white')
        self.label_item = canvas.create_text(x, y, text=label, fill='white', font=('Arial', 8, 'bold'))
        super(PowerUp, self).__init__(canvas, item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)
        self.canvas.move(self.label_item, x, y)

    def delete(self):
        self.canvas.delete(self.item)
        self.canvas.delete(self.label_item)

# Mengatur tampilan, input pemain, skor nyawa, dan alur permainan.
class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#aaaaff', width=self.width, height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.balls = []
        self.powerups = {}
        self.powerup_drop_chance = 0.20
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle
        self.brick_limit_y = self.paddle.get_position()[1]
        self.bricks_destroyed_since_layer = 0
        self.score = 0
        self.game_running = False

        # Status tombol memungkinkan platform bergerak terus tanpa auto-repeat OS.
        self.paddle_speed = 12
        self.paddle_directions = {'left': False, 'right': False}
        self.paddle_move_job = None

        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 2)
            self.add_brick(x + 37.5, 70, 1)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None
        self.score_hud = None
        self.update_score_text()
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<KeyPress-Left>', lambda _: self.set_paddle_direction('left', True))
        self.canvas.bind('<KeyRelease-Left>', lambda _: self.set_paddle_direction('left', False))
        self.canvas.bind('<KeyPress-Right>', lambda _: self.set_paddle_direction('right', True))
        self.canvas.bind('<KeyRelease-Right>', lambda _: self.set_paddle_direction('right', False))

    def set_paddle_direction(self, direction, is_pressed):
        # Mulai gerakan langsung saat tombol baru ditekan, lalu abaikan auto-repeat.
        was_pressed = self.paddle_directions[direction]
        self.paddle_directions[direction] = is_pressed
        if is_pressed and not was_pressed:
            self.move_paddle()

    def move_paddle(self):
        # Periksa status tombol setiap 16 ms agar gerakan terasa cepat dan mulus.
        offset = (int(self.paddle_directions['right']) - int(self.paddle_directions['left'])) * self.paddle_speed
        if offset:
            self.paddle.move(offset)

        if any(self.paddle_directions.values()):
            self.paddle_move_job = self.after(16, self.move_paddle)
        else:
            self.paddle_move_job = None

    def setup_game(self):
        # Siapkan bola, tampilan nyawa, dan pesan mulai permainan.
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200, 'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        # Siapkan bola utama di atas platform dan bersihkan bola/power-up lama.
        for ball in self.balls:
            ball.delete()
        self.balls = []
        for powerup in self.powerups.values():
            powerup.delete()
        self.powerups.clear()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.balls.append(Ball(self.canvas, x, paddle_coords[1] - 11))
        self.paddle.set_ball(self.balls[0])

    def add_brick(self, x, y, hits):
        # Buat bata dan simpan referensinya untuk deteksi benturan.
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        # Gambar teks untuk pesan permainan dan HUD.
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_lives_text(self):
        # Tampilkan jumlah nyawa yang tersisa.
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def update_score_text(self):
        # Perbarui skor yang ditampilkan di pojok kanan atas.
        text = 'Score: %s' % self.score
        if self.score_hud is None:
            self.score_hud = self.draw_text(self.width - 50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.score_hud, text=text)

    def start_game(self):
        # Hilangkan pesan mulai lalu jalankan loop permainan.
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_running = True
        self.game_loop()

    def add_brick_layer(self):
        # Turunkan balok lama dan tambahkan baris merah/biru acak di atas.
        if not self.game_running:
            return

        for item in self.canvas.find_withtag('brick'):
            brick = self.items.get(item)
            if brick is not None:
                brick.move(0, brick.height)

        for x in range(5, self.width - 5, 75):
            hits = 2 if random.random() < 0.30 else 1
            self.add_brick(x + 37.5, 50, hits)

        # Sisi atas platform menjadi batas; balok yang menyentuhnya mengakhiri game.
        bricks = self.canvas.find_withtag('brick')
        if any(self.canvas.coords(item)[3] >= self.brick_limit_y for item in bricks):
            self.end_game('Game Over! Bricks reached the paddle!')

    def spawn_powerup(self, x, y):
        # Sebagian balok hancur menjatuhkan salah satu power-up secara acak.
        if random.random() < self.powerup_drop_chance:
            power_type = random.choice(tuple(PowerUp.TYPES))
            powerup = PowerUp(self.canvas, x, y, power_type)
            self.powerups[powerup.item] = powerup

    def register_destroyed_bricks(self, count):
        # Tambahkan skor dan hitung balok untuk memunculkan lapisan berikutnya.
        if count <= 0:
            return
        self.score += count * 100
        self.update_score_text()
        self.bricks_destroyed_since_layer += count
        while self.bricks_destroyed_since_layer >= 8 and self.game_running:
            self.bricks_destroyed_since_layer -= 8
            self.add_brick_layer()

    def split_ball(self):
        # Pecah bola pertama menjadi tiga arah tanpa menggandakan bola lain.
        if not self.balls:
            return
        source = self.balls[0]
        coords = source.get_position()
        center_x = (coords[0] + coords[2]) * 0.5
        center_y = (coords[1] + coords[3]) * 0.5
        for angle in (-math.radians(30), math.radians(30)):
            ball = Ball(self.canvas, center_x, center_y)
            dx, dy = source.direction
            ball.direction = [dx * math.cos(angle) - dy * math.sin(angle),
                              dx * math.sin(angle) + dy * math.cos(angle)]
            ball.speed = source.speed
            ball.piercing_remaining = source.piercing_remaining
            self.balls.append(ball)

    def add_extra_ball(self):
        # Luncurkan bola tambahan dari atas platform.
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        ball = Ball(self.canvas, x, paddle_coords[1] - 11)
        horizontal = random.uniform(-0.45, 0.45)
        ball.direction = [horizontal, -math.sqrt(1 - horizontal ** 2)]
        self.balls.append(ball)

    def clear_bottom_brick_row(self):
        # Hancurkan semua balok pada baris terbawah, termasuk jika hanya tersisa satu.
        brick_ids = self.canvas.find_withtag('brick')
        if not brick_ids:
            return
        lowest_y = max(self.canvas.coords(item)[3] for item in brick_ids)
        bottom_row = [item for item in brick_ids if abs(self.canvas.coords(item)[3] - lowest_y) < 1]
        for item in bottom_row:
            self.canvas.delete(item)
            self.items.pop(item, None)
        self.register_destroyed_bricks(len(bottom_row))

    def activate_powerup(self, power_type):
        # Jalankan efek sesuai power-up yang berhasil ditangkap platform.
        if power_type == 'triple':
            self.split_ball()
        elif power_type == 'extra':
            self.add_extra_ball()
        elif power_type == 'pierce':
            for ball in self.balls:
                ball.piercing_remaining = 3
        elif power_type == 'clear':
            self.clear_bottom_brick_row()

    def update_powerups(self):
        # Jatuhkan power-up ke bawah dan aktifkan saat tertangkap platform.
        paddle_coords = self.paddle.get_position()
        for item, powerup in list(self.powerups.items()):
            powerup.move(0, powerup.speed)
            coords = powerup.get_position()
            caught = (coords[2] >= paddle_coords[0] and coords[0] <= paddle_coords[2]
                      and coords[3] >= paddle_coords[1] and coords[1] <= paddle_coords[3])
            if caught:
                powerup.delete()
                self.powerups.pop(item, None)
                self.activate_powerup(powerup.power_type)
            elif coords[1] > self.height:
                powerup.delete()
                self.powerups.pop(item, None)

    def end_game(self, message):
        # Hentikan loop permainan dan tampilkan hasilnya.
        self.game_running = False
        for ball in self.balls:
            ball.speed = None
        self.draw_text(300, 200, message)

    def game_loop(self):
        # Periksa tabrakan, kondisi menang/kalah, lalu perbarui posisi bola.
        if not self.game_running:
            return

        self.check_collisions()
        if not self.game_running:
            return

        num_bricks = len(self.canvas.find_withtag('brick'))
        
        if num_bricks == 0:
            self.end_game('You win!')
        else:
            for ball in list(self.balls):
                ball.update()
                if ball.get_position()[3] >= self.height:
                    ball.delete()
                    self.balls.remove(ball)

            if not self.balls:
                self.game_running = False
                self.lives -= 1
                if self.lives < 0:
                    self.end_game('You Lose!!! Game Over!')
                else:
                    self.after(1000, self.setup_game)
            else:
                self.after(50, self.game_loop)

    def check_collisions(self):
        # Periksa semua bola, lalu jatuhkan dan ambil power-up.
        for ball in list(self.balls):
            ball.bounce_from_paddle(self.paddle)
            ball_coords = ball.get_position()
            items = self.canvas.find_overlapping(*ball_coords)
            objects = [self.items[item] for item in items
                       if item in self.items and isinstance(self.items[item], Brick)]
            destroyed_bricks = ball.collide(objects)
            for x, y in destroyed_bricks:
                self.spawn_powerup(x, y)
            self.register_destroyed_bricks(len(destroyed_bricks))
            if not self.game_running:
                return
        self.update_powerups()

if __name__ == '__main__':
    # Buat jendela Tkinter dan mulai aplikasi permainan.
    root = tk.Tk()
    root.title('BrickBreaker Game')
    game = Game(root)
    game.mainloop()