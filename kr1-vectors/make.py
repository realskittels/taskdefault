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

W, H = 297, 210            # landscape page, mm
INK = '#1b3a9a'            # blue pen
RED = '#c62828'            # red pen (answers / highlights)
PEN = '#2b2b2b'            # pencil for drawings
GREEN = '#2e7d32'
GRID = '#9cc3e6'
FS = 16                    # base font size


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
        ax.plot([282, 282], [0, H], color='#e57373', lw=1.0, zorder=-4)   # margin
        self.ax = ax
        self.y = 20
        if title:
            ax.text(141, 13, title, ha='center', va='baseline', fontsize=FS + 3,
                    color=INK, fontweight='bold')
            self.y = 25

    def w(self, s, x=12, size=FS, color=INK, step=10, **kw):
        self.ax.text(x, self.y, s, fontsize=size, color=color, va='baseline', **kw)
        self.y += step

    def head(self, s, x=12):
        self.ax.text(x, self.y, s, fontsize=FS + 1, color=INK, va='baseline', fontweight='bold')
        self.ax.plot([x, x + 3.2 * len(s.replace('$', '')) * 0.62], [self.y + 1.2] * 2,
                     color=INK, lw=0.8)
        self.y += 10

    def answer(self, s, x=12):
        self.ax.text(x, self.y, 'Ответ: ' + s, fontsize=FS + 1, color=RED, va='baseline',
                     bbox=dict(boxstyle='square,pad=0.35', fc='none', ec=RED, lw=1.1))
        self.y += 12

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
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=16, color=c, lw=lw,
                                 shrinkA=0, shrinkB=0, zorder=4))


def lab(ax, p, s, dx=0, dy=0, c=PEN, size=FS):
    ax.text(p[0] + dx, p[1] + dy, s, fontsize=size, color=c, ha='center', va='center', zorder=6)


def dot(ax, p, c=PEN, r=None):
    ax.plot([p[0]], [p[1]], 'o', color=c, ms=4.5, zorder=5)


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


# ======================= pages =======================
def page_t1_t3(pdf, n, d):
    t = d['t1']
    p = Page(pdf, f'Контрольная работа № 1.   Вариант {n}')
    p.w('Часть 1', x=120, size=FS + 1, color=INK)
    p.head('Задача 1.')
    p.w(f'$KMNP$ — параллелограмм. ${V(t["start"] + t["a"])}+{V(t["start"] + t["b"])}=\\;?$')
    p.w(f'По правилу параллелограмма сумма — диагональ из ${t["start"]}$:')
    p.w(f'${V(t["start"] + t["a"])}+{V(t["start"] + t["b"])}={V(t["start"] + t["res"])}$', x=40, size=FS + 3, step=12)
    p.answer(t['ans'] + f'   $({V(OPTS1[t["ans"]])})$')
    # figure
    pts = {'K': (0, 0), 'M': (1.3, 2.6), 'N': (5.3, 2.6), 'P': (4, 0)}
    ax = p.inset(172, 22, 105, 80, (-0.8, 6.1), (-0.8, 3.4))
    poly = [pts[c] for c in 'KMNP']
    ax.add_patch(Polygon(poly, closed=True, fill=False, ec=PEN, lw=1.3))
    s = pts[t['start']]
    arrow(ax, s, pts[t['a']], c=INK, lw=2.2)
    arrow(ax, s, pts[t['b']], c=INK, lw=2.2)
    arrow(ax, s, pts[t['res']], c=RED, lw=2.2)
    off = {'K': (-0.35, -0.3), 'M': (-0.3, 0.3), 'N': (0.3, 0.3), 'P': (0.35, -0.3)}
    for c, q in pts.items():
        lab(ax, q, f'${c}$', *off[c])

    t3 = d['t3']; u, v, U, Vv, k1, k2, r = t3['u'], t3['v'], t3['U'], t3['Vv'], t3['k1'], t3['k2'], t3['r']
    A = (k1 * U[0], k1 * U[1]); B = (k2 * Vv[0], k2 * Vv[1]); R = (A[0] - B[0], A[1] - B[1])
    p.skip(4)
    p.head('Задача 3.')
    p.w(f'$\\vec{{{u}}}\\,{cv(U)},\\ \\vec{{{v}}}\\,{cv(Vv)}.\\quad \\vec{{{r}}}={k1}\\vec{{{u}}}-{k2}\\vec{{{v}}}$')
    p.w(f'${k1}\\vec{{{u}}}\\,\\{{{k1}\\cdot{num(U[0])};\\,{k1}\\cdot{num(U[1])}\\}}={cv(A)}$')
    p.w(f'${k2}\\vec{{{v}}}\\,\\{{{k2}\\cdot{num(Vv[0])};\\,{k2}\\cdot{num(Vv[1])}\\}}={cv(B)}$')
    p.w(f'$\\vec{{{r}}}\\,\\{{{A[0]}-{num(B[0])};\\,{A[1]}-{num(B[1])}\\}}={cv(R)}$')
    p.answer(t3['ans'] + f'   $(\\vec{{{r}}}\\,{cv(R)})$')
    p.save()


