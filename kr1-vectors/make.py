import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm, rcParams
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Polygon, Circle, FancyArrowPatch
import numpy as np, os, logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

HERE = os.path.dirname(os.path.abspath(__file__))
fm.fontManager.addfont(os.path.join(HERE, 'Pangolin.ttf'))
rcParams['mathtext.fontset'] = 'custom'
for k in ['rm', 'it', 'bf', 'sf']:
    rcParams['mathtext.' + k] = 'Pangolin'
rcParams['mathtext.fallback'] = 'stixsans'
rcParams['font.family'] = 'Pangolin'

W, H = 210, 297            # A4 portrait, mm
INK = '#1b3a9a'            # blue pen
RED = '#c62828'            # red pen (answers / highlights)
PEN = '#2b2b2b'            # pencil for drawings
GREEN = '#2e7d32'
GRID = '#9cc3e6'
FS = 13                    # base font size


def V(s):                  # vector with arrow
    return r'\overrightarrow{%s}' % s


class Page:
    def __init__(self, pdf, title=None):
        self.pdf = pdf
        self.fig = plt.figure(figsize=(W / 25.4, H / 25.4))
        ax = self.fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')
        ax.add_patch(plt.Rectangle((0, 0), W, H, color='#fdfdf8', zorder=-10))
        for x in np.arange(2, W, 5):
            ax.plot([x, x], [0, H], color=GRID, lw=0.35, zorder=-5)
        for y in np.arange(0, H, 5):
            ax.plot([0, W], [y, y], color=GRID, lw=0.35, zorder=-5)
        ax.plot([197, 197], [0, H], color='#e57373', lw=1.0, zorder=-4)   # margin
        self.ax = ax
        self.y = 20
        if title:
            ax.text(W / 2, 13, title, ha='center', va='baseline', fontsize=FS + 3,
                    color=INK, fontweight='bold')
            self.y = 23

    def w(self, s, x=10, size=FS, color=INK, step=7.5, **kw):
        self.ax.text(x, self.y, s, fontsize=size, color=color, va='baseline', **kw)
        self.y += step

    def head(self, s, x=10):
        self.ax.text(x, self.y, s, fontsize=FS + 1, color=INK, va='baseline', fontweight='bold')
        self.hy = self.y
        self.y += 7.5

    def answer(self, s, x=40):
        self.ax.text(x, self.hy, 'Ответ: ' + s, fontsize=FS + 1, color=RED, va='baseline',
                     bbox=dict(boxstyle='square,pad=0.3', fc='none', ec=RED, lw=1.0))

    def skip(self, d=5):
        self.y += d

    def inset(self, x, y, w, h, xlim, ylim):
        ax = self.fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])
        ax.set_xlim(*xlim); ax.set_ylim(*ylim)
        ax.set_aspect('equal', adjustable='datalim')
        ax.axis('off'); ax.patch.set_alpha(0)
        return ax

    def save(self):
        self.pdf.savefig(self.fig)
        plt.close(self.fig)


# ---------- drawing helpers ----------
def seg(ax, p, q, c=PEN, lw=1.4, ls='-', z=2):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=c, lw=lw, ls=ls, zorder=z, solid_capstyle='round')


def arrow(ax, p, q, c=INK, lw=2.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=12, color=c, lw=lw,
                                 shrinkA=0, shrinkB=0, zorder=4))


def lab(ax, p, s, dx=0, dy=0, c=PEN, size=FS):
    ax.text(p[0] + dx, p[1] + dy, s, fontsize=size, color=c, ha='center', va='center', zorder=6)


def dot(ax, p, c=PEN, r=None):
    ax.plot([p[0]], [p[1]], 'o', color=c, ms=3.5, zorder=5)


def right_angle(ax, foot, along, up, s=0.35, c=PEN):
    a = np.array(along, float); a /= np.linalg.norm(a)
    u = np.array(up, float); u /= np.linalg.norm(u)
    f = np.array(foot, float)
    pts = [f + a * s, f + a * s + u * s, f + u * s]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=c, lw=1.0, zorder=3)


def axes_xy(ax, xmin, xmax, ymin, ymax, ticks=True):
    arrow(ax, (xmin, 0), (xmax, 0), c=PEN, lw=1.2)
    arrow(ax, (0, ymin), (0, ymax), c=PEN, lw=1.2)
    lab(ax, (xmax, 0), '$x$', dx=-0.3, dy=-0.7)
    lab(ax, (0, ymax), '$y$', dx=-0.6, dy=-0.3)
    lab(ax, (0, 0), '0', dx=-0.45, dy=-0.55, size=FS - 3)


