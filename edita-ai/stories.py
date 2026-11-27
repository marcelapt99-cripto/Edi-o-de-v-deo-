"""Sequência de stories (1080x1920) nas cores da marca."""
import math, subprocess, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = '/home/user/edita-ai/stories/'
W, H, FPS = 1080, 1920, 30
F = '/home/user/edita-ai/fontes/pk_fontsource-%s.tgz/files/%s.woff'
def pf(w, i=False, s=100): return ImageFont.truetype(F % ('playfair-display-5.3.0', 'playfair-display-latin-%d-%s' % (w, 'italic' if i else 'normal')), s)
def ms(w, s): return ImageFont.truetype(F % ('montserrat-5.3.0', 'montserrat-latin-%d-normal' % w), s)
FUNDO = (238, 225, 215); MARROM = (90, 53, 36); DOURADO = (196, 138, 58); DCLARO = (232, 198, 137)
SALMAO = (216, 167, 156); BR = (255, 255, 255); SUAVE = (140, 110, 95); BEGE = (232, 222, 211)

def ease(p): p = min(max(p, 0), 1); return 1 - (1 - p) ** 3
def sm(p): p = min(max(p, 0), 1); return p * p * (3 - 2 * p)

def emoji(ch, size):
    f = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
    im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor='mm')
    im = im.crop(im.getbbox())
    return im.resize((size, int(size * im.height / im.width)), Image.LANCZOS)

def fundo():
    """Fundo off-white com moldura fina dourada e @ discreto."""
    im = Image.new('RGBA', (W, H), FUNDO + (255,)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((48, 48, W - 48, H - 48), 36, outline=DCLARO + (255,), width=2)
    d.text((W / 2, 1700), '@materencelash', font=ms(600, 30), fill=SUAVE, anchor='mm')
    return im

def sombra_card(im, box, r=32, fill=BR + (255,)):
    x0, y0, x1, y1 = box
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 8, x1, y1 + 8), r, fill=(60, 35, 20, 45))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(im).rounded_rectangle(box, r, fill=fill, outline=BEGE + (255,), width=2)

def layer(fn):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fn(ImageDraw.Draw(lay), lay); return lay

def put(base, lay, a, dy=0, sc=1.0, center=None):
    if a <= 0: return
    im = lay
    if sc != 1.0:
        cx, cy = center or (W / 2, H / 2)
        im = lay.transform((W, H), Image.AFFINE, (1 / sc, 0, cx - cx / sc, 0, 1 / sc, cy - cy / sc), Image.BICUBIC)
    if a < 1:
        im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    base.alpha_composite(im, (0, int(dy)))

def encode(name, frames_fn, n, sfx=()):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', OUT + name + '_v.mp4'], stdin=subprocess.PIPE)
    for k in range(n): p.stdin.write(np.array(frames_fn(k / FPS).convert('RGB')).tobytes())
    p.stdin.close(); p.wait()
    # sons: pop/whoosh baixinhos nos momentos de entrada
    dur = n / FPS
    ins = ['-f', 'lavfi', '-t', str(dur), '-i', 'anullsrc=r=48000:cl=stereo']; flt = []; k = 2
    for kind, t in sfx:
        ins += ['-i', OUT + '../v1/%s.wav' % kind]
        flt.append('[%d:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=-9dB,adelay=%d|%d[s%d]' % (k, t * 1000, t * 1000, k)); k += 1
    mix = '[1:a]' + ''.join('[s%d]' % j for j in range(2, k)) + 'amix=inputs=%d:normalize=0:duration=first[a]' % (k - 1)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', OUT + name + '_v.mp4'] + ins + ['-filter_complex', ';'.join(flt + [mix]),
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', OUT + name + '.mp4'], check=True)

def olho(d, cx, cy, s, prog, cor=DOURADO, w=7):
    """Olho fechado (arco para baixo) com cílios, desenhado aos poucos (0..1)."""
    us = np.linspace(0, 1, 60)
    pts = [(cx - s + 2 * s * u, cy + 0.32 * s * math.sin(math.pi * u)) for u in us]
    m = max(2, int(len(pts) * min(prog / 0.6, 1)))
    d.line(pts[:m], fill=cor, width=w, joint='curve')
    lp = min(1, max(0, (prog - 0.5) / 0.5)); nl = 7
    for j in range(int(nl * lp + 0.999)):
        u = 0.15 + 0.7 * j / (nl - 1)
        x, y = cx - s + 2 * s * u, cy + 0.32 * s * math.sin(math.pi * u)
        dx, dy = (u - 0.5) * 1.1, 1.0; n = math.hypot(dx, dy); L = s * (0.22 + 0.1 * math.sin(math.pi * u))
        d.line((x, y, x + L * dx / n, y + L * dy / n), fill=cor, width=w - 2)

