"""
VOX Face — Minimal purple/violet UI.
A single breathing orb on a dark background. Clean. No noise.
"""

import math
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Qt, QTimer, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QFontDatabase


# ── Palette ────────────────────────────────────────────────────────────────────
BG         = QColor(7, 6, 14)          # Near-black with a purple tint
ORB_CORE   = QColor(110, 40, 190)      # Deep violet
ORB_MID    = QColor(148, 68, 230)      # Medium purple
GLOW       = QColor(160, 80, 255)      # Bright violet glow
HIGHLIGHT  = QColor(220, 190, 255, 60) # Inner highlight
TEXT_DIM   = QColor(120, 90, 170)      # Muted purple text
TEXT_BRIGHT= QColor(195, 165, 255)     # Bright label text
ARC_COLOR  = QColor(180, 110, 255)     # Thinking arc


class FaceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.state = "idle"
        self.subtitle = ""

        self._phase = 0.0      # Breathing phase (0 → 2π)
        self._angle = 0.0      # Rotation for thinking arcs
        self._pulse = 0.0      # 0.0 → 1.0 computed from phase

        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)  # ~60fps

    def set_state(self, state: str, text: str = ""):
        self.state = state
        self.subtitle = text

    def _tick(self):
        speed = {"idle": 0.018, "listening": 0.03, "thinking": 0.025, "speaking": 0.05}
        self._phase = (self._phase + speed.get(self.state, 0.02)) % (2 * math.pi)
        self._pulse = (math.sin(self._phase) + 1) / 2   # smooth 0→1
        self._angle = (self._angle + 1.8) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2

        # ── Background (rounded rect) ─────────────────────────────────────────
        p.setPen(Qt.NoPen)
        p.setBrush(BG)
        p.drawRoundedRect(0, 0, w, h, 20, 20)

        # ── Orb size & glow intensity per state ───────────────────────────────
        orb_r   = 64 + int(self._pulse * 6)
        g_boost = {"idle": 0.25, "listening": 0.5, "thinking": 0.4, "speaking": 0.65}
        glow_i  = g_boost.get(self.state, 0.3) + self._pulse * 0.2

        # ── Glow layers ───────────────────────────────────────────────────────
        for i in range(7, 0, -1):
            r     = orb_r + i * 14
            alpha = max(0, int(glow_i * (55 - i * 6)))
            p.setBrush(QColor(GLOW.red(), GLOW.green(), GLOW.blue(), alpha))
            p.drawEllipse(cx - r, cy - r, r * 2, r * 2)

        # ── Orb body ──────────────────────────────────────────────────────────
        p.setBrush(ORB_MID)
        p.drawEllipse(cx - orb_r, cy - orb_r, orb_r * 2, orb_r * 2)

        # ── Inner highlight (top-left) ────────────────────────────────────────
        hl_r = orb_r // 3
        p.setBrush(HIGHLIGHT)
        p.drawEllipse(cx - hl_r - 14, cy - hl_r - 18, hl_r * 2, hl_r * 2)

        # ── Listening ring ────────────────────────────────────────────────────
        if self.state == "listening":
            ring_r = orb_r + 22 + int(self._pulse * 8)
            p.setPen(QPen(QColor(ARC_COLOR.red(), ARC_COLOR.green(), ARC_COLOR.blue(), 160), 1))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2)

        # ── Thinking arcs ─────────────────────────────────────────────────────
        if self.state == "thinking":
            arc_r = orb_r + 26
            rect  = QRect(cx - arc_r, cy - arc_r, arc_r * 2, arc_r * 2)
            p.setPen(QPen(ARC_COLOR, 2, Qt.SolidLine, Qt.RoundCap))
            p.setBrush(Qt.NoBrush)
            p.drawArc(rect, int(self._angle * 16),       100 * 16)
            p.drawArc(rect, int((self._angle + 180) * 16), 100 * 16)

        # ── Speaking pulse ring ───────────────────────────────────────────────
        if self.state == "speaking":
            ring_r = orb_r + 18 + int(self._pulse * 18)
            alpha  = int((1 - self._pulse) * 180)
            p.setPen(QPen(QColor(GLOW.red(), GLOW.green(), GLOW.blue(), alpha), 1.5))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(cx - ring_r, cy - ring_r, ring_r * 2, ring_r * 2)

        # ── VOX label ─────────────────────────────────────────────────────────
        p.setPen(TEXT_BRIGHT)
        f = QFont("Consolas", 14, QFont.Bold)
        p.setFont(f)
        p.drawText(0, cy - orb_r - 52, w, 26, Qt.AlignCenter, "VOX")

        # Thin divider
        div_y = cy - orb_r - 28
        p.setPen(QPen(QColor(100, 60, 160, 80), 1))
        p.drawLine(cx - 28, div_y, cx + 28, div_y)

        # ── State label ───────────────────────────────────────────────────────
        p.setPen(TEXT_DIM)
        f2 = QFont("Consolas", 8)
        p.setFont(f2)
        p.drawText(0, cy + orb_r + 14, w, 18, Qt.AlignCenter, self.state.upper())

        # ── Subtitle (last spoken text) ───────────────────────────────────────
        if self.subtitle:
            p.setPen(QColor(160, 130, 210, 190))
            f3 = QFont("Consolas", 9)
            p.setFont(f3)
            p.drawText(24, cy + orb_r + 36, w - 48, 56,
                       Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap,
                       self.subtitle)

        p.end()


class VoxWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VOX")
        self.setFixedSize(360, 420)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool                     # No taskbar entry
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.face = FaceWidget()
        self.setCentralWidget(self.face)
        self._drag_pos: QPoint | None = None

    def set_state(self, state: str, text: str = ""):
        self.face.set_state(state, text)

    # ── Drag to move ──────────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()
