"""Transição em fusão no piscar, com câmera lenta real (fonte 60 qps) e frase discreta."""
import json, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

V = '/home/user/edita-ai/v1/'; L = V + 'l60/'
W, H, FPS = 1080, 1920, 30
SW, SH = 1440, 2560; K = SW / W          # resolução de trabalho (vinda do 4K)

J = json.load(open(L + 'olhos.json'))
def eyes(key):
    a = np.array([r[1:5] for r in J[key]], float)
    k = np.ones(7) / 7
    return np.stack([np.convolve(np.pad(a[:, c], 3, mode='edge'), k, 'valid') for c in range(4)], 1)
EA, ED = eyes('a60.mov'), eyes('d60.mov')

def read(path, idx):
    cap = cv2.VideoCapture(path); out = {}; i = 0; need = set(idx); mx = max(idx)
    while i <= mx:
        ok, f = cap.read()
        if not ok: break
        if i in need: out[i] = cv2.resize(f, (SW, SH), interpolation=cv2.INTER_AREA)
        i += 1
    return out

# ---- linha do tempo (posições nos quadros de 60 qps) ----
OFF = 53                       # depois = antes - 53 (piscadas alinhadas: 234 <-> 181)
plan = []                      # (posA ou None, posD ou None, peso_depois)
p = 132.0
while p < 200: plan.append((p, None, 0)); p += 2          # 1x
n = 15
for k in range(n): plan.append((p, None, 0)); p += 2 - (k + 1) / n   # desacelera 1x -> 0,5x
while p < 229: plan.append((p, None, 0)); p += 1          # 0,5x
XN = 12
for k in range(XN):                                       # fusão em 0,25x, olhos fechados
    a = (k + 1) / (XN + 1); a = a * a * (3 - 2 * a)
    plan.append((p, p - OFF, a)); p += 0.5
q = p - OFF
while q <= 214: plan.append((None, q, 1)); q += 1         # depois em 0,5x (abre os olhos devagar)
T_X0 = next(i for i, r in enumerate(plan) if r[0] is not None and r[1] is not None)
T_X1 = T_X0 + XN

need_a = sorted({int(np.floor(r[0])) + d for r in plan if r[0] is not None for d in (0, 1)})
need_d = sorted({min(int(np.floor(r[1])) + d, 215) for r in plan if r[1] is not None for d in (0, 1)})
A = read(V + 'original_antes.mov', need_a); D = read(V + 'original_depois.mov', need_d)
def frame(src, E, pos):
    i = int(np.floor(pos)); f = pos - i; j = min(i + 1, max(src))
    img = src[i] if f < 1e-3 else cv2.addWeighted(src[i], 1 - f, src[j], f, 0)
    e = E[i] * (1 - f) + E[min(i + 1, len(E) - 1)] * f
    return img, e

# ---- alinhamento pelos olhos ----
def geom(e):
    l, r = e[:2], e[2:]; c = (l + r) / 2; d = r - l
    return c, np.hypot(*d), np.degrees(np.arctan2(d[1], d[0]))
ca, da, aa = geom(EA[232]); cd, dd, ad = geom(ED[179])
TA = aa + 0.3 * (ad - aa); TD = 1.22 * da; TC = ca + 0.3 * (cd - ca) + np.array([0, 0])
def M_for(e, w):
    c, d, ang = geom(e)
    s = 1 + w * (TD / d - 1); rot = w * (ang - TA); tc = c + w * (TC - c)
    M = np.vstack([cv2.getRotationMatrix2D(tuple(c), rot, s), [0, 0, 1]])
    M[:2, 2] += tc - c
    S = np.diag([1 / K, 1 / K, 1])                         # 1440 -> 1080
    return (S @ M)[:2]
def warp(f, M):
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_AREA if M[0, 0] < 1 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
def sm(x):
    x = min(max(x, 0), 1); return x * x * (3 - 2 * x)

# ---- textos (fonte e cores da marca) ----
FF = '/home/user/edita-ai/fontes/pk_fontsource-playfair-display-5.3.0.tgz/files/playfair-display-latin-%d-%s.woff'
def texto(linhas, font, cor, y):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k, t in enumerate(linhas): d.text((W / 2, y + k * font.size * 1.25), t, font=font, fill=(40, 25, 15, 150), anchor='mm')
    sh = lay.filter(ImageFilter.GaussianBlur(7))
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.alpha_composite(sh, (0, 3))
    d = ImageDraw.Draw(out)
    for k, t in enumerate(linhas): d.text((W / 2, y + k * font.size * 1.25), t, font=font, fill=cor, anchor='mm')
    return np.array(out).astype(np.float32) / 255
T1 = texto(['"Minha sobrancelha é', 'fina e sem volume"'], ImageFont.truetype(FF % (500, 'italic'), 56), (238, 225, 215, 255), 1400)
T2 = texto(['Resolvido!'], ImageFont.truetype(FF % (600, 'italic'), 76), (232, 198, 137, 255), 1430)
def over(img_bgr, T, a):
    if a <= 0: return img_bgr
    rgb = img_bgr[:, :, ::-1].astype(np.float32) / 255
    al = T[:, :, 3:] * a
    rgb = rgb * (1 - al) + T[:, :, :3] * al
    return np.ascontiguousarray((rgb[:, :, ::-1] * 255).astype(np.uint8))

N = len(plan); t1_out = T_X0 - 4; t2_in = T_X1 + 10
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', V + 'lenta_sem_som.mp4'], stdin=subprocess.PIPE)
EA4, ED4 = EA * K, ED * K
TC, TD = TC * K, TD * K
R0 = T_X0 - 30                                   # começo do alinhamento do antes
for n, (pa, pd, wd) in enumerate(plan):
    if pa is not None:
        ia, ea = frame(A, EA4, pa); fa = warp(ia, M_for(ea, sm((n - R0) / (T_X0 - R0))))
    if pd is not None:
        idd, ed = frame(D, ED4, pd); fd = warp(idd, M_for(ed, 1 - sm((n - T_X1) / (N - T_X1))))
    if pa is not None and pd is not None: img = cv2.addWeighted(fa, 1 - wd, fd, wd, 0)
    else: img = fa if pa is not None else fd
    a1 = sm(n / 6) * (1 - sm((n - t1_out) / 6)); a2 = sm((n - t2_in) / 6)
    img = over(over(img, T1, a1), T2, a2)
    enc.stdin.write(img.tobytes())
enc.stdin.close(); enc.wait()
json.dump({'plan': plan, 'X0': T_X0, 'X1': T_X1}, open(V + 'lenta_plano.json', 'w'))
print(N, 'quadros =', N / FPS, 's | fusão', T_X0 / FPS, '-', T_X1 / FPS)