def page_t2(pdf, n, d):
    t = d['t2']
    p = Page(pdf, f'Контрольная работа № 1.   Вариант {n}')
    name = 'прямоугольник' if t['fig'] == 'rect' else 'ромб'
    p.head('Задача 2.')
    p.w(f'$ABCD$ — {name}.', step=12)
    for i, (eq, ok, why) in enumerate(t['items'], 1):
        mark = '+' if ok else '−'
        col = GREEN if ok else RED
        p.ax.text(14, p.y, f'{i})', fontsize=FS, color=INK, va='baseline')
        p.ax.text(22, p.y, f'${eq}$', fontsize=FS, color=INK, va='baseline')
        p.ax.text(78, p.y, ('верно' if ok else 'неверно') + ' (' + why + ')', fontsize=FS - 1,
                  color=col, va='baseline')
        p.y += 11
    p.skip(2)
    p.answer(t['ans'])
    if t['fig'] == 'rect':
        P = {'A': (0, 0), 'B': (0, 2.6), 'C': (5, 2.6), 'D': (5, 0)}
        off = {'A': (-0.3, -0.3), 'B': (-0.3, 0.3), 'C': (0.3, 0.3), 'D': (0.3, -0.3)}
        ax = p.inset(185, 30, 92, 75, (-0.7, 5.7), (-0.8, 3.4))
        for a, b in [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')]:
            seg(ax, P[a], P[b])
        right_angle(ax, P['A'], (1, 0), (0, 1), 0.3)
    else:
        P = {'A': (0, 0), 'B': (2.6, 1.5), 'C': (5.2, 0), 'D': (2.6, -1.5)}
        off = {'A': (-0.35, 0), 'B': (0, 0.35), 'C': (0.35, 0), 'D': (0, -0.4)}
        ax = p.inset(185, 30, 92, 75, (-0.7, 5.9), (-2.1, 2.1))
        for a, b in [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'A')]:
            seg(ax, P[a], P[b])
        right_angle(ax, (2.6, 0), (1, 0), (0, 1), 0.25)
    seg(ax, P['A'], P['C'], lw=1.0); seg(ax, P['B'], P['D'], lw=1.0)
    O = ((P['A'][0] + P['C'][0]) / 2, (P['A'][1] + P['C'][1]) / 2)
    dot(ax, O)
    for c in 'ABCD':
        lab(ax, P[c], f'${c}$', *off[c])
    if t['fig'] == 'rect':
        lab(ax, O, '$O$', 0.0, -0.4, size=FS - 1)
    else:
        lab(ax, O, '$O$', -0.3, -0.35, size=FS - 1)
    # notes under the figure
    if t['fig'] == 'rect':
        notes = ['$AC=BD$ (диагонали равны)', '$AO=OC=BO=OD$', '$\\overrightarrow{AB}=\\overrightarrow{DC}$, $\\overrightarrow{BA}=\\overrightarrow{CD}$']
    else:
        notes = ['$AB=BC=CD=DA$', '$AO=OC,\\ BO=OD$', '$\\overrightarrow{BC}=\\overrightarrow{AD}$, $\\overrightarrow{CB}=\\overrightarrow{DA}$']
    yy = 125
    notes = []
    for s_ in notes:
        p.ax.text(190, yy, s_, fontsize=FS - 2, color=PEN, va='baseline'); yy += 10
    p.save()


