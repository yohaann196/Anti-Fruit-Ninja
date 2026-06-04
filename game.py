import pygame, sys, os, random, math, json, array

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

WIDTH, HEIGHT = 600, 800
FPS = 60
GRAVITY = 1200
BASE_SPAWN_PROB = 0.04
MAX_ACTIVE = 5
SAVE_FILE = os.path.join(os.path.expanduser("~"), ".anti_fruit_ninja_save.json")


# --- Native sound generation (no external files needed) ---
def _generate_sound(frequency, duration, volume=0.3, wave_type="sine", fade_out=True):
    """Generate a pygame Sound from a waveform programmatically."""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array('h')  # signed short
    max_amp = int(32767 * volume)
    for i in range(n_samples):
        t = i / sample_rate
        if wave_type == "sine":
            val = math.sin(2 * math.pi * frequency * t)
        elif wave_type == "square":
            val = 1.0 if math.sin(2 * math.pi * frequency * t) >= 0 else -1.0
        elif wave_type == "noise":
            val = random.uniform(-1, 1)
        else:
            val = math.sin(2 * math.pi * frequency * t)
        if fade_out:
            val *= max(0, 1 - i / n_samples)
        sample = int(val * max_amp)
        buf.append(sample)
    sound = pygame.mixer.Sound(buffer=buf)
    return sound


def _generate_slice_sound():
    """Quick harsh slash sound."""
    sample_rate = 44100
    duration = 0.15
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n_samples):
        t = i / sample_rate
        env = max(0, 1 - i / n_samples)
        freq = 800 - 600 * (i / n_samples)
        val = math.sin(2 * math.pi * freq * t) * 0.4 + random.uniform(-0.3, 0.3)
        buf.append(int(val * env * 20000))
    return pygame.mixer.Sound(buffer=buf)


def _generate_splat_sound():
    """Wet splat/impact sound."""
    sample_rate = 44100
    duration = 0.25
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n_samples):
        t = i / sample_rate
        env = max(0, 1 - (i / n_samples) ** 0.5)
        val = random.uniform(-1, 1) * env * 0.3
        val += math.sin(2 * math.pi * 120 * t) * env * 0.4
        buf.append(int(val * 22000))
    return pygame.mixer.Sound(buffer=buf)


def _generate_mercy_sound():
    """Gentle ascending chime for mercy."""
    sample_rate = 44100
    duration = 0.4
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n_samples):
        t = i / sample_rate
        freq = 600 + 400 * (i / n_samples)
        env = max(0, 1 - (i / n_samples) ** 2)
        val = math.sin(2 * math.pi * freq * t) * 0.3
        val += math.sin(2 * math.pi * freq * 1.5 * t) * 0.15
        buf.append(int(val * env * 25000))
    return pygame.mixer.Sound(buffer=buf)


def _generate_combo_sound():
    """Aggressive escalating tone for combos."""
    sample_rate = 44100
    duration = 0.3
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n_samples):
        t = i / sample_rate
        freq = 300 + 500 * (i / n_samples)
        env = max(0, 1 - i / n_samples)
        val = (math.sin(2 * math.pi * freq * t) * 0.4 +
               math.sin(2 * math.pi * freq * 2 * t) * 0.2)
        buf.append(int(val * env * 24000))
    return pygame.mixer.Sound(buffer=buf)


def _generate_lawsuit_sound():
    """Alarming buzzer for lawyer hits."""
    sample_rate = 44100
    duration = 0.5
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n_samples):
        t = i / sample_rate
        env = max(0, 1 - i / n_samples)
        val = (math.sin(2 * math.pi * 200 * t) * 0.3 +
               math.sin(2 * math.pi * 253 * t) * 0.3)
        buf.append(int(val * env * 22000))
    return pygame.mixer.Sound(buffer=buf)


def _generate_angel_sound():
    """Ethereal angelic chord."""
    sample_rate = 44100
    duration = 0.6
    n_samples = int(sample_rate * duration)
    buf = array.array('h')
    for i in range(n_samples):
        t = i / sample_rate
        env = math.sin(math.pi * i / n_samples)
        val = (math.sin(2 * math.pi * 523 * t) * 0.2 +
               math.sin(2 * math.pi * 659 * t) * 0.2 +
               math.sin(2 * math.pi * 784 * t) * 0.15)
        buf.append(int(val * env * 22000))
    return pygame.mixer.Sound(buffer=buf)


# Pre-generate all sounds
SFX_SLICE = _generate_slice_sound()
SFX_SPLAT = _generate_splat_sound()
SFX_MERCY = _generate_mercy_sound()
SFX_COMBO = _generate_combo_sound()
SFX_LAWSUIT = _generate_lawsuit_sound()
SFX_ANGEL = _generate_angel_sound()

BG_WAYPOINTS = [(0, (255, 255, 255)), (25, (255, 200, 200)), (75, (200, 80, 40)), (150, (40, 20, 20))]

LAST_WORDS = [
    "please! spare me", "i have a family!", "how can you be so cruel?",
    "the kids... the KIDS", "my children will never know their father",
    "i was going to propose tomorrow", "i just wanted to live",
    "why? WHY?!", "i forgive you... but they won't",
    "tell my wife i love her", "i'm begging you... please stop",
    "we were supposed to grow old together", "...mother? is that you?",
    "i never got to say goodbye", "they'll find out what you did",
]