def coord_grid(ax, xmin, xmax, ymin, ymax):
    for x in range(int(np.floor(xmin)), int(np.ceil(xmax)) + 1):
        ax.plot([x, x], [ymin, ymax], color='#cfd8dc', lw=0.5, zorder=0)
    for y in range(int(np.floor(ymin)), int(np.ceil(ymax)) + 1):
        ax.plot([xmin, xmax], [y, y], color='#cfd8dc', lw=0.5, zorder=0)


# ======================= variant data =======================
VARS = {
    1: dict(
        t1=dict(start='M', a='K', b='N', res='P', ans='3'),
        t2=dict(fig='rect', items=[
            (V('AO') + '=' + V('CO'), False, r'$\uparrow\downarrow$'),
            (V('AC') + '=' + V('BD'), False, 'разные направления'),
            (r'|' + V('AC') + '|=|' + V('BD') + '|', True, 'диагонали равны'),
            (V('BA') + '=' + V('CD'), True, r'сонаправлены, $BA=CD$'),
            (V('AB') + '=' + V('CD'), False, r'$\uparrow\downarrow$'),
            (V('OD') + r'=0{,}5' + V('BD'), True, r'$O$ — середина $BD$, $\uparrow\uparrow$'),
        ], ans='3; 4; 6'),
        t3=dict(u='m', v='n', U=(-2, 1), Vv=(2, 4), k1=2, k2=3, r='a', ans='1'),
        t4=dict(b=(-5, 3), calc=r'\sqrt{(-5)^2+3^2}=\sqrt{25+9}=\sqrt{34}', ans=r'$\sqrt{34}$'),
        t5=dict(kind='len', P=('B', (2, -4)), Q=('C', (8, 4))),
        t6=dict(seg='MK', mid='C', e1='M', e2='K', v1=16, v2=6),
        t7=dict(R2=12, Rs=r'2\sqrt{3}', Rv=np.sqrt(12), side=+1, A='M', B='K', xb=-2,
                y2=8, ys=r'2\sqrt{2}', S=r'\frac{1}{2}\cdot 2\sqrt{3}\cdot 2\sqrt{2}=2\sqrt{6}',
                ans=r'$2\sqrt{6}$', half='положительную'),
    ),
    2: dict(
        t1=dict(start='N', a='M', b='P', res='K', ans='2'),
        t2=dict(fig='rhomb', items=[
            (V('AB') + '=' + V('AD'), False, 'разные направления'),
            (r'|' + V('AB') + '|=|' + V('AD') + '|', True, 'стороны равны'),
            (V('BO') + '=' + V('DO'), False, r'$\uparrow\downarrow$'),
            (V('CB') + '=' + V('AD'), False, r'$\overrightarrow{CB}\uparrow\downarrow\overrightarrow{AD}$'),
            (V('BC') + '=' + V('AD'), True, r'сонаправлены, $BC=AD$'),
            (V('CO') + r'=0{,}5' + V('CA'), True, r'$O$ — середина $CA$, $\uparrow\uparrow$'),
        ], ans='2; 5; 6'),
        t3=dict(u='n', v='h', U=(-4, 2), Vv=(1, 3), k1=2, k2=4, r='d', ans='4'),
        t4=dict(b=(2, -6), calc=r'\sqrt{2^2+(-6)^2}=\sqrt{4+36}=\sqrt{40}=2\sqrt{10}', ans=r'$2\sqrt{10}$'),
        t5=dict(kind='mid', P=('D', (-3, 7)), Q=('E', (5, 1))),
        t6=dict(seg='KN', mid='D', e1='K', e2='N', v1=14, v2=10),
        t7=dict(R2=36, Rs='6', Rv=6.0, side=-1, A='P', B='M', xb=3,
                y2=27, ys=r'3\sqrt{3}', S=r'\frac{1}{2}\cdot 6\cdot 3\sqrt{3}=9\sqrt{3}',
                ans=r'$9\sqrt{3}$', half='отрицательную'),
    ),
    3: dict(
        t1=dict(start='K', a='P', b='M', res='N', ans='1'),
        t2=dict(fig='rect', items=[
            (r'|' + V('CA') + '|=|' + V('BD') + '|', True, 'диагонали равны'),
            (V('CA') + '=' + V('BD'), False, 'разные направления'),
            (V('OA') + '=' + V('OC'), False, r'$\uparrow\downarrow$'),
            (V('OB') + r'=0{,}5' + V('DB'), True, r'$O$ — середина $DB$, $\uparrow\uparrow$'),
            (V('AB') + '=' + V('CD'), False, r'$\uparrow\downarrow$'),
            (V('AB') + '=' + V('DC'), True, r'сонаправлены, $AB=DC$'),
        ], ans='1; 4; 6'),
        t3=dict(u='n', v='k', U=(-3, 4), Vv=(1, 2), k1=3, k2=4, r='b', ans='2'),
        t4=dict(b=(-3, 2), calc=r'\sqrt{(-3)^2+2^2}=\sqrt{9+4}=\sqrt{13}', ans=r'$\sqrt{13}$'),
        t5=dict(kind='len', P=('T', (-1, -4)), Q=('H', (5, 4))),
        t6=dict(seg='PK', mid='B', e1='P', e2='K', v1=8, v2=16),
        t7=dict(R2=20, Rs=r'2\sqrt{5}', Rv=np.sqrt(20), side=-1, A='N', B='L', xb=2,
                y2=16, ys='4', S=r'\frac{1}{2}\cdot 2\sqrt{5}\cdot 4=4\sqrt{5}',
                ans=r'$4\sqrt{5}$', half='отрицательную'),
    ),
    4: dict(
        t1=dict(start='P', a='N', b='K', res='M', ans='4'),
        t2=dict(fig='rhomb', items=[
            (V('OB') + '=' + V('OD'), False, r'$\uparrow\downarrow$'),
            (V('BC') + '=' + V('DA'), False, r'$\overrightarrow{BC}\uparrow\downarrow\overrightarrow{DA}$'),
            (V('CB') + '=' + V('DA'), True, r'сонаправлены, $CB=DA$'),
            (V('BA') + '=' + V('BC'), False, 'разные направления'),
            (r'|' + V('BA') + '|=|' + V('BC') + '|', True, 'стороны равны'),
            (V('OA') + r'=0{,}5' + V('CA'), True, r'$O$ — середина $CA$, $\uparrow\uparrow$'),
        ], ans='3; 5; 6'),
        t3=dict(u='c', v='b', U=(-3, 4), Vv=(2, 3), k1=4, k2=2, r='m', ans='3'),
        t4=dict(b=(4, -2), calc=r'\sqrt{4^2+(-2)^2}=\sqrt{16+4}=\sqrt{20}=2\sqrt{5}', ans=r'$2\sqrt{5}$'),
        t5=dict(kind='mid', P=('K', (-5, 7)), Q=('M', (3, 1))),
        t6=dict(seg='MP', mid='T', e1='M', e2='P', v1=4, v2=14),
        t7=dict(R2=25, Rs='5', Rv=5.0, side=+1, A='K', B='P', xb=-3,
                y2=16, ys='4', S=r'\frac{1}{2}\cdot 5\cdot 4=10',
                ans='10', half='положительную'),
    ),
}
OPTS1 = {'1': 'KN', '2': 'NK', '3': 'MP', '4': 'PM'}