def page_t4_t5(pdf, n, d):
    p = Page(pdf, f'Контрольная работа № 1.   Вариант {n}')
    p.w('Часть 2', x=120, size=FS + 1)
    t4 = d['t4']; b = t4['b']
    p.head('Задача 4.')
    p.w(f'$\\vec b\\,{cv(b)}$.    $|\\vec b|=\\sqrt{{x^2+y^2}}$')
    p.w(f'$|\\vec b|={t4["calc"]}$', step=12)
    p.answer(t4['ans'])
    # small picture for vector b
    ax = p.inset(150, 22, 62, 62, (-6, 6), (-6.5, 6))
    coord_grid(ax, -5.5, 5.5, -6.5, 5.5)
    axes_xy(ax, -5.8, 5.8, -6.6, 5.8)
    arrow(ax, (0, 0), b, c=RED, lw=2.0)
    seg(ax, (b[0], 0), b, ls='--', lw=0.9); seg(ax, (0, b[1]), b, ls='--', lw=0.9)
    lab(ax, b, '$\\vec b$', 0.9 if b[0] > 0 else -0.9, 0.3, c=RED)

    t5 = d['t5']; (n1, P1), (n2, P2) = t5['P'], t5['Q']
    p.skip(3)
    p.head('Задача 5.')
    p.w(f'По рисунку: ${n1}({P1[0]};\\,{P1[1]})$,  ${n2}({P2[0]};\\,{P2[1]})$.')
    if t5['kind'] == 'len':
        dx, dy = P2[0] - P1[0], P2[1] - P1[1]
        p.w(f'${n1}{n2}=\\sqrt{{(x_2-x_1)^2+(y_2-y_1)^2}}$')
        p.w(f'${n1}{n2}=\\sqrt{{({P2[0]}-{num(P1[0])})^2+({P2[1]}-{num(P1[1])})^2}}='
            f'\\sqrt{{{dx}^2+{dy}^2}}=\\sqrt{{{dx*dx}+{dy*dy}}}=\\sqrt{{{dx*dx+dy*dy}}}={int(np.sqrt(dx*dx+dy*dy))}$', step=12)
        p.answer(f'{n1}{n2} = {int(np.sqrt(dx*dx+dy*dy))}')
    else:
        mx, my = (P1[0] + P2[0]) / 2, (P1[1] + P2[1]) / 2
        p.w(f'Середина $F$: $x=\\frac{{x_1+x_2}}{{2}}$,  $y=\\frac{{y_1+y_2}}{{2}}$', step=12)
        p.w(f'$x=\\frac{{{P1[0]}+{P2[0]}}}{{2}}=\\frac{{{P1[0]+P2[0]}}}{{2}}={int(mx)}$;   '
            f'$y=\\frac{{{P1[1]}+{P2[1]}}}{{2}}=\\frac{{{P1[1]+P2[1]}}}{{2}}={int(my)}$', step=13)
        p.answer(f'$({int(mx)};\\,{int(my)})$')
    # coordinate figure
    xs = [P1[0], P2[0], 0]; ys = [P1[1], P2[1], 0]
    x0, x1 = min(xs) - 1.5, max(xs) + 1.8; y0, y1 = min(ys) - 1.5, max(ys) + 1.8
    ax = p.inset(215, 75, 65, 128, (x0, x1), (y0, y1))
    coord_grid(ax, x0 + 0.3, x1 - 0.3, y0 + 0.3, y1 - 0.3)
    axes_xy(ax, x0 + 0.3, x1, y0 + 0.3, y1)
    seg(ax, P1, P2, c=INK, lw=2.2)
    for nm, P in [(n1, P1), (n2, P2)]:
        dot(ax, P, c=INK)
        seg(ax, (P[0], 0), P, ls='--', lw=0.9); seg(ax, (0, P[1]), P, ls='--', lw=0.9)
        lab(ax, P, f'${nm}$', 0.7 if P[0] >= max(P1[0], P2[0]) else -0.7, 0.5, c=INK)
        lab(ax, (P[0], 0), f'{P[0]}', 0.0, 0.6 if P[1] < 0 else -0.6, size=FS - 4)
        lab(ax, (0, P[1]), f'{P[1]}', -0.7 if P[0] > 0 else 0.7, 0, size=FS - 4)
    if t5['kind'] == 'mid':
        F = ((P1[0] + P2[0]) / 2, (P1[1] + P2[1]) / 2)
        dot(ax, F, c=RED); lab(ax, F, '$F$', 0.5, 0.6, c=RED)
    p.save()


