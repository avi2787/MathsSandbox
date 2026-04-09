import os
import pygame
import numpy as np
import math
import random
import time
import hashlib
from argon2.low_level import hash_secret_raw, Type

# ------------- basic colors and layout -------------
BG = (15, 17, 26)
PANEL = (25, 27, 38)
CANVAS_BG = (10, 10, 16)
TEXT = (220, 230, 240)
ACCENT = (80, 150, 255)
ALERT = (255, 120, 120)
WIDTH, HEIGHT = 1200, 720
PANEL_W = 280

pygame.init()
FONT = pygame.font.SysFont("consolas", 16)
BIG = pygame.font.SysFont("consolas", 20)

# ------------- tiny UI helpers -------------
class Button:
    def __init__(self, rect, text, on_click):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
    def draw(self, surf):
        color = ACCENT if self.rect.collidepoint(pygame.mouse.get_pos()) else (70, 90, 130)
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        label = FONT.render(self.text, True, BG)
        surf.blit(label, label.get_rect(center=self.rect.center))
    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

class Slider:
    def __init__(self, x, y, w, min_v, max_v, val, name, step=1):
        self.rect = pygame.Rect(x, y, w, 20)
        self.min_v, self.max_v = min_v, max_v
        self.val = val
        self.name = name
        self.dragging = False
        self.step = step
    def draw(self, surf):
        pygame.draw.rect(surf, (60, 70, 90), self.rect, border_radius=4)
        pct = (self.val - self.min_v) / (self.max_v - self.min_v)
        knob_x = self.rect.x + int(pct * self.rect.w)
        pygame.draw.circle(surf, ACCENT, (knob_x, self.rect.centery), 8)
        label = FONT.render(f"{self.name}: {self.val}", True, TEXT)
        surf.blit(label, (self.rect.x, self.rect.y - 18))
    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        if event.type == pygame.MOUSEMOTION and self.dragging:
            pct = (event.pos[0] - self.rect.x) / self.rect.w
            pct = max(0.0, min(1.0, pct))
            raw = self.min_v + pct * (self.max_v - self.min_v)
            snapped = int(round(raw / self.step) * self.step)
            self.val = max(self.min_v, min(self.max_v, snapped))
        return self.val

def draw_text(surf, text, x, y, color=TEXT, wrap=240):
    # simple word wrap so the left panel text doesn’t run off
    words = text.split(" ")
    line = ""
    yy = y
    for w in words:
        test = f"{line}{w} "
        if FONT.size(test)[0] > wrap:
            surf.blit(FONT.render(line, True, color), (x, yy))
            yy += 18
            line = f"{w} "
        else:
            line = test
    surf.blit(FONT.render(line, True, color), (x, yy))
    return yy + 18

# ------------- math helpers -------------
def sieve_primes(n):
    if n < 2:
        return []
    flags = [True] * (n + 1)
    flags[0] = flags[1] = False
    p = 2
    while p * p <= n:
        if flags[p]:
            for k in range(p * p, n + 1, p):
                flags[k] = False
        p += 1
    return [i for i, is_p in enumerate(flags) if is_p]

def twin_primes(n):
    primes = sieve_primes(n)
    twins = []
    prime_set = set(primes)
    for p in primes:
        if p + 2 in prime_set:
            twins.append((p, p + 2))
    return primes, twins

def collatz_steps(start):
    seq = [start]
    n = start
    while n != 1 and len(seq) < 2000:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        seq.append(n)
    return seq

def birthday_probability(people, days=365):
    prob_no = 1.0
    for i in range(people):
        prob_no *= (days - i) / days
    return 1 - prob_no

def hash_sha_iter(data, rounds=1000):
    digest = data
    for _ in range(rounds):
        digest = hashlib.sha256(digest).digest()
    return digest

def hash_argon2(data, t=2, m=2**15, p=1):
    return hash_secret_raw(
        secret=data,
        salt=b"fixed_salt",
        time_cost=t,
        memory_cost=m,
        parallelism=p,
        hash_len=32,
        type=Type.ID,
    )