# ---------------- STORY 1 ----------------
def story1():
    base = fundo()
    tag = layer(lambda d, l: (d.text((W / 2, 520), 'D E Z E M B R O   C H E G O U', font=ms(700, 30), fill=DOURADO, anchor='mm'),
                              d.line((400, 560, 680, 560), fill=DCLARO, width=2)))
    linhas = [('Você já planejou', pf(700, s=92), MARROM, 700), ('seus cílios para', pf(700, s=92), MARROM, 815),
              ('dezembro?', pf(700, True, 120), DOURADO, 950)]
    L = [layer(lambda d, l, t=t, f=f, c=c, y=y: d.text((W / 2, y), t, font=f, fill=c, anchor='mm')) for t, f, c, y in linhas]
    gata = emoji('😂', 64)
    def sub(d, l):
        f = ms(500, 40); t1 = 'Porque chegar no Natal capenga'; t2 = 'não dá, né, gata?'
        d.text((W / 2, 1150), t1, font=f, fill=SUAVE, anchor='mm')
        w2 = d.textlength(t2, font=f); x = W / 2 - (w2 + 80) / 2
        d.text((x, 1210), t2, font=f, fill=SUAVE, anchor='lm'); l.alpha_composite(gata, (int(x + w2 + 16), 1210 - gata.height // 2))
    S = layer(sub)
    def fr(t):
        im = base.copy()
        put(im, tag, ease(t / 0.4), dy=-20 * (1 - ease(t / 0.4)))
        for k, l in enumerate(L):
            t0 = 0.35 + 0.3 * k; p = ease((t - t0) / 0.4)
            put(im, l, p, dy=40 * (1 - p)) if k < 2 else put(im, l, p, sc=0.85 + 0.15 * p + 0.05 * math.sin(math.pi * p), center=(W / 2, 950))
        d = ImageDraw.Draw(im)
        if t > 1.5: olho(d, W / 2, 1380, 130, (t - 1.5) / 1.0)
        put(im, S, ease((t - 2.4) / 0.4), dy=30 * (1 - ease((t - 2.4) / 0.4)))
        return im
    encode('story1', fr, 6 * FPS, sfx=[('whoosh', 0.3), ('pop', 0.95), ('pop', 2.4)])

# ---------------- STORY 2 ----------------
def story2():
    ph = Image.open(OUT + 'foto_manutencao.jpg').convert('RGB')
    s = max(W / ph.width, H / ph.height); ph = ph.resize((int(ph.width * s) + 1, int(ph.height * s) + 1), Image.LANCZOS)
    ph = ph.crop(((ph.width - W) // 2, (ph.height - H) // 2, (ph.width - W) // 2 + W, (ph.height - H) // 2 + H)).convert('RGBA')
    big = ph.resize((int(W * 1.12), int(H * 1.12)), Image.LANCZOS)
    cor = emoji('😂', 50)
    cor = emoji('😂', 42)
    def card(d, l):
        """Texto simples, sem fundo, sobre a parte escura (luva e cabelo), com sombra leve."""
        f1, f2 = pf(600, True, 58), pf(500, True, 42)
        t2 = 'pra ninguém chegar capenga no Natal'
        w2 = d.textlength(t2, font=f2); x2 = W / 2 - (w2 + 54) / 2
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
        ds.text((W / 2, 1685), 'Repondo os fiozinhos…', font=f1, fill=(0, 0, 0, 170), anchor='mm')
        ds.text((x2, 1752), t2, font=f2, fill=(0, 0, 0, 170), anchor='lm')
        l.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)), (0, 3))
        d = ImageDraw.Draw(l)
        d.text((W / 2, 1685), 'Repondo os fiozinhos…', font=f1, fill=FUNDO, anchor='mm')
        d.text((x2, 1752), t2, font=f2, fill=FUNDO, anchor='lm')
        l.alpha_composite(cor, (int(x2 + w2 + 12), 1752 - cor.height // 2))
    C = layer(card)
    def fr(t):
        z = 1 + 0.12 * sm(t / 6)                     # zoom lento, centrado nos cílios
        cx, cy = 560, 850
        bw, bh = W / z, H / z; x0 = cx - bw * cx / W; y0 = cy - bh * cy / H
        im = ph.transform((W, H), Image.EXTENT, (x0, y0, x0 + bw, y0 + bh), Image.BICUBIC)
        p = ease((t - 0.5) / 0.6); put(im, C, p)
        return im
    encode('story2', fr, 6 * FPS, sfx=[])

# ---------------- STORY 3 (imagem) ----------------
def story3():
    im = fundo(); d = ImageDraw.Draw(im)
    d.text((W / 2, 330), 'C O M O   F U N C I O N A', font=ms(700, 30), fill=DOURADO, anchor='mm')
    d.text((W / 2, 430), 'Planejamento', font=pf(700, s=96), fill=MARROM, anchor='mm')
    d.text((W / 2, 540), 'de fim de ano', font=pf(700, True, 96), fill=DOURADO, anchor='mm')
    itens = [('Clientes fixas', 'já estão com aplicação e', 'manutenções agendadas'),
             ('Agenda aberta', 'para clientes novas até o', 'Natal e o Ano Novo'),
             ('Deixe TODAS as manutenções', 'marcadas até as festas', '')]
    y = 660
    for t, a, b in itens:
        sombra_card(im, (110, y, 970, y + 200)); d = ImageDraw.Draw(im)
        d.ellipse((150, y + 50, 250, y + 150), fill=(244, 232, 214))
        d.line((175, y + 102, 193, y + 120, 226, y + 80), fill=DOURADO, width=8, joint='curve')
        d.text((285, y + 55), t, font=pf(700, s=44), fill=MARROM)
        d.text((285, y + 115), a, font=ms(500, 32), fill=SUAVE)
        if b: d.text((285, y + 152), b, font=ms(500, 32), fill=SUAVE)
        y += 240
    f = pf(600, True, 46)
    d.text((W / 2, 1420), 'Senão, queriiida, pode ficar', font=f, fill=MARROM, anchor='mm')
    d.text((W / 2, 1482), 'sem horário no fim do ano!', font=f, fill=MARROM, anchor='mm')
    im.convert('RGB').save(OUT + 'story3.png')

# ---------------- STORY 5 ----------------
def story5():
    base = fundo()
    zap = emoji('💬', 90)
    def topo(d, l):
        d.text((W / 2, 430), 'A G E N D A   A B E R T A', font=ms(700, 30), fill=DOURADO, anchor='mm')
        d.line((400, 470, 680, 470), fill=DCLARO, width=2)
    T = layer(topo)
    linhas = [('Bora já chamar', pf(700, s=96), MARROM, 620), ('no WhatsApp', pf(700, True, 110), DOURADO, 745),
              ('pra não ficar', pf(700, s=96), MARROM, 880), ('sem horário!', pf(700, s=96), MARROM, 995)]
    L = [layer(lambda d, l, t=t, f=f, c=c, y=y: d.text((W / 2, y), t, font=f, fill=c, anchor='mm')) for t, f, c, y in linhas]
    Z = layer(lambda d, l: l.alpha_composite(zap, (W // 2 + 300, 690)))
    dica = layer(lambda d, l: d.text((W / 2, 1150), 'toque no link abaixo', font=ms(600, 34), fill=SUAVE, anchor='mm'))
    def fr(t):
        im = base.copy(); put(im, T, ease(t / 0.4))
        for k, l in enumerate(L):
            t0 = 0.3 + 0.28 * k; p = ease((t - t0) / 0.4)
            put(im, l, p, dy=40 * (1 - p)) if k != 1 else put(im, l, p, sc=0.85 + 0.15 * p + 0.05 * math.sin(math.pi * p), center=(W / 2, 745))
        p = ease((t - 1.0) / 0.35); pass
        p = ease((t - 1.8) / 0.4); put(im, dica, p)
        if t > 1.8:   # seta pulando, apontando para o espaço do link
            b = 14 * abs(math.sin((t - 1.8) * 4)); d = ImageDraw.Draw(im); a = int(255 * p)
            y = 1215 + b; d.line((W / 2, y, W / 2, y + 70), fill=DOURADO + (a,), width=6)
            d.line((W / 2 - 26, y + 46, W / 2, y + 74, W / 2 + 26, y + 46), fill=DOURADO + (a,), width=6, joint='curve')
        return im
    encode('story5', fr, 6 * FPS, sfx=[('whoosh', 0.3), ('pop', 0.6), ('pop', 1.0)])

for s in sys.argv[1:]: globals()['story' + s]()