def page_t6(pdf, n, d):
    t = d['t6']; s, m, e1, e2, v1, v2 = t['seg'], t['mid'], t['e1'], t['e2'], t['v1'], t['v2']
    res = (v1 + v2) / 2; res_s = f'{res:g}'
    p = Page(pdf, f'Контрольная работа № 1.   Вариант {n}')
    p.w('Часть 3', x=120, size=FS + 1)
    p.head('Задача 6.')
    p.w(f'Дано: ${s}\\cap a=\\varnothing$, ${m}$ — середина ${s}$,')
    p.w(f'${e1}{e1}_1\\perp a$, ${e2}{e2}_1\\perp a$, ${m}{m}_1\\perp a$, ${e1}{e1}_1={v1}$, ${e2}{e2}_1={v2}$.')
    p.w(f'Найти: ${m}{m}_1$.', step=12)
    p.w('Решение.')
    p.w(f'1) ${e1}{e1}_1\\parallel {m}{m}_1\\parallel {e2}{e2}_1$ (все $\\perp a$) $\\Rightarrow$ ${e1}{e1}_1{e2}_1{e2}$ — трапеция.')
    p.w(f'2) ${m}$ — середина ${s}$ $\\Rightarrow$ ${m}_1$ — середина ${e1}_1{e2}_1$ (т. Фалеса).')
    p.w(f'3) ${m}{m}_1$ — средняя линия трапеции:')
    p.w(f'${m}{m}_1=\\frac{{{e1}{e1}_1+{e2}{e2}_1}}{{2}}=\\frac{{{v1}+{v2}}}{{2}}=\\frac{{{v1+v2}}}{{2}}={res_s}$', x=40, size=FS + 3, step=14)
    p.answer(res_s)
    # figure
    big_left = v1 > v2
    h1, h2 = (3.2, 1.3) if big_left else (1.3, 3.2)
    X1, X2 = 0.6, 5.4
    A, B = (X1, h1), (X2, h2); A1, B1 = (X1, 0), (X2, 0)
    C = ((X1 + X2) / 2, (h1 + h2) / 2); C1 = (C[0], 0)
    ax = p.inset(180, 70, 98, 85, (-0.4, 6.4), (-0.9, 4.0))
    seg(ax, (-0.3, 0), (6.3, 0), lw=1.3); lab(ax, (6.3, 0), '$a$', 0, 0.3)
    seg(ax, A, B, c=INK, lw=2.0)
    for P, Q in [(A, A1), (B, B1), (C, C1)]:
        seg(ax, P, Q, c=PEN, lw=1.2)
        right_angle(ax, Q, (1, 0), (0, 1), 0.22)
    for P in [A, B, C, A1, B1, C1]:
        dot(ax, P)
    lab(ax, A, f'${e1}$', -0.3, 0.3); lab(ax, B, f'${e2}$', 0.3, 0.3); lab(ax, C, f'${m}$', 0.1, 0.4)
    lab(ax, A1, f'${e1}_1$', 0, -0.45); lab(ax, B1, f'${e2}_1$', 0, -0.45); lab(ax, C1, f'${m}_1$', 0, -0.45)
    lab(ax, ((A[0] + A1[0]) / 2, A[1] / 2), f'{v1}', -0.35, 0, c=RED, size=FS - 2)
    lab(ax, ((B[0] + B1[0]) / 2, B[1] / 2), f'{v2}', 0.35, 0, c=RED, size=FS - 2)
    lab(ax, (C[0], C[1] / 2), '?', 0.3, 0, c=RED, size=FS - 1)
    # equal-segment ticks
    for P, Q in [(A, C), (C, B)]:
        mpt = np.array([(P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2])
        dvec = np.array([Q[0] - P[0], Q[1] - P[1]]); nv = np.array([-dvec[1], dvec[0]]); nv /= np.linalg.norm(nv)
        seg(ax, mpt - nv * 0.15, mpt + nv * 0.15, lw=1.0)
    p.save()


def page_t7(pdf, n, d):
    t = d['t7']
    p = Page(pdf, f'Контрольная работа № 1.   Вариант {n}')
    A, B, side = t['A'], t['B'], t['side']
    xa = t['Rs'] if side > 0 else '-' + t['Rs']
    p.head('Задача 7*.')
    p.w(f'Дано: $x^2+y^2={t["R2"]}$;  ${A}$ на $Ox$ $(x{">" if side > 0 else "<"}0)$;  ${B}$ на окр., $x_{B}={t["xb"]}$.')
    p.w(f'Найти: $S_{{O{B}{A}}}$.', step=12)
    p.w('Решение.')
    p.w(f'1) Центр $O(0;\\,0)$, радиус $R=\\sqrt{{{t["R2"]}}}={t["Rs"]}$.' if t['Rs'] not in ('6', '5')
        else f'1) Центр $O(0;\\,0)$, радиус $R=\\sqrt{{{t["R2"]}}}={t["Rs"]}$.')
    p.w(f'2) ${A}$ лежит на $Ox$: $y=0$, $x^2={t["R2"]}$, $x={xa}$  $\\Rightarrow$  ${A}({xa};\\,0)$,  $O{A}={t["Rs"]}$.')
    p.w(f'3) ${B}$: ${num(t["xb"])}^2+y^2={t["R2"]}$, $y^2={t["R2"]}-{t["xb"]**2}={t["y2"]}$, $y=\\pm {t["ys"]}$.')
    p.w(f'4) Высота ${B}H$ к $O{A}$ (на оси $Ox$): ${B}H=|y|={t["ys"]}$.')
    p.w(f'5) $S=\\frac{{1}}{{2}}\\cdot O{A}\\cdot {B}H={t["S"]}$', size=FS + 2, step=13)
    p.answer(t['ans'])
    # figure
    R = t['Rv']; xb = t['xb']; yb = np.sqrt(t['y2'])
    L = R + 1.5
    ax = p.inset(192, 25, 88, 120, (-L, L), (-L, L))
    axes_xy(ax, -L, L, -L, L)
    ax.add_patch(Circle((0, 0), R, fill=False, ec=PEN, lw=1.3))
    Ap = (side * R, 0); Bp = (xb, yb); Hp = (xb, 0)
    ax.add_patch(Polygon([(0, 0), Ap, Bp], closed=True, fc='#ffcdd2', ec=RED, lw=1.8, alpha=0.9, zorder=3))
    seg(ax, Bp, Hp, c=INK, ls='--', lw=1.2, z=4)
    right_angle(ax, Hp, (1 if xb < 0 else -1, 0), (0, 1), R * 0.07)
    for P in [Ap, Bp, Hp]:
        dot(ax, P)
    lab(ax, Ap, f'${A}$', side * 0.45, -0.45 * R / 4)
    lab(ax, Bp, f'${B}$', 0.0, 0.5 * R / 4)
    lab(ax, Hp, '$H$', -0.0, -0.5 * R / 4)
    p.save()


def title_page(pdf):
    p = Page(pdf)
    p.ax.text(141, 55, 'Контрольная работа № 1', ha='center', fontsize=40, color=INK, fontweight='bold')
    p.ax.text(141, 75, 'Векторы. Метод координат', ha='center', fontsize=30, color=INK)
    p.ax.text(141, 95, 'Решения всех четырёх вариантов', ha='center', fontsize=24, color=RED)
    p.ax.text(141, 125, 'Н. Б. Мельникова, «Контрольные работы по геометрии. 9 класс»',
              ha='center', fontsize=19, color=PEN)
    p.ax.text(141, 140, 'Части 1–2 — ответы с пояснениями, часть 3 — полное решение с чертежом',
              ha='center', fontsize=19, color=PEN)
    # small decorative vectors
    ax = p.inset(100, 150, 90, 45, (0, 6), (0, 3))
    arrow(ax, (0.5, 0.5), (3.5, 0.5), c=INK); arrow(ax, (0.5, 0.5), (2.0, 2.5), c=INK)
    arrow(ax, (0.5, 0.5), (5.0, 2.5), c=RED)
    seg(ax, (3.5, 0.5), (5.0, 2.5), ls='--', lw=1); seg(ax, (2.0, 2.5), (5.0, 2.5), ls='--', lw=1)
    lab(ax, (2, 0.15), '$\\vec a$', c=INK); lab(ax, (1.0, 1.8), '$\\vec b$', c=INK)
    lab(ax, (2.6, 2.0), '$\\vec a+\\vec b$', c=RED)
    p.save()


def summary_page(pdf):
    p = Page(pdf, 'Ответы (сводная таблица)')
    rows = [('№', 'Вариант 1', 'Вариант 2', 'Вариант 3', 'Вариант 4'),
            ('1', '3', '2', '1', '4'),
            ('2', '3; 4; 6', '2; 5; 6', '1; 4; 6', '3; 5; 6'),
            ('3', '1', '4', '2', '3'),
            ('4', r'$\sqrt{34}$', r'$2\sqrt{10}$', r'$\sqrt{13}$', r'$2\sqrt{5}$'),
            ('5', '10', '(1; 4)', '10', '(−1; 4)'),
            ('6', '11', '12', '12', '9'),
            ('7*', r'$2\sqrt{6}$', r'$9\sqrt{3}$', r'$4\sqrt{5}$', '10')]
    xs = [27, 69.5, 124.5, 179.5, 234.5]; x_edges = [12, 42, 97, 152, 207, 262]
    y = 35
    for i, r in enumerate(rows):
        for x, c in zip(xs, r):
            p.ax.text(x, y + 7, c, fontsize=FS + 2, color=INK if i else RED,
                      ha='center', va='baseline')
        y += 20
    for yy in range(25, 25 + 20 * len(rows) + 1, 20):
        p.ax.plot([12, 262], [yy, yy], color=INK, lw=1)
    for xx in x_edges:
        p.ax.plot([xx, xx], [25, 25 + 20 * len(rows)], color=INK, lw=1)
    p.ax.text(141, 200, 'Ответы сверены с ответами в конце сборника.', ha='center', fontsize=FS - 1, color=PEN)
    p.save()


out = os.path.join(HERE, 'КР1_векторы_решения.pdf')
with PdfPages(out) as pdf:
    title_page(pdf)
    for n in range(1, 5):
        d = VARS[n]
        page_t1_t3(pdf, n, d)
        page_t2(pdf, n, d)
        page_t4_t5(pdf, n, d)
        page_t6(pdf, n, d)
        page_t7(pdf, n, d)
    summary_page(pdf)
print(out)