# ------------- modes -------------
class MandelbrotMode:
    def __init__(self, canvas):
        self.canvas = canvas
        self.max_iter = 80
        self.zoom = 1.0
        self.center = (-0.5, 0.0)
        self.needs_redraw = True
        self.surface = pygame.Surface(canvas.size)
    def controls(self, panel):
        slider_y = panel.control_start_y()
        panel.sliders = [
            Slider(panel.x + 20, slider_y, PANEL_W - 40, 20, 400, self.max_iter, "Iterations", 5)
        ]
        panel.info = "Mandelbrot: click canvas to zoom\nRight-click to zoom out."
    def handle_canvas_click(self, pos, button):
        cx, cy = self.canvas.top_left()
        w, h = self.canvas.size
        x = (pos[0] - cx) / w * (3.0 / self.zoom) + (self.center[0] - 1.5 / self.zoom)
        y = (pos[1] - cy) / h * (2.0 / self.zoom) + (self.center[1] - 1.0 / self.zoom)
        if button == 1:
            self.center = (x, y)
            self.zoom *= 1.8
        elif button == 3:
            self.zoom /= 1.8
        self.needs_redraw = True
    def update_params(self, sliders):
        self.max_iter = sliders[0].val
        self.needs_redraw = True
    def render(self):
        if not self.needs_redraw:
            return self.surface
        w, h = self.canvas.size
        xs = np.linspace(self.center[0] - 1.5 / self.zoom, self.center[0] + 1.5 / self.zoom, w)
        ys = np.linspace(self.center[1] - 1.0 / self.zoom, self.center[1] + 1.0 / self.zoom, h)
        surf_array = pygame.surfarray.pixels3d(self.surface)
        for j, y in enumerate(ys):
            for i, x in enumerate(xs):
                c = complex(x, y)
                z = 0 + 0j
                iter_count = 0
                while abs(z) <= 2 and iter_count < self.max_iter:
                    z = z * z + c
                    iter_count += 1
                hue = int(255 * iter_count / self.max_iter)
                surf_array[i, j] = (hue, int(hue * 0.6), int(hue * 0.2))
        del surf_array
        self.needs_redraw = False
        return self.surface

class TwinPrimeMode:
    def __init__(self, canvas):
        self.canvas = canvas
        self.limit = 500
        self.primes = []
        self.twins = []
        self.surface = pygame.Surface(canvas.size)
        self.compute()
    def compute(self):
        self.primes, self.twins = twin_primes(self.limit)
        self.draw()
    def controls(self, panel):
        slider_y = panel.control_start_y()
        panel.sliders = [
            Slider(panel.x + 20, slider_y, PANEL_W - 40, 50, 5000, self.limit, "Limit", 50)
        ]
        panel.info = "Twin primes up to N.\nDots for primes, lines for twin pairs."
    def handle_canvas_click(self, pos, button):
        pass
    def update_params(self, sliders):
        new_limit = sliders[0].val
        if new_limit != self.limit:
            self.limit = new_limit
            self.compute()
    def draw(self):
        self.surface.fill(CANVAS_BG)
        w, h = self.canvas.size
        if not self.primes:
            return
        max_n = self.limit
        for p in self.primes:
            x = int(p / max_n * (w - 40)) + 20
            y = h - 40 - int(math.log(p + 1) / math.log(max_n + 2) * (h - 80))
            pygame.draw.circle(self.surface, ACCENT, (x, y), 2)
        for a, b in self.twins:
            x1 = int(a / max_n * (w - 40)) + 20
            x2 = int(b / max_n * (w - 40)) + 20
            y = h - 50
            pygame.draw.line(self.surface, ALERT, (x1, y), (x2, y), 2)
    def render(self):
        return self.surface

