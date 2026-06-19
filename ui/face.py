"""
VOX Face — Particle sphere.
Particles live on a rotating 3D sphere surface projected to 2D.
Sphere radius pulses organically. No central dot — particles ARE the sphere.
"""

import math
import random
import ctypes
import ctypes.wintypes
import pygame

# ── Config ──────────────────────────────────────────────────────────────────
W, H      = 400, 440
FPS       = 60
N         = 90
BASE_R    = 130      # sphere base radius
CONNECT_D = 55       # screen-space line threshold

BG  = (7, 6, 14)
COL = {
    "idle":      (100,  45, 180),
    "listening": (140,  75, 250),
    "thinking":  ( 80,  25, 200),
    "speaking":  (185, 105, 255),
}

# Pulse amplitude per state (sphere breathes by this many px)
AMP = {"idle": 7, "listening": 16, "thinking": 10, "speaking": 32}

# Rotation speed per state (radians/frame)
ROT_SPEED = {"idle": 0.004, "listening": 0.009, "thinking": 0.012, "speaking": 0.007}


class Particle:
    def __init__(self):
        # Fibonacci sphere distribution — evenly spread points
        pass

    def set_angles(self, theta: float, phi: float):
        self.theta = theta   # azimuth 0→2π
        self.phi   = phi     # polar   0→π
        self.size  = random.uniform(1.4, 2.8)

    def xyz(self):
        return (
            math.sin(self.phi) * math.cos(self.theta),
            math.sin(self.phi) * math.sin(self.theta),
            math.cos(self.phi),
        )

    def project(self, rot_y: float, rot_x: float, r: float, cx: float, cy: float):
        x, y, z = self.xyz()

        # Rotate Y
        x2 =  x * math.cos(rot_y) + z * math.sin(rot_y)
        z2 = -x * math.sin(rot_y) + z * math.cos(rot_y)

        # Rotate X
        y3 = y * math.cos(rot_x) - z2 * math.sin(rot_x)
        z3 = y * math.sin(rot_x) + z2 * math.cos(rot_x)

        sx = cx + x2 * r
        sy = cy + y3 * r
        depth = z3   # -1 (back) to +1 (front)
        return sx, sy, depth


def fibonacci_sphere(n: int):
    """Evenly distribute n points on a unit sphere."""
    pts = []
    phi_golden = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        y   = 1 - (i / (n - 1)) * 2
        r   = math.sqrt(max(0, 1 - y * y))
        th  = phi_golden * i
        pts.append((math.atan2(r * math.sin(th), r * math.cos(th)),
                    math.acos(max(-1, min(1, y)))))
    return pts


def run_face(state_ref: dict):
    pygame.init()
    pygame.display.set_caption("VOX")
    screen     = pygame.display.set_mode((W, H), pygame.NOFRAME)
    clock      = pygame.time.Clock()
    font_title = pygame.font.SysFont("Consolas", 15, bold=True)
    font_state = pygame.font.SysFont("Consolas",  9)
    font_text  = pygame.font.SysFont("Consolas", 10)

    cx = W / 2
    cy = (H - 90) / 2

    # Build particles on Fibonacci sphere
    particles = [Particle() for _ in range(N)]
    for p, (theta, phi) in zip(particles, fibonacci_sphere(N)):
        p.set_angles(theta, phi)

    glow_surf = pygame.Surface((W, H), pygame.SRCALPHA)

    rot_y = 0.0
    rot_x = 0.25      # slight tilt so it doesn't look flat

    # Three oscillators for organic pulsation
    ph1, ph2, ph3 = 0.0, 0.0, 0.0

    dragging  = False
    drag_off  = (0, 0)

    # Pin top-right, always on top
    try:
        hwnd = pygame.display.get_wm_info()["window"]
        sw   = ctypes.windll.user32.GetSystemMetrics(0)
        ctypes.windll.user32.SetWindowPos(hwnd, -1, sw - W - 20, 40, 0, 0, 0x0001 | 0x0002)
    except Exception:
        pass

    while True:
        clock.tick(FPS)

        state = state_ref.get("state", "idle")
        text  = state_ref.get("text",  "")
        col   = COL[state]
        amp   = AMP[state]

        # Advance oscillators — different speeds for organic feel
        ph1 = (ph1 + 0.038) % (2 * math.pi)
        ph2 = (ph2 + 0.087) % (2 * math.pi)
        ph3 = (ph3 + 0.053) % (2 * math.pi)

        pulse = (
            math.sin(ph1)          * 0.50 +
            math.sin(ph2 * 2.3)    * 0.30 +
            math.sin(ph3 * 3.7)    * 0.20
        )  # -1 → +1, complex waveform
        sphere_r = BASE_R + amp * pulse

        rot_y = (rot_y + ROT_SPEED[state]) % (2 * math.pi)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                dragging = True; drag_off = pygame.mouse.get_pos()
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

        # ── Project all particles ─────────────────────────────────────────────
        projected = []   # (sx, sy, depth, particle)
        for p in particles:
            sx, sy, depth = p.project(rot_y, rot_x, sphere_r, cx, cy)
            projected.append((sx, sy, depth, p))

        # Sort back-to-front for painter's algorithm
        projected.sort(key=lambda t: t[2])

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BG)

        # Connecting lines — only front-facing particles
        front = [(sx, sy, depth, p) for sx, sy, depth, p in projected if depth > -0.3]
        for i in range(len(front)):
            for j in range(i + 1, len(front)):
                sx1, sy1, d1, _ = front[i]
                sx2, sy2, d2, _ = front[j]
                dist = math.hypot(sx1-sx2, sy1-sy2)
                if dist < CONNECT_D:
                    fade = int((1 - dist / CONNECT_D) * 55 * ((d1 + d2) / 2 + 1) / 2)
                    if fade > 3:
                        pygame.draw.line(
                            screen,
                            (max(0, col[0]-40), max(0, col[1]-25), col[2]),
                            (int(sx1), int(sy1)), (int(sx2), int(sy2)), 1)

        # Particles — depth-shaded (back = dim, front = bright)
        for sx, sy, depth, p in projected:
            norm  = (depth + 1) / 2        # 0 (back) → 1 (front)
            alpha = int(80 + norm * 175)
            size  = max(1, int(p.size * (0.5 + norm * 0.7)))
            r = min(255, int(col[0] * (0.4 + norm * 0.6) + 40 * norm))
            g = min(255, int(col[1] * (0.4 + norm * 0.6) + 10 * norm))
            b = min(255, int(col[2] * (0.5 + norm * 0.5)))
            pygame.draw.circle(screen, (r, g, b), (int(sx), int(sy)), size)

        # ── UI panel ──────────────────────────────────────────────────────────
        py = H - 85
        pygame.draw.line(screen, (40, 22, 75), (40, py), (W-40, py), 1)

        title = font_title.render("V O X", True, (190, 160, 255))
        screen.blit(title, (W//2 - title.get_width()//2, py + 10))

        ss = font_state.render(state.upper(), True, (80, 52, 135))
        screen.blit(ss, (W//2 - ss.get_width()//2, py + 30))

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
                ts = font_text.render(ln, True, (125, 95, 180))
                screen.blit(ts, (W//2 - ts.get_width()//2, py + 47 + i*14))

        pygame.display.flip()