ROSTER = [
    ("Brenda", "watermelon", "please... i have children at home", 2),
    ("Greg", "apple", "my kids are watching you murder me", 2),
    ("Linda", "pear", "i'm BEGGING you. please don't.", 1),
    ("Doug", "banana", "i just want to see my daughter grow up", 1),
    ("Pamela", "peach", "why would you do this to me?", 2),
    ("Steve", "plum", "i was finally getting my life together...", 3),
    ("Reginald", "kiwi", "my son will grow up without a father", 2),
    ("Margaret", "grapes", "we're a family! you're tearing us apart!", 5),
]

FRUIT_COLORS = {
    "watermelon": (34, 139, 34),
    "apple": (200, 0, 0),
    "pear": (180, 200, 50),
    "banana": (255, 220, 0),
    "peach": (255, 180, 130),
    "plum": (100, 0, 120),
    "kiwi": (120, 80, 40),
    "grapes": (100, 0, 150),
    "strawberry": (200, 30, 30),
    "god": (255, 235, 100),
}

FRUIT_DESCRIPTIONS = {
    "watermelon": "+2 sins - an innocent mother",
    "apple": "+2 sins - had kids watching",
    "pear": "+1 sin - just wanted to talk",
    "banana": "+1 sin - wanted to see his daughter grow",
    "peach": "+2 sins - didn't deserve this",
    "plum": "+3 sins - was turning his life around",
    "kiwi": "+2 sins - a father figure",
    "grapes": "+5 sins - an entire family",
    "god": "GOD - grants you a peaceful death",
    "angel": "-20 sins - redemption... wasted",
    "strawberry": "LAWSUIT - you'll hear from their attorney",
    "documentarian": "DOCUMENTED - footage at 11",
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("anti fruit ninja")
clock = pygame.time.Clock()

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_FONT_REGULAR = os.path.join(_BASE_DIR, 'fonts', 'ComicNeue-Regular.ttf')
_FONT_BOLD = os.path.join(_BASE_DIR, 'fonts', 'ComicNeue-Bold.ttf')
_FONT_ITALIC = os.path.join(_BASE_DIR, 'fonts', 'ComicNeue-Italic.ttf')
_FONT_BOLD_ITALIC = os.path.join(_BASE_DIR, 'fonts', 'ComicNeue-BoldItalic.ttf')

font16 = pygame.font.Font(_FONT_REGULAR, 16)
font22 = pygame.font.Font(_FONT_BOLD, 22)
font28 = pygame.font.Font(_FONT_REGULAR, 28)
font40 = pygame.font.Font(_FONT_BOLD, 40)
font60 = pygame.font.Font(_FONT_BOLD_ITALIC, 60)


# --- Persistent save ---
def load_save():
    try:
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"lifetime_sins": 0, "sessions": 0}


def save_game(sins_earned):
    data = load_save()
    data["lifetime_sins"] = data.get("lifetime_sins", 0) + sins_earned
    data["sessions"] = data.get("sessions", 0) + 1
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)


# --- Drawing helpers ---
def draw_watermelon(surf, x, y):
    pygame.draw.ellipse(surf, (34, 139, 34), (x + 5, y + 10, 50, 40))
    pygame.draw.line(surf, (0, 80, 0), (x + 15, y + 15), (x + 45, y + 45), 2)


def draw_apple(surf, x, y):
    pygame.draw.circle(surf, (200, 0, 0), (x + 30, y + 32), 22)
    pygame.draw.line(surf, (80, 40, 0), (x + 30, y + 10), (x + 30, y + 5), 3)


def draw_pear(surf, x, y):
    pygame.draw.ellipse(surf, (180, 200, 50), (x + 15, y + 25, 30, 30))
    pygame.draw.ellipse(surf, (180, 200, 50), (x + 20, y + 10, 20, 25))


def draw_banana(surf, x, y):
    pygame.draw.arc(surf, (255, 220, 0), (x + 10, y + 10, 40, 40), 0.5, 2.5, 8)


def draw_peach(surf, x, y):
    pygame.draw.circle(surf, (255, 180, 130), (x + 30, y + 32), 22)
    pygame.draw.circle(surf, (255, 150, 100), (x + 28, y + 30), 10)


def draw_plum(surf, x, y):
    pygame.draw.circle(surf, (100, 0, 120), (x + 30, y + 32), 20)


def draw_kiwi(surf, x, y):
    pygame.draw.ellipse(surf, (120, 80, 40), (x + 10, y + 15, 40, 30))


def draw_grapes(surf, x, y):
    for pos in [(25, 25), (35, 25), (20, 35), (30, 35), (40, 35)]:
        pygame.draw.circle(surf, (100, 0, 150), (x + pos[0], y + pos[1]), 8)


DRAW_FNS = {
    "watermelon": draw_watermelon, "apple": draw_apple, "pear": draw_pear,
    "banana": draw_banana, "peach": draw_peach, "plum": draw_plum,
    "kiwi": draw_kiwi, "grapes": draw_grapes,
}


def lerp_color(sins_val):
    for i in range(len(BG_WAYPOINTS) - 1):
        s0, c0 = BG_WAYPOINTS[i]
        s1, c1 = BG_WAYPOINTS[i + 1]
        if sins_val <= s1:
            t = (sins_val - s0) / max(1, s1 - s0)
            return tuple(int(c0[j] + (c1[j] - c0[j]) * t) for j in range(3))
    return BG_WAYPOINTS[-1][1]