class CollatzMode:
    def __init__(self, canvas):
        self.canvas = canvas
        self.start = 27
        self.seq = collatz_steps(self.start)
        self.surface = pygame.Surface(canvas.size)
        self.draw()
    def controls(self, panel):
        slider_y = panel.control_start_y()
        panel.sliders = [
            Slider(panel.x + 20, slider_y, PANEL_W - 40, 2, 1000, self.start, "Start", 1)
        ]
        panel.info = "Collatz trajectory.\nY is value, X is step."
    def handle_canvas_click(self, pos, button):
        pass
    def update_params(self, sliders):
        new_start = sliders[0].val
        if new_start != self.start:
            self.start = new_start
            self.seq = collatz_steps(self.start)
            self.draw()
    def draw(self):
        self.surface.fill(CANVAS_BG)
        w, h = self.canvas.size
        if len(self.seq) < 2:
            return
        max_val = max(self.seq)
        max_step = len(self.seq) - 1
        points = []
        for i, v in enumerate(self.seq):
            x = int(i / max_step * (w - 40)) + 20
            y = h - 20 - int(v / max_val * (h - 40))
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(self.surface, ACCENT, False, points, 2)
        for p in points:
            pygame.draw.circle(self.surface, (180, 200, 255), p, 2)
    def render(self):
        return self.surface