def num(v):
    return f'{v}' if v >= 0 else f'({v})'


def cv(t):  # {x; y}
    return r'\{%d;\,%d\}' % t


# ======================= blocks (tasks in order) =======================
FX, FW = 140, 54          # figure column
GAP = 5
BOTTOM = 290


class Flow:
    def __init__(self, pdf, n):
        self.pdf, self.n = pdf, n
        self.p = Page(pdf, f'Контрольная работа № 1.  Вариант {n}')

    def need(self, h):
        if self.p.y + h > BOTTOM:
            self.p.save()
            self.p = Page(self.pdf, f'Вариант {self.n} (продолжение)')
        return self.p

    def part(self, s):
        p = self.need(30)
        p.ax.text(W / 2, p.y, s, ha='center', fontsize=FS + 1, color=INK, va='baseline',
                  style='italic')
        p.y += 6.5

    def fig(self, y0, fh, xlim, ylim, fw=FW, fx=FX):
        return self.p.inset(fx, y0 - 4, fw, fh, xlim, ylim)

    def end(self, y0, fh):
        self.p.y = max(self.p.y, y0 - 4 + fh) + GAP


def b1(f, d):
    t = d['t1']; s = t['start']
    p = f.need(32); y0 = p.y
    p.head('Задача 1.')
    p.w(f'${V(s + t["a"])}+{V(s + t["b"])}={V(s + t["res"])}$  (правило параллелограмма)')
    p.answer(t['ans'])
    pts = {'K': (0, 0), 'M': (1.3, 2.6), 'N': (5.3, 2.6), 'P': (4, 0)}
    ax = f.fig(y0 - 2, 26, (-0.6, 5.9), (-0.6, 3.2))
    ax.add_patch(Polygon([pts[c] for c in 'KMNP'], closed=True, fill=False, ec=PEN, lw=1.1))
    S = pts[s]
    arrow(ax, S, pts[t['a']], c=INK, lw=1.6); arrow(ax, S, pts[t['b']], c=INK, lw=1.6)
    arrow(ax, S, pts[t['res']], c=RED, lw=1.6)
    off = {'K': (-0.3, -0.3), 'M': (-0.3, 0.3), 'N': (0.3, 0.3), 'P': (0.3, -0.3)}
    for c, q in pts.items():
        lab(ax, q, f'${c}$', *off[c])
    f.end(y0, 26)


