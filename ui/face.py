"""
VOX Face — Particle constellation UI.
120 particles connected by lines when close. State-aware behavior.
Dark bg, violet/purple palette. Runs at 60fps via pygame/SDL2.
"""

import math
import random
import ctypes
import ctypes.wintypes
import pygame

# ── Config ─────────────────────────────────────────────────────────────────────
W, H      = 420, 460
FPS       = 60
N         = 120
CONNECT_D = 100

# ── Palette ────────────────────────────────────────────────────────────────────
BG  = (7, 6, 14)
COL = {
    "idle":      (110,  50, 190),
    "listening": (150,  80, 255),
    "thinking":  ( 90,  30, 210),
    "speaking":  (190, 110, 255),
}


class Particle:
    def __init__(self):
        self.x  = random.uniform(40, W - 40)
        self.y  = random.uniform(40, H - 120)
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(-0.4, 0.4)
        self.r  = random.uniform(1.5, 3.2)
        self.a  = random.randint(130, 230)

    def update(self, state: str, cx: float, cy: float):
        if state == "idle":
            self.vx += random.uniform(-0.025, 0.025)
            self.vy += random.uniform(-0.025, 0.025)
            self._clamp(0.55)
        elif state == "listening":
            dx, dy = cx - self.x, cy - self.y
            d = math.hypot(dx, dy) or 1
            self.vx += dx / d * 0.035 + (-dy / d) * 0.075
            self.vy += dy / d * 0.035 + ( dx / d) * 0.075
            self._clamp(2.6)
        elif state == "thinking":
            dx, dy = cx - self.x, cy - self.y
            d = math.hypot(dx, dy) or 1
            if d > 28:
                self.vx += dx / d * 0.08 + (-dy / d) * 0.045
                self.vy += dy / d * 0.08 + ( dx / d) * 0.045
            self._clamp(2.8)
        elif state == "speaking":
            dx, dy = self.x - cx, self.y - cy
            d = math.hypot(dx, dy) or 1
            if d < 190:
                f = (190 - d) / 190 * 0.18
                self.vx += dx / d * f
                self.vy += dy / d * f
            self._clamp(3.2)

        self.x += self.vx
        self.y += self.vy
        if self.x < -20:  self.x = W + 10
        if self.x > W+20: self.x = -10
        if self.y < -20:  self.y = H + 10
        if self.y > H+20: self.y = -10

    def _clamp(self, mx: float):
        s = math.hypot(self.vx, self.vy)
        if s > mx:
            self.vx = self.vx / s * mx
            self.vy = self.vy / s * mx


def run_face(state_ref: dict):
    """Blocking pygame loop. state_ref is shared with the voice thread."""
    pygame.init()
    pygame.display.set_caption("VOX")
    screen     = pygame.display.set_mode((W, H), pygame.NOFRAME)
    clock      = pygame.time.Clock()
    font_title = pygame.font.SysFont("Consolas", 16, bold=True)
    font_state = pygame.font.SysFont("Consolas", 10)
    font_text  = pygame.font.SysFont("Consolas", 11)
    particles  = [Particle() for _ in range(N)]
    glow_surf  = pygame.Surface((W, H), pygame.SRCALPHA)
    cx, cy     = W / 2, (H - 100) / 2
    phase      = 0.0
    dragging   = False
    drag_off   = (0, 0)

    # Pin to top-right corner, always on top
    try:
        hwnd = pygame.display.get_wm_info()["window"]
        sw   = ctypes.windll.user32.GetSystemMetrics(0)
        ctypes.windll.user32.SetWindowPos(hwnd, -1, sw - W - 20, 40, 0, 0, 0x0001 | 0x0002)
    except Exception:
        pass

    while True:
        clock.tick(FPS)
        phase = (phase + 0.04) % (2 * math.pi)
        pulse = (math.sin(phase) + 1) / 2
        state = state_ref.get("state", "idle")
        text  = state_ref.get("text",  "")
        col   = COL[state]

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                dragging = True
                drag_off = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                mx, my = pygame.mouse.get_pos()
                try:
                    hwnd = pygame.display.get_wm_info()["window"]
                    rect = ctypes.wintypes.RECT()
                    ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
                    ctypes.windll.user32.SetWindowPos(
                        hwnd, -1,
                        rect.left + mx - drag_off[0],
                        rect.top  + my - drag_off[1],
                        0, 0, 0x0001 | 0x0002
                    )
                except Exception:
                    pass

        # ── Update ────────────────────────────────────────────────────────────
        for p in particles:
            p.update(state, cx, cy)

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BG)

        # Lines between nearby particles
        for i in range(N):
            for j in range(i + 1, N):
                pi, pj = particles[i], particles[j]
                d = math.hypot(pi.x - pj.x, pi.y - pj.y)
                if d < CONNECT_D:
                    alpha = int((1 - d / CONNECT_D) * 70)
                    c = (max(0, col[0]-30), max(0, col[1]-20), col[2], alpha)
                    pygame.draw.line(screen, c[:3],
                                     (int(pi.x), int(pi.y)),
                                     (int(pj.x), int(pj.y)), 1)

        # Particles
        for p in particles:
            brightness = 0.65 + pulse * 0.35
            c = (
                min(255, int(col[0] * brightness + 60)),
                min(255, int(col[1] * brightness + 20)),
                min(255, int(col[2] * brightness)),
            )
            pygame.draw.circle(screen, c, (int(p.x), int(p.y)), max(1, int(p.r)))

        # Central glow
        glow_surf.fill((0, 0, 0, 0))
        for i in range(6, 0, -1):
            gr = int(22 + pulse * 8) + i * 9
            ga = int((0.25 + pulse * 0.35) * (55 - i * 7))
            if ga > 0:
                pygame.draw.circle(glow_surf, (*col, ga), (int(cx), int(cy)), gr)
        screen.blit(glow_surf, (0, 0))
        pygame.draw.circle(screen, col, (int(cx), int(cy)), int(18 + pulse * 5))
        pygame.draw.circle(screen, (235, 210, 255), (int(cx) - 5, int(cy) - 6), 4)

        # ── UI panel ──────────────────────────────────────────────────────────
        panel_y = H - 100
        pygame.draw.line(screen, (55, 30, 90), (35, panel_y), (W - 35, panel_y), 1)

        title = font_title.render("V O X", True, (195, 165, 255))
        screen.blit(title, (W // 2 - title.get_width() // 2, panel_y + 10))

        state_s = font_state.render(state.upper(), True, (95, 65, 150))
        screen.blit(state_s, (W // 2 - state_s.get_width() // 2, panel_y + 34))

        if text:
            words, line, lines = text.split(), "", []
            for w in words:
                test = (line + " " + w).strip()
                if font_text.size(test)[0] < W - 60:
                    line = test
                else:
                    if line: lines.append(line)
                    line = w
            if line: lines.append(line)
            for i, ln in enumerate(lines[:2]):
                ts = font_text.render(ln, True, (140, 110, 195))
                screen.blit(ts, (W // 2 - ts.get_width() // 2, panel_y + 52 + i * 15))

        pygame.display.flip()

    pygame.quit()
