"""
VOX Face — Contained particle field.
Particles live inside a circular boundary. State changes their behavior.
Clean, minimal, violet/purple on near-black.
"""

import math
import random
import ctypes
import ctypes.wintypes
import pygame

# ── Config ─────────────────────────────────────────────────────────────────────
W, H        = 400, 440
FPS         = 60
N           = 80          # fewer = cleaner
FIELD_R     = 140         # particles stay within this radius
CONNECT_D   = 90          # max distance for connecting lines

BG  = (7, 6, 14)
COL = {
    "idle":      (100,  45, 180),
    "listening": (140,  75, 250),
    "thinking":  ( 80,  25, 200),
    "speaking":  (185, 105, 255),
}


class Particle:
    def __init__(self, cx: float, cy: float):
        # Spawn within the field
        angle  = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, FIELD_R * 0.9)
        self.x  = cx + math.cos(angle) * radius
        self.y  = cy + math.sin(angle) * radius
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(-0.3, 0.3)
        self.r  = random.uniform(1.5, 3.0)

    def update(self, state: str, cx: float, cy: float):
        dx_c = cx - self.x
        dy_c = cy - self.y
        dist  = math.hypot(dx_c, dy_c) or 1

        # ── Boundary pull — always active, scales up near edge ────────────────
        if dist > FIELD_R * 0.75:
            strength = ((dist - FIELD_R * 0.75) / (FIELD_R * 0.25)) * 0.12
            self.vx += dx_c / dist * strength
            self.vy += dy_c / dist * strength

        # ── State behaviour ───────────────────────────────────────────────────
        if state == "idle":
            self.vx += random.uniform(-0.02, 0.02)
            self.vy += random.uniform(-0.02, 0.02)
            self._clamp(0.45)

        elif state == "listening":
            # Gentle orbit around center
            self.vx += (-dy_c / dist) * 0.07
            self.vy += ( dx_c / dist) * 0.07
            self.vx += dx_c / dist * 0.02  # slight inward pull to keep orbit tight
            self.vy += dy_c / dist * 0.02
            self._clamp(2.4)

        elif state == "thinking":
            # Tighter spiral inward
            if dist > 20:
                self.vx += dx_c / dist * 0.07 + (-dy_c / dist) * 0.04
                self.vy += dy_c / dist * 0.07 + ( dx_c / dist) * 0.04
            self._clamp(2.6)

        elif state == "speaking":
            # Burst outward, boundary will pull them back
            if dist < FIELD_R and dist > 0:
                f = (1 - dist / FIELD_R) * 0.15
                self.vx -= dx_c / dist * f
                self.vy -= dy_c / dist * f
            self._clamp(3.0)

        self.x += self.vx
        self.y += self.vy

        # Hard clamp — nothing escapes the field + margin
        hard_r = FIELD_R * 1.25
        if dist > hard_r:
            self.x = cx + dx_c / dist * hard_r
            self.y = cy + dy_c / dist * hard_r
            self.vx *= 0.3
            self.vy *= 0.3

    def _clamp(self, mx: float):
        s = math.hypot(self.vx, self.vy)
        if s > mx:
            self.vx = self.vx / s * mx
            self.vy = self.vy / s * mx


def run_face(state_ref: dict):
    pygame.init()
    pygame.display.set_caption("VOX")
    screen     = pygame.display.set_mode((W, H), pygame.NOFRAME)
    clock      = pygame.time.Clock()
    font_title = pygame.font.SysFont("Consolas", 15, bold=True)
    font_state = pygame.font.SysFont("Consolas", 9)
    font_text  = pygame.font.SysFont("Consolas", 10)

    cx     = W / 2
    cy     = (H - 90) / 2
    particles  = [Particle(cx, cy) for _ in range(N)]
    glow_surf  = pygame.Surface((W, H), pygame.SRCALPHA)
    phase      = 0.0
    dragging   = False
    drag_off   = (0, 0)

    # Pin top-right, always on top
    try:
        hwnd = pygame.display.get_wm_info()["window"]
        sw   = ctypes.windll.user32.GetSystemMetrics(0)
        ctypes.windll.user32.SetWindowPos(hwnd, -1, sw - W - 20, 40, 0, 0, 0x0001 | 0x0002)
    except Exception:
        pass

    while True:
        clock.tick(FPS)
        phase = (phase + 0.035) % (2 * math.pi)
        pulse = (math.sin(phase) + 1) / 2

        state = state_ref.get("state", "idle")
        text  = state_ref.get("text",  "")
        col   = COL[state]

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type in (pygame.QUIT,):
                pygame.quit(); return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); return
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
                        0, 0, 0x0001 | 0x0002)
                except Exception:
                    pass

        # ── Update ────────────────────────────────────────────────────────────
        for p in particles:
            p.update(state, cx, cy)

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BG)

        # Connecting lines — only between particles inside the field
        for i in range(N):
            for j in range(i + 1, N):
                pi, pj = particles[i], particles[j]
                d = math.hypot(pi.x - pj.x, pi.y - pj.y)
                if d < CONNECT_D:
                    a = int((1 - d / CONNECT_D) * 65)
                    pygame.draw.line(
                        screen,
                        (max(0, col[0]-40), max(0, col[1]-25), col[2]),
                        (int(pi.x), int(pi.y)),
                        (int(pj.x), int(pj.y)), 1)

        # Particles
        for p in particles:
            b = 0.6 + pulse * 0.4
            c = (min(255, int(col[0]*b + 50)), min(255, int(col[1]*b + 15)), min(255, col[2]))
            pygame.draw.circle(screen, c, (int(p.x), int(p.y)), max(1, int(p.r)))

        # Central glow
        glow_surf.fill((0, 0, 0, 0))
        for i in range(5, 0, -1):
            gr = int(16 + pulse * 7) + i * 10
            ga = int((0.2 + pulse * 0.4) * (50 - i * 7))
            if ga > 0:
                pygame.draw.circle(glow_surf, (*col, ga), (int(cx), int(cy)), gr)
        screen.blit(glow_surf, (0, 0))
        pygame.draw.circle(screen, col, (int(cx), int(cy)), int(14 + pulse * 4))
        pygame.draw.circle(screen, (235, 210, 255), (int(cx)-4, int(cy)-5), 3)

        # ── UI panel ──────────────────────────────────────────────────────────
        py = H - 85
        pygame.draw.line(screen, (45, 25, 80), (40, py), (W-40, py), 1)

        title = font_title.render("V O X", True, (190, 160, 255))
        screen.blit(title, (W//2 - title.get_width()//2, py + 10))

        ss = font_state.render(state.upper(), True, (85, 55, 140))
        screen.blit(ss, (W//2 - ss.get_width()//2, py + 32))

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
                ts = font_text.render(ln, True, (130, 100, 185))
                screen.blit(ts, (W//2 - ts.get_width()//2, py + 50 + i*14))

        pygame.display.flip()