def b2(f, d):
    t = d['t2']
    p = f.need(45); y0 = p.y
    p.head('Задача 2.')
    y = p.y
    for i, (eq, ok, why) in enumerate(t['items']):
        col, row = i // 3, i % 3
        x = 10 + col * 62; yy = y + row * 8
        p.ax.text(x, yy, f'{i + 1}) ${eq}$', fontsize=FS, color=INK, va='baseline')
        p.ax.text(x + 36, yy, 'верно' if ok else 'неверно', fontsize=FS - 1,
                  color=GREEN if ok else RED, va='baseline')
    p.y = y + 3 * 8
    p.answer(t['ans'])
    if t['fig'] == 'rect':
        P = {'A': (0, 0), 'B': (0, 2.6), 'C': (5, 2.6), 'D': (5, 0)}
        off = {'A': (-0.3, -0.3), 'B': (-0.3, 0.3), 'C': (0.3, 0.3), 'D': (0.3, -0.3)}
        ax = f.fig(y0 + 2, 28, (-0.6, 5.6), (-0.7, 3.2))
        right_angle(ax, P['A'], (1, 0), (0, 1), 0.3)
    else:
        P = {'A': (0, 0), 'B': (2.6, 1.5), 'C': (5.2, 0), 'D': (2.6, -1.5)}
        off = {'A': (-0.3, 0), 'B': (0, 0.35), 'C': (0.3, 0), 'D': (0, -0.4)}
        ax = f.fig(y0 + 2, 28, (-0.6, 5.8), (-2.1, 2.1))
    for a, b in [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')]:
        seg(ax, P[a], P[b], lw=1.1)
    seg(ax, P['A'], P['C'], lw=0.8); seg(ax, P['B'], P['D'], lw=0.8)
    O = ((P['A'][0] + P['C'][0]) / 2, (P['A'][1] + P['C'][1]) / 2)
    dot(ax, O)
    for c in 'ABCD':
        lab(ax, P[c], f'${c}$', *off[c])
    lab(ax, O, '$O$', 0.0 if t['fig'] == 'rect' else -0.3, -0.4)
    f.end(y0 + 2, 28)


def b3(f, d):
    t3 = d['t3']; u, v, U, Vv, k1, k2, r = t3['u'], t3['v'], t3['U'], t3['Vv'], t3['k1'], t3['k2'], t3['r']
    A = (k1 * U[0], k1 * U[1]); B = (k2 * Vv[0], k2 * Vv[1]); R = (A[0] - B[0], A[1] - B[1])
    p = f.need(30)
    p.head('Задача 3.')
    p.w(f'${k1}\\vec{{{u}}}\\,{cv(A)}$,   ${k2}\\vec{{{v}}}\\,{cv(B)}$')
    p.w(f'$\\vec{{{r}}}={k1}\\vec{{{u}}}-{k2}\\vec{{{v}}}=\\{{{A[0]}-{num(B[0])};\\,{A[1]}-{num(B[1])}\\}}={cv(R)}$')
    p.answer(t3['ans'])
    p.y += GAP


def b4(f, d):
    t4 = d['t4']
    p = f.need(24)
    p.head('Задача 4.')
    p.w(f'$|\\vec b|={t4["calc"]}$')
    p.answer(t4['ans'])
    p.y += GAP


def b5(f, d):
    t5 = d['t5']; (n1, P1), (n2, P2) = t5['P'], t5['Q']
    p = f.need(42); y0 = p.y
    p.head('Задача 5.')
    p.w(f'${n1}({P1[0]};\\,{P1[1]})$,  ${n2}({P2[0]};\\,{P2[1]})$')
    if t5['kind'] == 'len':
        dx, dy = P2[0] - P1[0], P2[1] - P1[1]; L = int(np.sqrt(dx * dx + dy * dy))
        p.w(f'${n1}{n2}=\\sqrt{{{dx}^2+{dy}^2}}=\\sqrt{{{dx*dx}+{dy*dy}}}=\\sqrt{{{dx*dx+dy*dy}}}={L}$')
        p.answer(f'{L}')
    else:
        mx, my = (P1[0] + P2[0]) // 2, (P1[1] + P2[1]) // 2
        p.w(f'$x=\\frac{{{P1[0]}+{P2[0]}}}{{2}}={mx}$,   $y=\\frac{{{P1[1]}+{P2[1]}}}{{2}}={my}$', step=8.5)
        p.answer(f'$({mx};\\,{my})$')
    xs = [P1[0], P2[0], 0]; ys = [P1[1], P2[1], 0]
    x0, x1 = min(xs) - 1.2, max(xs) + 1.5; y0d, y1 = min(ys) - 1.2, max(ys) + 1.5
    fh = 34
    ax = f.fig(y0, fh, (x0, x1), (y0d, y1))
    coord_grid(ax, x0 + 0.3, x1 - 0.3, y0d + 0.3, y1 - 0.3)
    axes_xy(ax, x0 + 0.3, x1, y0d + 0.3, y1)
    seg(ax, P1, P2, c=INK, lw=1.8)
    for nm, P in [(n1, P1), (n2, P2)]:
        dot(ax, P, c=INK)
        seg(ax, (P[0], 0), P, ls='--', lw=0.7); seg(ax, (0, P[1]), P, ls='--', lw=0.7)
        lab(ax, P, f'${nm}$', 0.7 if P[0] >= max(P1[0], P2[0]) else -0.7, 0.5, c=INK)
        lab(ax, (P[0], 0), f'{P[0]}', 0.0, 0.7 if P[1] < 0 else -0.7, size=FS - 4)
        lab(ax, (0, P[1]), f'{P[1]}', -0.8 if P[0] > 0 else 0.8, 0, size=FS - 4)
    if t5['kind'] == 'mid':
        F = ((P1[0] + P2[0]) / 2, (P1[1] + P2[1]) / 2)
        dot(ax, F, c=RED)
    f.end(y0, fh)


def b6(f, d):
    t = d['t6']; s, m, e1, e2, v1, v2 = t['seg'], t['mid'], t['e1'], t['e2'], t['v1'], t['v2']
    res_s = f'{(v1 + v2) / 2:g}'
    p = f.need(42); y0 = p.y
    p.head('Задача 6.')
    p.w(f'${e1}{e1}_1\\parallel {m}{m}_1\\parallel {e2}{e2}_1$ (все $\\perp a$) $\\Rightarrow$')
    p.w(f'${e1}{e1}_1{e2}_1{e2}$ — трапеция; ${m}_1$ — середина ${e1}_1{e2}_1$')
    p.w(f'(т. Фалеса) $\\Rightarrow$ ${m}{m}_1$ — средняя линия:')
    p.w(f'${m}{m}_1=\\frac{{{v1}+{v2}}}{{2}}={res_s}$', step=8.5)
    p.answer(res_s)
    big_left = v1 > v2
    h1, h2 = (3.0, 1.2) if big_left else (1.2, 3.0)
    X1, X2 = 0.5, 5.0
    A, B = (X1, h1), (X2, h2); A1, B1 = (X1, 0), (X2, 0)
    C = ((X1 + X2) / 2, (h1 + h2) / 2); C1 = (C[0], 0)
    ax = f.fig(y0, 36, (-0.3, 5.9), (-0.8, 3.6))
    seg(ax, (-0.2, 0), (5.8, 0), lw=1.1); lab(ax, (5.8, 0), '$a$', 0, 0.3)
    seg(ax, A, B, c=INK, lw=1.6)
    for P_, Q in [(A, A1), (B, B1), (C, C1)]:
        seg(ax, P_, Q, lw=1.0); right_angle(ax, Q, (1, 0), (0, 1), 0.2)
    for P_ in [A, B, C, A1, B1, C1]:
        dot(ax, P_)
    lab(ax, A, f'${e1}$', -0.3, 0.3); lab(ax, B, f'${e2}$', 0.3, 0.3); lab(ax, C, f'${m}$', 0.1, 0.4)
    lab(ax, A1, f'${e1}_1$', 0, -0.45); lab(ax, B1, f'${e2}_1$', 0, -0.45); lab(ax, C1, f'${m}_1$', 0, -0.45)
    lab(ax, (A[0], A[1] / 2), f'{v1}', -0.35, 0, c=RED, size=FS - 2)
    lab(ax, (B[0], B[1] / 2), f'{v2}', 0.35, 0, c=RED, size=FS - 2)
    f.end(y0, 36)


def b7(f, d):
    t = d['t7']; A, B, side = t['A'], t['B'], t['side']
    xa = t['Rs'] if side > 0 else '-' + t['Rs']
    p = f.need(45); y0 = p.y
    p.head('Задача 7*.')
    p.w(f'$R=\\sqrt{{{t["R2"]}}}={t["Rs"]}$,  ${A}({xa};\\,0)$,  $O{A}={t["Rs"]}$' if t['Rs'] not in ('5', '6')
        else f'$R={t["Rs"]}$,  ${A}({xa};\\,0)$,  $O{A}={t["Rs"]}$')
    p.w(f'${B}$: ${num(t["xb"])}^2+y^2={t["R2"]}$, $y^2={t["y2"]}$, ${B}H=|y|={t["ys"]}$')
    p.w(f'$S=\\frac{{1}}{{2}}\\cdot O{A}\\cdot {B}H={t["S"]}$', step=8.5)
    p.answer(t['ans'])
    R = t['Rv']; xb = t['xb']; yb = np.sqrt(t['y2']); L = R * 1.3
    fh = 40
    ax = f.fig(y0, fh, (-L, L), (-L, L))
    axes_xy(ax, -L, L, -L, L)
    ax.add_patch(Circle((0, 0), R, fill=False, ec=PEN, lw=1.1))
    Ap = (side * R, 0); Bp = (xb, yb); Hp = (xb, 0)
    ax.add_patch(Polygon([(0, 0), Ap, Bp], closed=True, fc='#ffcdd2', ec=RED, lw=1.4, zorder=3))
    seg(ax, Bp, Hp, c=INK, ls='--', lw=1.0, z=4)
    for P_ in [Ap, Bp, Hp]:
        dot(ax, P_)
    lab(ax, Ap, f'${A}$', side * 0.1 * R, 0.12 * R)
    lab(ax, Bp, f'${B}$', 0.0, 0.13 * R)
    lab(ax, Hp, '$H$', 0.0, -0.13 * R)
    f.end(y0, fh)


def variant(pdf, n):
    d = VARS[n]
    f = Flow(pdf, n)
    f.part('Часть 1'); b1(f, d); b2(f, d); b3(f, d)
    f.part('Часть 2'); b4(f, d); b5(f, d)
    f.part('Часть 3'); b6(f, d); b7(f, d)
    f.p.save()


def summary_page(pdf):
    p = Page(pdf, 'Ответы')
    rows = [('', 'Вар. 1', 'Вар. 2', 'Вар. 3', 'Вар. 4'),
            ('1', '3', '2', '1', '4'),
            ('2', '3; 4; 6', '2; 5; 6', '1; 4; 6', '3; 5; 6'),
            ('3', '1', '4', '2', '3'),
            ('4', r'$\sqrt{34}$', r'$2\sqrt{10}$', r'$\sqrt{13}$', r'$2\sqrt{5}$'),
            ('5', '10', '(1; 4)', '10', '(−1; 4)'),
            ('6', '11', '12', '12', '9'),
            ('7*', r'$2\sqrt{6}$', r'$9\sqrt{3}$', r'$4\sqrt{5}$', '10')]
    edges = [15, 35, 75, 115, 155, 195]
    top, rh = 25, 12
    for i, r in enumerate(rows):
        for j, c in enumerate(r):
            p.ax.text((edges[j] + edges[j + 1]) / 2, top + i * rh + 8, c, fontsize=FS + 1,
                      color=RED if i == 0 or j == 0 else INK, ha='center', va='baseline')
    for i in range(len(rows) + 1):
        p.ax.plot([edges[0], edges[-1]], [top + i * rh] * 2, color=INK, lw=0.8)
    for x in edges:
        p.ax.plot([x, x], [top, top + rh * len(rows)], color=INK, lw=0.8)
    p.save()


out = os.path.join(HERE, 'КР1_векторы_решения.pdf')
with PdfPages(out) as pdf:
    for n in range(1, 5):
        variant(pdf, n)
    summary_page(pdf)
print(out)