def luminance(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def text_color(bg):
    return (255, 255, 255) if luminance(bg) < 128 else (0, 0, 0)


_vignette_cache = {}


def draw_vignette(surface, intensity):
    """Draw a subtle vignette overlay that darkens edges based on sin intensity."""
    if intensity <= 0:
        return
    alpha = min(int(intensity * 1.5), 180)
    # Quantize to buckets of 10 so the cache caps at ~18 entries instead of ~180.
    alpha = ((alpha + 5) // 10) * 10
    if alpha == 0:
        return
    if alpha not in _vignette_cache:
        vig = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(40):
            a = int(alpha * (1 - i / 40.0))
            pygame.draw.rect(vig, (0, 0, 0, a), (i, i, WIDTH - 2 * i, HEIGHT - 2 * i), 3)
        _vignette_cache[alpha] = vig
    surface.blit(_vignette_cache[alpha], (0, 0))


# --- Particle system ---
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(100, 400)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 200
        self.life = random.uniform(0.4, 1.0)
        self.size = random.randint(3, 8)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += GRAVITY * 0.6 * dt
        self.life -= dt

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = max(0, min(255, int(255 * self.life)))
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


# --- Trail system ---
class Trail:
    def __init__(self):
        self.points = []
        self.max_points = 20

    def add_point(self, pos):
        self.points.append({"pos": pos, "life": 0.3})
        if len(self.points) > self.max_points:
            self.points.pop(0)

    def update(self, dt):
        for p in self.points:
            p["life"] -= dt
        self.points = [p for p in self.points if p["life"] > 0]

    def draw(self, surface, sins_val):
        if len(self.points) < 2:
            return
        for i in range(1, len(self.points)):
            alpha = max(0, min(255, int(255 * self.points[i]["life"] / 0.3)))
            r = min(255, 100 + int(sins_val * 1.5))
            g = max(0, 200 - int(sins_val * 2))
            b = max(0, 255 - int(sins_val * 2))
            color = (r, g, b)
            width = max(1, int(3 * self.points[i]["life"] / 0.3))
            start = self.points[i - 1]["pos"]
            end = self.points[i]["pos"]
            pygame.draw.line(surface, color, start, end, width)


# --- Screen shake ---
class ScreenShake:
    def __init__(self):
        self.duration = 0
        self.intensity = 0

    def trigger(self, intensity=5, duration=0.2):
        self.intensity = intensity
        self.duration = duration

    def update(self, dt):
        if self.duration > 0:
            self.duration -= dt

    def get_offset(self):
        if self.duration > 0:
            return (random.randint(-int(self.intensity), int(self.intensity)),
                    random.randint(-int(self.intensity), int(self.intensity)))
        return (0, 0)


# --- Game helper functions ---
def spawn_fruit_fn(g):
    if len(g.fruits) >= MAX_ACTIVE:
        return
    if g.mercy >= 10 and not g.angel_spawned:
        g.angel_spawned = True
        g.fruits.append(make_angel(g))
        return
    r = random.random()
    lawyer_chance = 1 / 300 if not g.documented else 1 / 100
    if r < 1 / 300:
        g.fruits.append(make_god(g))
    elif r < 1 / 300 + lawyer_chance:
        g.fruits.append(make_lawyer(g))
    elif r < 1 / 300 + lawyer_chance + 1 / 400:
        g.fruits.append(make_documentarian(g))
    else:
        info = random.choice(ROSTER)
        g.fruits.append(make_normal(g, info))


def make_normal(g, info):
    speed_mult = g.get_fruit_speed_mult()
    extra_plea = None
    if g.documented and g.sliced_names and random.random() < 0.3:
        ref = random.choice(g.sliced_names)
        extra_plea = f"you killed my friend {ref}"
    return {
        "name": info[0], "kind": info[1], "plea": info[2], "sin_val": info[3],
        "x": random.randint(80, WIDTH - 140), "y": HEIGHT,
        "vx": random.randint(-150, 150), "vy": int(random.randint(-1000, -850) * speed_mult),
        "hit": False, "special": None, "speaks": random.random() < 0.25,
        "extra_plea": extra_plea,
    }


def make_god(g):
    return {
        "name": "GOD", "kind": "god", "plea": "i have granted you a peaceful death.",
        "sin_val": 0, "x": random.randint(120, WIDTH - 180), "y": HEIGHT,
        "vx": random.randint(-40, 40), "vy": random.randint(-700, -600),
        "hit": False, "special": "god", "speaks": True, "extra_plea": None,
    }


def make_angel(g):
    return {
        "name": "Angel", "kind": "angel", "plea": "", "sin_val": -20,
        "x": random.randint(80, WIDTH - 140), "y": HEIGHT,
        "vx": random.randint(-100, 100), "vy": random.randint(-900, -800),
        "hit": False, "special": "angel", "speaks": False, "extra_plea": None,
    }


def make_lawyer(g):
    return {
        "name": "Lawyer", "kind": "strawberry", "plea": "", "sin_val": 0,
        "x": random.randint(80, WIDTH - 140), "y": HEIGHT,
        "vx": random.randint(-150, 150), "vy": random.randint(-1000, -850),
        "hit": False, "special": "lawyer", "speaks": False, "extra_plea": None,
    }


def make_documentarian(g):
    info = random.choice(ROSTER)
    return {
        "name": "Documentarian", "kind": info[1], "plea": "", "sin_val": 0,
        "x": random.randint(80, WIDTH - 140), "y": HEIGHT,
        "vx": random.randint(-150, 150), "vy": random.randint(-1000, -850),
        "hit": False, "special": "documentarian", "speaks": False, "extra_plea": None,
    }


def draw_god_fn(surf, x, y):
    t = pygame.time.get_ticks() / 100.0
    cx, cy = x + 30, y + 40
    # Rainbow glow halo
    glow_surf = pygame.Surface((180, 180), pygame.SRCALPHA)
    for r in range(85, 40, -5):
        hue = (t + r) % 360
        color = pygame.Color(0)
        color.hsva = (hue, 100, 100, 100)
        pygame.draw.circle(glow_surf, (color.r, color.g, color.b, 25), (90, 90), r)
    surf.blit(glow_surf, (cx - 90, cy - 90))
    # Wings (large, white, feathered)
    pygame.draw.ellipse(surf, (255, 255, 255), (x - 40, y + 10, 50, 70))
    pygame.draw.ellipse(surf, (255, 255, 255), (x + 50, y + 10, 50, 70))
    pygame.draw.ellipse(surf, (220, 220, 255), (x - 32, y + 18, 36, 54))
    pygame.draw.ellipse(surf, (220, 220, 255), (x + 56, y + 18, 36, 54))
    # Staff (golden, vertical, curled top)
    staff_x = x + 78
    pygame.draw.line(surf, (218, 165, 32), (staff_x, y + 10), (staff_x, y + 90), 4)
    pygame.draw.arc(surf, (218, 165, 32), (staff_x - 12, y - 4, 18, 24), 0, math.pi, 4)
    # Body (large bright circle, rainbow border)
    pygame.draw.circle(surf, (255, 255, 255), (cx, cy), 38)
    border_hue = (t * 2) % 360
    border_color = pygame.Color(0)
    border_color.hsva = (border_hue, 100, 100, 100)
    pygame.draw.circle(surf, (border_color.r, border_color.g, border_color.b), (cx, cy), 38, 3)
    # Halo (golden ring above)
    pygame.draw.ellipse(surf, (255, 215, 0), (cx - 28, y - 6, 56, 18), 4)
    pygame.draw.ellipse(surf, (255, 235, 100), (cx - 24, y - 2, 48, 12), 2)
    # Serene face
    pygame.draw.line(surf, (60, 60, 60), (cx - 10, cy - 4), (cx - 4, cy - 4), 2)
    pygame.draw.line(surf, (60, 60, 60), (cx + 4, cy - 4), (cx + 10, cy - 4), 2)
    pygame.draw.arc(surf, (60, 60, 60), (cx - 8, cy, 16, 10), math.pi, 2 * math.pi, 2)


def draw_fruit_fn(surf, f):
    x, y = int(f["x"]), int(f["y"])
    if f["special"] == "god":
        draw_god_fn(surf, x, y)
    elif f["special"] == "angel":
        # Yellow glow
        glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        for r in range(35, 10, -3):
            alpha = max(10, 80 - r * 2)
            pygame.draw.circle(glow_surf, (255, 255, 100, alpha), (40, 40), r)
        surf.blit(glow_surf, (x - 10, y - 5))
        # Wings
        pygame.draw.ellipse(surf, (255, 255, 200), (x - 8, y + 15, 22, 30))
        pygame.draw.ellipse(surf, (255, 255, 200), (x + 46, y + 15, 22, 30))
        pygame.draw.ellipse(surf, (255, 255, 240), (x - 3, y + 20, 16, 22))
        pygame.draw.ellipse(surf, (255, 255, 240), (x + 48, y + 20, 16, 22))
        # Body with contrasting outline
        pygame.draw.circle(surf, (50, 50, 50), (x + 30, y + 32), 24, 3)
        pygame.draw.circle(surf, (255, 255, 255), (x + 30, y + 32), 22)
        # Halo above head
        pygame.draw.ellipse(surf, (255, 220, 0), (x + 12, y - 2, 36, 12), 3)
        pygame.draw.ellipse(surf, (255, 200, 0), (x + 14, y, 32, 8), 2)
    elif f["special"] == "lawyer":
        pygame.draw.circle(surf, (200, 30, 30), (x + 30, y + 28), 20)
        pygame.draw.polygon(surf, (200, 30, 30), [(x + 20, y + 28), (x + 40, y + 28), (x + 35, y + 50), (x + 25, y + 50)])
        pygame.draw.rect(surf, (0, 0, 0), (x + 38, y + 40, 10, 8))
    else:
        fn = DRAW_FNS.get(f["kind"])
        if fn:
            fn(surf, x, y)
    if f["special"] == "documentarian":
        pygame.draw.rect(surf, (0, 0, 0), (x + 20, y - 5, 20, 12))


def draw_witnesses_fn(surf, bg, g):
    for i, w in enumerate(g.witnesses):
        wx = 10 + i * 25
        wy = HEIGHT - 20
        pygame.draw.ellipse(surf, (60, 60, 60), (wx, wy, 20, 15))
        if g.sins >= 50:
            pygame.draw.circle(surf, (255, 255, 255), (wx + 13, wy + 7), 3)
        if g.bloodlust_ending:
            if i < len(g.witnesses) - 1:
                pygame.draw.line(surf, (60, 60, 60), (wx + 20, wy + 7), (wx + 25, wy + 7), 2)


# --- Game State ---
class GameState:
    def __init__(self):
        self.reset()
        self.save_data = load_save()
        self.state = "title"  # title, playing, paused, ending

    def reset(self):
        self.sins = 0
        self.mercy = 0
        self.fruits = []
        self.floaters = []
        self.lawsuits = []
        self.particles = []
        self.ticker_text = ""
        self.ticker_timer = 0
        self.witnesses = []
        self.halted = False
        self.letter_timer = 0
        self.letter_shown = False
        self.angel_spawned = False
        self.trail = Trail()
        self.shake = ScreenShake()
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_label_timer = 0
        self.sliced_names = []
        self.documented = False
        self.time_since_slice = 0.0
        self.consecutive_slices = 0
        self.extinction_ending = False
        self.forgiveness_ending = False
        self.peaceful_ending = False
        self.redemption_ending = False
        self.bloodlust_ending = False
        self.ending_type = None
        self.sin_shake_timer = 0
        self.mercy_flash_timer = 0
        self.session_sins = 0
        self.graves = []
        self.captions = []

    def get_spawn_prob(self):
        """Difficulty curve: spawn rate increases with sins."""
        base = BASE_SPAWN_PROB + self.sins * 0.0003
        if self.sins >= 100 and not self.letter_shown:
            base *= 0.6
        return base

    def get_fruit_speed_mult(self):
        """Fruits get faster as sins rise."""
        return 1.0 + self.sins * 0.003


# --- Main game loop ---
game = GameState()
trail_frame_counter = 0

while True:
    raw_dt = clock.tick(FPS) / 1000.0
    dt = min(raw_dt, 0.05)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if game.session_sins > 0:
                save_game(game.session_sins)
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game.state == "playing":
                    game.state = "paused"
                elif game.state == "paused":
                    game.state = "playing"
            if event.key == pygame.K_r and game.state == "ending":
                game.save_data = load_save()
                game.reset()
                game.state = "playing"
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if game.state == "title":
                    game.state = "playing"

    # --- Title screen ---
    if game.state == "title":
        screen.fill((255, 255, 255))
        title_r = font60.render("anti fruit ninja", True, (200, 0, 0))
        screen.blit(title_r, (WIDTH // 2 - title_r.get_width() // 2, HEIGHT // 3 - 40))

        sub_r = font22.render("they have names. they have families.", True, (80, 80, 80))
        screen.blit(sub_r, (WIDTH // 2 - sub_r.get_width() // 2, HEIGHT // 3 + 40))

        # Nervous fruit
        t = pygame.time.get_ticks() / 500.0
        wobble = int(math.sin(t) * 5)
        fx, fy = WIDTH // 2 - 30, HEIGHT // 2 + 20 + wobble
        draw_watermelon(screen, fx, fy)
        eye_r = font16.render("o_o", True, (0, 0, 0))
        screen.blit(eye_r, (fx + 18, fy + 20))

        start_r = font28.render("press ENTER to begin", True, (0, 0, 0))
        if int(t * 2) % 2 == 0:
            screen.blit(start_r, (WIDTH // 2 - start_r.get_width() // 2, HEIGHT * 3 // 4))

        # Persistent guilt
        if game.save_data.get("lifetime_sins", 0) > 0:
            guilt_r = font16.render(
                f"welcome back. {game.save_data['lifetime_sins']} lifetime sins.",
                True, (150, 0, 0))
            screen.blit(guilt_r, (WIDTH // 2 - guilt_r.get_width() // 2, HEIGHT - 60))

        pygame.display.update()
        continue

    # --- Pause screen ---
    if game.state == "paused":
        screen.fill((240, 240, 240))
        pause_r = font40.render("PAUSED", True, (0, 0, 0))
        screen.blit(pause_r, (WIDTH // 2 - pause_r.get_width() // 2, HEIGHT // 3))
        msg_r = font22.render("the fruits are still alive while you're away.", True, (80, 80, 80))
        screen.blit(msg_r, (WIDTH // 2 - msg_r.get_width() // 2, HEIGHT // 2))
        esc_r = font16.render("press ESC to resume", True, (120, 120, 120))
        screen.blit(esc_r, (WIDTH // 2 - esc_r.get_width() // 2, HEIGHT // 2 + 60))
        pygame.display.update()
        continue

    # --- Ending screen ---
    if game.state == "ending":
        bg = lerp_color(game.sins)
        tc = text_color(bg)
        screen.fill(bg)

        if game.ending_type == "peaceful":
            screen.fill((255, 250, 230))
            draw_god_fn(screen, WIDTH // 2 - 30, HEIGHT // 3 - 40)
            lines = ["\"i have granted you", "a peaceful death.\""]
            for i, line in enumerate(lines):
                r = font40.render(line, True, (60, 40, 0))
                screen.blit(r, (WIDTH // 2 - r.get_width() // 2, HEIGHT // 2 + i * 50))
            label_r = font22.render("ENDING: PEACEFUL (divine ending)", True, (160, 100, 0))
            screen.blit(label_r, (WIDTH // 2 - label_r.get_width() // 2, 40))
            hint_r = font16.render("how: slice GOD — the 1-in-300 rainbow fruit with halo, wings, and staff", True, (80, 60, 0))
            screen.blit(hint_r, (WIDTH // 2 - hint_r.get_width() // 2, 70))

        elif game.ending_type == "redemption":
            screen.fill((230, 240, 255))
            lines = ["you paused.", "you saw what you had done.", "you stopped."]
            for i, line in enumerate(lines):
                r = font40.render(line, True, (30, 60, 120))
                screen.blit(r, (WIDTH // 2 - r.get_width() // 2, HEIGHT // 3 + i * 60))
            label_r = font22.render("ENDING: REDEMPTION (good ending)", True, (30, 60, 120))
            screen.blit(label_r, (WIDTH // 2 - label_r.get_width() // 2, 40))
            hint_r = font16.render("how: reach 100 sins, then pause for 5 seconds in remorse", True, (60, 90, 160))
            screen.blit(hint_r, (WIDTH // 2 - hint_r.get_width() // 2, 70))

        elif game.ending_type == "bloodlust":
            screen.fill((40, 0, 0))
            r = font40.render("you didn't stop.", True, (255, 50, 50))
            screen.blit(r, (WIDTH // 2 - r.get_width() // 2, HEIGHT // 2 - 40))
            r2 = font22.render(f"{game.consecutive_slices} in a row. unbroken.", True, (220, 80, 80))
            screen.blit(r2, (WIDTH // 2 - r2.get_width() // 2, HEIGHT // 2 + 20))
            label_r = font22.render("ENDING: BLOODLUST (bad ending)", True, (255, 100, 100))
            screen.blit(label_r, (WIDTH // 2 - label_r.get_width() // 2, 40))
            hint_r = font16.render("how: slice 50 fruits in a row at 100+ sins without missing", True, (220, 100, 100))
            screen.blit(hint_r, (WIDTH // 2 - hint_r.get_width() // 2, 70))

        elif game.ending_type == "extinction":
            screen.fill((20, 0, 0))
            crack_lines = [(100, 0, 300, 400), (500, 0, 200, 600), (0, 300, 400, 500),
                           (300, 0, 350, 800), (0, 600, 600, 400)]
            for cl in crack_lines:
                pygame.draw.line(screen, (80, 0, 0), (cl[0], cl[1]), (cl[2], cl[3]), 2)
            r = font40.render("they are all dead.", True, (255, 50, 50))
            screen.blit(r, (WIDTH // 2 - r.get_width() // 2, HEIGHT // 2 - 40))
            r2 = font22.render(f"sins: {game.sins}. no fruits remain.", True, (200, 0, 0))
            screen.blit(r2, (WIDTH // 2 - r2.get_width() // 2, HEIGHT // 2 + 20))
            label_r = font22.render("ENDING: EXTINCTION (worst ending)", True, (255, 100, 100))
            screen.blit(label_r, (WIDTH // 2 - label_r.get_width() // 2, 40))
            hint_r = font16.render("how: reach 300 sins — every fruit dies, the world ends", True, (200, 100, 100))
            screen.blit(hint_r, (WIDTH // 2 - hint_r.get_width() // 2, 70))

        elif game.ending_type == "forgiveness":
            screen.fill((220, 255, 220))
            r = font40.render("they forgive you.", True, (0, 100, 0))
            screen.blit(r, (WIDTH // 2 - r.get_width() // 2, HEIGHT // 3))
            for i, info in enumerate(ROSTER):
                fruit_x = 50 + i * 65
                fruit_y = HEIGHT // 2 + int(math.sin(pygame.time.get_ticks() / 300.0 + i) * 10)
                fn = DRAW_FNS.get(info[1])
                if fn:
                    fn(screen, fruit_x, fruit_y)
                wave_r = font16.render("~", True, (0, 100, 0))
                screen.blit(wave_r, (fruit_x + 25, fruit_y - 15))
            label_r = font22.render("ENDING: FORGIVENESS (best ending)", True, (0, 80, 0))
            screen.blit(label_r, (WIDTH // 2 - label_r.get_width() // 2, 40))
            hint_r = font16.render("how: reach 50 mercy by letting fruits pass without slicing", True, (0, 80, 0))
            screen.blit(hint_r, (WIDTH // 2 - hint_r.get_width() // 2, 70))

        # Restart prompt
        end_tc = tc if game.ending_type not in ("peaceful", "forgiveness", "redemption") else (0, 0, 0)
        restart_r = font22.render("press R to restart", True, end_tc)
        screen.blit(restart_r, (WIDTH // 2 - restart_r.get_width() // 2, HEIGHT - 60))

        pygame.display.update()
        continue

    # --- Playing state ---
    bg = lerp_color(game.sins)
    tc = text_color(bg)

    # Letter interlude
    if game.letter_timer > 0:
        game.letter_timer -= dt
        screen.fill(bg)
        ticker_r = font22.render("BREAKING: 200 sins reached. letter delivered from brenda jr.", True, (255, 0, 0))
        screen.blit(ticker_r, (WIDTH // 2 - ticker_r.get_width() // 2, 5))
        letter = [
            "dear player,", "",
            "my mother brenda was a watermelon.",
            "she had hobbies.", "she had a husband.",
            "she had a podcast.", "",
            "regards,", "brenda jr.",
        ]
        for i, line in enumerate(letter):
            r = font22.render(line, True, tc)
            screen.blit(r, (WIDTH // 2 - r.get_width() // 2, 150 + i * 35))
        pygame.display.update()
        continue

    # Screen shake
    game.shake.update(dt)
    shake_offset = game.shake.get_offset()

    # Render surface for shake effect
    render_surf = pygame.Surface((WIDTH, HEIGHT))
    render_surf.fill(bg)

    mouse = pygame.mouse.get_pos()

    # Trail
    trail_frame_counter += 1
    if trail_frame_counter % 2 == 0:
        game.trail.add_point(mouse)
    game.trail.update(dt)

    # Combo timer
    if game.combo_timer > 0:
        game.combo_timer -= dt
        if game.combo_timer <= 0:
            game.combo_count = 0
    if game.combo_label_timer > 0:
        game.combo_label_timer -= dt

    # Score animation timers
    if game.sin_shake_timer > 0:
        game.sin_shake_timer -= dt
    if game.mercy_flash_timer > 0:
        game.mercy_flash_timer -= dt

    # Remorse timer: counts time since last slice (drives redemption ending after 100 sins)
    game.time_since_slice += dt

    # Spawn fruits (stop spawning at 300 sins so the extinction ending can trigger)
    if game.sins < 300 and random.random() < game.get_spawn_prob():
        spawn_fruit_fn(game)

    # Update fruits
    new_fruits = []
    for f in game.fruits:
        f["x"] += f["vx"] * dt
        f["y"] += f["vy"] * dt
        f["vy"] += GRAVITY * dt

        if f["y"] > HEIGHT + 60:
            if not f["hit"]:
                game.mercy += 1
                game.mercy_flash_timer = 0.3
                SFX_MERCY.play()
                if f["special"] == "angel":
                    game.mercy += 5
                    game.angel_spawned = False
                if game.sins >= 100:
                    game.consecutive_slices = 0
            continue

        if not f["hit"]:
            # Circle-based collision
            fx_center = f["x"] + 30
            fy_center = f["y"] + 30
            dist = math.sqrt((mouse[0] - fx_center) ** 2 + (mouse[1] - fy_center) ** 2)
            if dist < 30:
                f["hit"] = True
                game.time_since_slice = 0.0
                # Capture sins before any additions this frame so the 100-sin
                # ticker fires whether the crossing comes from combo or sin_val.
                prev_sins = game.sins
                # Sound effects
                SFX_SLICE.play()
                SFX_SPLAT.play()

                # Combo
                game.combo_count += 1
                game.combo_timer = 1.0
                if game.combo_count >= 3:
                    game.combo_label_timer = 1.5
                    combo_bonus = game.combo_count - 2
                    game.sins += combo_bonus
                    game.session_sins += combo_bonus
                    SFX_COMBO.play()

                # Particles
                color = FRUIT_COLORS.get(f["kind"], (200, 200, 200))
                for _ in range(random.randint(8, 15)):
                    game.particles.append(Particle(fx_center, fy_center, color))

                # Screen shake
                shake_intensity = 3 if f["kind"] != "grapes" else 8
                game.shake.trigger(shake_intensity, 0.15)

                if game.sins >= 100 and f["special"] != "god":
                    game.consecutive_slices += 1

                if f["special"] == "god":
                    game.ending_type = "peaceful"
                    game.peaceful_ending = True
                    game.state = "ending"
                    save_game(game.session_sins)
                elif f["special"] == "angel":
                    game.sins = max(0, game.sins + f["sin_val"])
                    game.mercy = 0
                    game.angel_spawned = False
                    game.floaters.append({"text": "redeemed (partially)", "x": f["x"], "y": f["y"], "t": 0})
                    SFX_ANGEL.play()
                elif f["special"] == "lawyer":
                    for _ in range(3):
                        game.lawsuits.append({"x": mouse[0], "y": mouse[1], "t": 0})
                    SFX_LAWSUIT.play()
                elif f["special"] == "documentarian":
                    game.documented = True
                    game.ticker_text = "BREAKING: Local Player Identified. Footage at 11."
                    game.ticker_timer = 6.0
                else:
                    game.sins += f["sin_val"]
                    game.session_sins += f["sin_val"]
                    game.sin_shake_timer = 0.3
                    if prev_sins < 100 <= game.sins:
                        game.ticker_text = "BREAKING: 100 sins. pause 5 sec for redemption — or slice 50 in a row for bloodlust."
                        game.ticker_timer = 6.0
                    if f["name"] and f["name"] not in game.sliced_names:
                        game.sliced_names.append(f["name"])
                    game.floaters.append({"text": random.choice(LAST_WORDS), "x": f["x"], "y": f["y"], "t": 0})
                    # Add a grave for this fruit (cap at 20)
                    grave_x = random.randint(30, WIDTH - 70)
                    game.graves.append({"x": grave_x, "name": f["name"], "kind": f["kind"]})
                    if len(game.graves) > 20:
                        game.graves.pop(0)
                    if game.sins >= 200 and not game.letter_shown:
                        game.letter_shown = True
                        game.letter_timer = 5.0

                # Show caption describing what the fruit does
                desc_kind = f["kind"] if f["special"] is None else (f["special"] if f["special"] in FRUIT_DESCRIPTIONS else f["kind"])
                caption_text = FRUIT_DESCRIPTIONS.get(desc_kind, "")
                if caption_text:
                    game.captions.append({"text": caption_text, "x": f["x"], "y": f["y"] + 50, "t": 0})

        new_fruits.append(f)
    game.fruits = new_fruits

    # Check endings
    if game.sins >= 300 and not game.extinction_ending:
        game.extinction_ending = True
        game.ending_type = "extinction"
        game.state = "ending"
        save_game(game.session_sins)
        pygame.display.update()
        continue

    if game.mercy >= 50 and not game.forgiveness_ending:
        game.forgiveness_ending = True
        game.ending_type = "forgiveness"
        game.state = "ending"
        save_game(game.session_sins)
        pygame.display.update()
        continue

    if game.sins >= 100 and not game.redemption_ending and not game.letter_shown:
        if game.time_since_slice >= 5.0:
            game.redemption_ending = True
            game.ending_type = "redemption"
            game.state = "ending"
            save_game(game.session_sins)
            pygame.display.update()
            continue

    if game.sins >= 100 and not game.bloodlust_ending:
        if game.consecutive_slices >= 50:
            game.bloodlust_ending = True
            game.ending_type = "bloodlust"
            game.state = "ending"
            save_game(game.session_sins)
            pygame.display.update()
            continue

    # Draw graves in background
    for i, grave in enumerate(game.graves):
        gx = grave["x"]
        gy = HEIGHT - 60
        # Tombstone
        pygame.draw.rect(render_surf, (100, 100, 100), (gx, gy - 25, 30, 35))
        pygame.draw.arc(render_surf, (100, 100, 100), (gx, gy - 40, 30, 30), 0, math.pi, 0)
        pygame.draw.ellipse(render_surf, (100, 100, 100), (gx, gy - 40, 30, 30))
        # Cross on tombstone
        pygame.draw.line(render_surf, (60, 60, 60), (gx + 15, gy - 30), (gx + 15, gy - 10), 2)
        pygame.draw.line(render_surf, (60, 60, 60), (gx + 9, gy - 22), (gx + 21, gy - 22), 2)
        # Name on grave
        if grave["name"]:
            name_r = font16.render(grave["name"], True, (200, 200, 200))
            render_surf.blit(name_r, (gx + 15 - name_r.get_width() // 2, gy - 8))
        # Ground mound
        pygame.draw.ellipse(render_surf, (80, 60, 40), (gx - 5, gy + 8, 40, 10))

    # Draw fruits
    for f in game.fruits:
        draw_fruit_fn(render_surf, f)
        x, y = int(f["x"]), int(f["y"])
        if not f["hit"] and f["name"] and f["special"] != "god":
            nr = font16.render(f["name"], True, tc)
            render_surf.blit(nr, (x + 30 - nr.get_width() // 2, y - 18))
        if not f["hit"] and f["speaks"]:
            plea_text = f.get("extra_plea") or f["plea"]
            pr = font22.render(plea_text, True, tc)
            render_surf.blit(pr, (x + 30 - pr.get_width() // 2, y - 40))

    # Draw particles
    new_particles = []
    for p in game.particles:
        p.update(dt)
        if p.life > 0:
            p.draw(render_surf)
            new_particles.append(p)
    game.particles = new_particles

    # Draw floaters
    new_floaters = []
    for fl in game.floaters:
        fl["t"] += dt
        if fl["t"] < 1.5:
            alpha = max(0, 255 - int(255 * fl["t"] / 1.5))
            s = font22.render(fl["text"], True, tc)
            s.set_alpha(alpha)
            render_surf.blit(s, (int(fl["x"]), int(fl["y"] - fl["t"] * 30)))
            new_floaters.append(fl)
    game.floaters = new_floaters

    # Draw captions (what each fruit does)
    new_captions = []
    for cap in game.captions:
        cap["t"] += dt
        if cap["t"] < 2.5:
            alpha = max(0, 255 - int(255 * cap["t"] / 2.5))
            s = font16.render(cap["text"], True, (255, 200, 0))
            s.set_alpha(alpha)
            render_surf.blit(s, (int(cap["x"] + 30 - s.get_width() // 2), int(cap["y"] - cap["t"] * 15)))
            new_captions.append(cap)
    game.captions = new_captions

    # Draw lawsuits
    new_lawsuits = []
    for ls in game.lawsuits:
        ls["t"] += dt
        if ls["t"] < 10:
            ls["x"] += (mouse[0] - ls["x"]) * 0.05
            ls["y"] += (mouse[1] - ls["y"]) * 0.05
            r = font16.render("LAWSUIT", True, (200, 0, 0))
            render_surf.blit(r, (int(ls["x"]), int(ls["y"])))
            new_lawsuits.append(ls)
    game.lawsuits = new_lawsuits

    # Draw ticker
    if game.ticker_timer > 0:
        game.ticker_timer -= dt
        tr = font22.render(game.ticker_text, True, (255, 0, 0))
        render_surf.blit(tr, (WIDTH // 2 - tr.get_width() // 2, 5))

    # Draw trail
    game.trail.draw(render_surf, game.sins)

    # HUD - sins with shake
    sin_offset_x = random.randint(-3, 3) if game.sin_shake_timer > 0 else 0
    sin_offset_y = random.randint(-3, 3) if game.sin_shake_timer > 0 else 0
    sin_r = font28.render(f"sins: {game.sins}", True, tc)
    render_surf.blit(sin_r, (10 + sin_offset_x, 10 + sin_offset_y))

    # Mercy counter with green flash
    mercy_color = (0, 180, 0) if game.mercy_flash_timer > 0 else tc
    mercy_r = font28.render(f"mercy: {game.mercy}/50", True, mercy_color)
    render_surf.blit(mercy_r, (WIDTH - mercy_r.get_width() - 10, 10))

    # Combo label
    if game.combo_label_timer > 0 and game.combo_count >= 3:
        combo_r = font40.render(f"RAMPAGE x{game.combo_count}!", True, (255, 50, 0))
        render_surf.blit(combo_r, (WIDTH // 2 - combo_r.get_width() // 2, HEIGHT // 2 - 100))

    # Witnesses
    while len(game.witnesses) < min(game.sins // 5, 20):
        game.witnesses.append({})
    draw_witnesses_fn(render_surf, bg, game)

    # Vignette
    draw_vignette(render_surf, game.sins)

    # Apply shake and display
    screen.blit(render_surf, shake_offset)
    pygame.display.update()
