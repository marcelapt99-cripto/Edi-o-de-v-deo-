import subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

V = '/home/user/edita-ai/v1/'
F = '/home/user/edita-ai/fontes/pk_fontsource-%s.tgz/files/%s.woff'
def pf(w, i=False, s=100):
    return ImageFont.truetype(F % ('playfair-display-5.3.0', 'playfair-display-latin-%d-%s' % (w, 'italic' if i else 'normal')), s)
def ms(w, s):
    return ImageFont.truetype(F % ('montserrat-5.3.0', 'montserrat-latin-%d-normal' % w), s)

FUNDO = (238, 225, 215); MARROM = (90, 53, 36); DOURADO = (196, 138, 58); BR = (255, 255, 255)
W, H, FPS = 1080, 1920, 30

def card(box, r=30, fill=FUNDO + (240,)):
    """Cartão claro com sombra suave (visual E-book)."""
    x0, y0, x1, y1 = box
    pad = 40
    lay = Image.new('RGBA', (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', lay.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 6, pad + x1 - x0, pad + 6 + y1 - y0), r, fill=(40, 25, 15, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    lay.alpha_composite(sh)
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((pad, pad, pad + x1 - x0, pad + y1 - y0), r, fill=fill, outline=(232, 222, 211, 255), width=2)
    return lay, d, (x0 - pad, y0 - pad), pad

def make_gancho():
    f1, f2 = pf(700, s=78), pf(700, True, 92)
    l1, l2 = 'Sobrancelhas sem volume?', 'Olha a diferença'
    tmp = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    w = max(tmp.textlength(l1, font=f1), tmp.textlength(l2, font=f2)) + 100
    x0 = int((W - w) / 2); box = (x0, 250, x0 + int(w), 520)
    lay, d, pos, p = card(box)
    cx = p + (box[2] - box[0]) / 2
    d.text((cx, p + 85), l1, font=f1, fill=MARROM, anchor='mm')
    d.text((cx, p + 190), l2, font=f2, fill=DOURADO, anchor='mm')
    d.line((cx - 120, p + 248, cx + 120, p + 248), fill=DOURADO, width=2)
    return lay, pos

def make_tag(top, main):
    f1, f2 = ms(700, 30), pf(600, True, 64)
    tmp = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    top_sp = '  '.join(top)  # caixa alta espaçada
    w = max(tmp.textlength(top_sp, font=f1), tmp.textlength(main, font=f2)) + 110
    x0 = int((W - w) / 2); box = (x0, 1520, x0 + int(w), 1700)
    lay, d, pos, p = card(box)
    cx = p + (box[2] - box[0]) / 2
    d.text((cx, p + 50), top_sp, font=f1, fill=DOURADO, anchor='mm')
    d.text((cx, p + 118), main, font=f2, fill=MARROM, anchor='mm')
    return lay, pos

def make_cta():
    box = (110, 1500, 970, 1720)
    lay, d, pos, p = card(box, fill=BR + (248,))
    d.ellipse((p + 40, p + 60, p + 140, p + 160), fill=(244, 232, 214))
    d.line((p + 65, p + 112, p + 85, p + 132, p + 118, p + 88), fill=DOURADO, width=8, joint='curve')
    d.text((p + 170, p + 62), 'Bora já chamar no WhatsApp', font=pf(700, s=44), fill=MARROM)
    d.text((p + 170, p + 128), 'pra não ficar sem horário! · @materencelash', font=ms(500, 26), fill=(140, 110, 95))
    return lay, pos

def ease(p):
    p = min(max(p, 0), 1); return 1 - (1 - p) ** 3

def place(frame_pil, el, t, t_in, t_out, mode='slide'):
    lay, (x, y) = el
    if t < t_in or t > t_out + 0.2:
        return
    a = 1.0; dy = 0; sc = 1.0
    if t < t_in + 0.3:
        p = ease((t - t_in) / 0.3); a = p
        if mode == 'slide': dy = int(40 * (1 - p))
        else: sc = 0.9 + 0.1 * p
    elif t > t_out:
        p = (t - t_out) / 0.2; a = 1 - p
    im = lay
    if sc != 1.0:
        nw, nh = int(lay.width * sc), int(lay.height * sc)
        im = lay.resize((nw, nh), Image.LANCZOS); x += (lay.width - nw) // 2; y += (lay.height - nh) // 2
    if a < 1:
        im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
    frame_pil.alpha_composite(im, (x, y + dy))

def read_all(path):
    cap = cv2.VideoCapture(path); out = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        out.append(fr)
    return out

def zoom_blur(fr, z, strength):
    """Zoom no centro + desfoque radial (vários zooms somados)."""
    acc = np.zeros(fr.shape, np.float32); n = 6
    for k in range(n):
        zz = z * (1 + strength * k / n)
        M = cv2.getRotationMatrix2D((W / 2, H * 0.42), 0, zz)
        acc += cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return (acc / n).astype(np.uint8)

A = read_all(V + 'a.mov'); D = read_all(V + 'd.mov')
TR = 8  # quadros de cada lado da transição (~0,27 s)
for i in range(TR):
    p = (i + 1) / TR
    A[-TR + i] = zoom_blur(A[-TR + i], 1 + 0.35 * p ** 2, 0.12 * p)
    q = 1 - i / TR
    D[i] = zoom_blur(D[i], 1 + 0.35 * q ** 2, 0.12 * q)
frames = A + D
T_CUT = len(A) / FPS; T_END = len(frames) / FPS

gancho = make_gancho(); antes = make_tag('ANTES', 'Brow Lamination'); depois = make_tag('DEPOIS', 'Brow Lamination'); cta = make_cta()
T_CTA = T_END - 1.6
events = {'whoosh': T_CUT - 0.2, 'pop': T_CUT + 0.35, 'ding': T_CTA}

enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', V + 'video_sem_som.mp4'], stdin=subprocess.PIPE)
for n, fr in enumerate(frames):
    t = n / FPS
    pil = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert('RGBA')
    place(pil, gancho, t, 0.0, T_CUT - 0.35, mode='scale')
    place(pil, antes, t, 0.5, T_CUT - 0.35)
    place(pil, depois, t, T_CUT + 0.25, T_CTA - 0.25)
    place(pil, cta, t, T_CTA, 99)
    enc.stdin.write(cv2.cvtColor(np.array(pil.convert('RGB')), cv2.COLOR_RGB2BGR).tobytes())
enc.stdin.close(); enc.wait()
open(V + 'tempos.txt', 'w').write('%f %f %s\n' % (T_CUT, T_END, ' '.join('%s=%.3f' % kv for kv in events.items())))
print(T_CUT, T_END, events)