class SieveMode:
    def __init__(self, canvas):
        self.canvas = canvas
        self.limit = 120
        self.flags = []
        self.current = 2
        self.surface = pygame.Surface(canvas.size)
        self.reset()
    def reset(self):
        # standard sieve flags
        self.flags = [True] * (self.limit + 1)
        if self.limit >= 0:
            self.flags[0] = False
        if self.limit >= 1:
            self.flags[1] = False
        self.current = 2
        self.draw()
    def step(self):
        # one sieve step to mark multiples
        while self.current * self.current <= self.limit and not self.flags[self.current]:
            self.current += 1
        if self.current * self.current > self.limit:
            return False
        for k in range(self.current * self.current, self.limit + 1, self.current):
            self.flags[k] = False
        self.current += 1
        return True
    def controls(self, panel):
        slider_y = panel.control_start_y()
        panel.sliders = [
            Slider(panel.x + 20, slider_y, PANEL_W - 40, 20, 400, self.limit, "Limit", 10)
        ]
        panel.info = "Sieve of Eratosthenes.\nPress 'Step' to mark multiples."
        panel.extra_button = ("Step", self.step)
        panel.reset_button = ("Reset", self.reset)
    def handle_canvas_click(self, pos, button):
        pass
    def update_params(self, sliders):
        new_limit = sliders[0].val
        if new_limit != self.limit:
            self.limit = new_limit
            self.reset()
    def draw(self):
        self.surface.fill(CANVAS_BG)
        w, h = self.canvas.size
        cols = int(math.sqrt(self.limit)) + 1
        size = min((w - 40) // cols, (h - 40) // cols)
        x0, y0 = 20, 20
        for n in range(self.limit + 1):
            r = n // cols
            c = n % cols
            rect = pygame.Rect(x0 + c * size, y0 + r * size, size - 2, size - 2)
            color = (60, 60, 70)
            if n == 0 or n == 1:
                color = (40, 40, 50)
            elif self.flags[n]:
                color = (60, 200, 150)
            else:
                color = (200, 80, 80)
            pygame.draw.rect(self.surface, color, rect)
    def render(self):
        self.draw()
        return self.surface

class BirthdayMode:
    def __init__(self, canvas):
        self.canvas = canvas
        self.people = 23
        self.sim_trials = []
        self.surface = pygame.Surface(canvas.size)
        self.draw()
    def controls(self, panel):
        slider_y = panel.control_start_y()
        panel.sliders = [
            Slider(panel.x + 20, slider_y, PANEL_W - 40, 2, 200, self.people, "People", 1)
        ]
        panel.info = "Birthday paradox: prob of shared birthday.\nShows formula and simulation."
    def handle_canvas_click(self, pos, button):
        pass
    def update_params(self, sliders):
        self.people = sliders[0].val
        self.draw()
    def simulate(self, trials=200):
        # run quick Monte Carlo; not perfect but illustrative
        count = 0
        for _ in range(trials):
            seen = set()
            collision = False
            for _ in range(self.people):
                b = random.randint(1, 365)
                if b in seen:
                    collision = True
                    break
                seen.add(b)
            if collision:
                count += 1
        self.sim_trials.append(count / trials)
    def draw(self):
        self.surface.fill(CANVAS_BG)
        prob = birthday_probability(self.people)
        self.simulate(50)
        sim_avg = sum(self.sim_trials[-50:]) / max(1, len(self.sim_trials[-50:]))
        w, h = self.canvas.size
        bar_w = 100
        pygame.draw.rect(self.surface, (80, 90, 130), (w//3, h//2, bar_w, -int(prob * h//3)))
        pygame.draw.rect(self.surface, (180, 120, 220), (w//3 + 140, h//2, bar_w, -int(sim_avg * h//3)))
        txt1 = BIG.render(f"Formula: {prob*100:.1f}%", True, TEXT)
        txt2 = BIG.render(f"Sim: {sim_avg*100:.1f}%", True, TEXT)
        self.surface.blit(txt1, (w//3 - 10, h//2 + 20))
        self.surface.blit(txt2, (w//3 + 130, h//2 + 20))
    def render(self):
        return self.surface

class HashMode:
    def __init__(self, canvas):
        self.canvas = canvas
        self.rounds = 500
        self.argon_time = None
        self.sha_time = None
        self.leading_hits = []
        self.surface = pygame.Surface(canvas.size)
        self.run_once()
    def controls(self, panel):
        slider_y = panel.control_start_y()
        panel.sliders = [
            Slider(panel.x + 20, slider_y, PANEL_W - 40, 10, 2000, self.rounds, "SHA Rounds", 10)
        ]
        panel.info = "Hash collisions: Argon2id vs iterated SHA-256.\nShowing time and leading-bit matches."
        panel.extra_button = ("Run", self.run_once)
    def handle_canvas_click(self, pos, button):
        pass
    def update_params(self, sliders):
        self.rounds = sliders[0].val
    def run_once(self):
        data = os.urandom(32)  # os.urandom works everywhere
        start = time.time()
        sha_out = hash_sha_iter(data, self.rounds)
        self.sha_time = time.time() - start

        start = time.time()
        argon_out = hash_argon2(data, t=2)
        self.argon_time = time.time() - start

        # quick “how many leading bits match” metric
        lead = 0
        for a, b in zip(sha_out, argon_out):
            x = a ^ b
            for i in range(8):
                if x & (128 >> i) == 0:
                    lead += 1
                else:
                    break
            if x != 0:
                break
        self.leading_hits.append(lead)
        if len(self.leading_hits) > 200:
            self.leading_hits.pop(0)
        self.draw()
    def draw(self):
        self.surface.fill(CANVAS_BG)
        w, h = self.canvas.size
        if self.leading_hits:
            max_lead = max(self.leading_hits + [1])
            for i, v in enumerate(self.leading_hits):
                x = int(i / len(self.leading_hits) * (w - 40)) + 20
                bar_h = int(v / max_lead * (h - 100))
                pygame.draw.rect(self.surface, ACCENT, (x, h - 40 - bar_h, 4, bar_h))
        lines = [
            f"SHA-256 rounds: {self.rounds}",
            f"SHA time: {self.sha_time*1000:.1f} ms",
            f"Argon2id time: {self.argon_time*1000:.1f} ms",
            "Metric: leading equal bits between outputs"
        ]
        y = 20
        for ln in lines:
            self.surface.blit(FONT.render(ln, True, TEXT), (20, y))
            y += 20
    def render(self):
        return self.surface

# ------------- canvas/panel helpers -------------
class Canvas:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.size = (w, h)
    def draw(self, surf, content):
        pygame.draw.rect(surf, CANVAS_BG, self.rect)
        surf.blit(content, self.rect)
    def top_left(self):
        return self.rect.x, self.rect.y

class ControlPanel:
    def __init__(self, x, y, w, h):
        # keep x/y so the mode controls can position sliders easily
        self.x, self.y, self.w, self.h = x, y, w, h
        self.rect = pygame.Rect(x, y, w, h)
        self.buttons = []
        self.temp_buttons = []  # extra/reset buttons refreshed each frame
        self.sliders = []
        self.info = ""
        self.extra_button = None
        self.reset_button = None
    def control_start_y(self):
        # place controls below the mode buttons so they don't overlap
        if self.buttons:
            return self.buttons[-1].rect.bottom + 24
        return self.y + 60
    def draw(self, surf):
        pygame.draw.rect(surf, PANEL, self.rect)
        for b in self.buttons:
            b.draw(surf)
        for s in self.sliders:
            s.draw(surf)
        info_y = self.control_start_y()
        if self.sliders:
            info_y = max(s.rect.bottom for s in self.sliders) + 16
        yy = draw_text(surf, self.info, self.rect.x + 20, info_y)
        # rebuild temp buttons each draw (avoids piling duplicates)
        self.temp_buttons = []
        if self.extra_button:
            btn = Button((self.rect.x + 20, yy + 10, self.rect.w - 40, 28), self.extra_button[0],
self.extra_button[1])
            btn.draw(surf)
            self.temp_buttons.append(btn)
        if self.reset_button:
            btn = Button((self.rect.x + 20, yy + 45, self.rect.w - 40, 28), "Reset", self.reset_button[1])
            btn.draw(surf)
            self.temp_buttons.append(btn)
    def handle(self, event):
        for b in list(self.buttons) + list(self.temp_buttons):
            b.handle(event)
        for s in self.sliders:
            s.handle(event)

# ------------- main app -------------
class SandboxApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Math/CS Sandbox (dark)")
        self.canvas = Canvas(PANEL_W, 0, WIDTH - PANEL_W, HEIGHT)
        self.panel = ControlPanel(0, 0, PANEL_W, HEIGHT)
        self.modes = {
            "Mandelbrot": MandelbrotMode(self.canvas),
            "Twin Primes": TwinPrimeMode(self.canvas),
            "Collatz": CollatzMode(self.canvas),
            "Sieve": SieveMode(self.canvas),
            "Birthday": BirthdayMode(self.canvas),
            "Hash": HashMode(self.canvas),
        }
        self.mode_order = list(self.modes.keys())
        self.current_mode = self.mode_order[0]
        self.build_buttons()
        self.modes[self.current_mode].controls(self.panel)
    def build_buttons(self):
        self.panel.buttons = []
        y = 20
        for name in self.mode_order:
            def make_cb(n=name):
                return lambda: self.switch_mode(n)
            btn = Button((20, y, PANEL_W - 40, 28), name, make_cb())
            self.panel.buttons.append(btn)
            y += 36
    def switch_mode(self, name):
        self.current_mode = name
        self.panel.buttons = []
        self.build_buttons()
        self.panel.sliders = []
        self.panel.extra_button = None
        self.panel.reset_button = None
        self.modes[name].controls(self.panel)
    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.pos[0] > PANEL_W:
                    self.modes[self.current_mode].handle_canvas_click(event.pos, event.button)
                self.panel.handle(event)
            # update mode from sliders
            self.modes[self.current_mode].update_params(self.panel.sliders)
            # render
            self.screen.fill(BG)
            self.panel.draw(self.screen)
            content = self.modes[self.current_mode].render()
            self.canvas.draw(self.screen, content)
            pygame.display.flip()
            clock.tick(30)
        pygame.quit()

if __name__ == "__main__":
    SandboxApp().run()