import json, subprocess, numpy as np, cv2
V = '/home/user/edita-ai/v1/'
W, H, FPS = 1080, 1920, 30
J = json.load(open(V + 'olhos.json'))
def eyes(key):
    a = np.array([r[1:5] for r in J[key]], float)
    k = np.ones(5) / 5
    return np.stack([np.convolve(np.pad(a[:, c], 2, mode='edge'), k, 'valid') for c in range(4)], 1)
EA, ED = eyes('a_full.mov'), eyes('d_full.mov')
def read(p):
    cap = cv2.VideoCapture(p); fr = []
    while True:
        ok, f = cap.read()
        if not ok: break
        fr.append(f)
    return fr
A, D = read(V + 'a_full.mov'), read(V + 'd_full.mov')

A0, A1 = 60, 125      # antes: início e fim (fim = fim da fusão)
D0, D1 = 40, 107      # depois: início (= início da fusão) e fim
XF = A1 - 110          # 15 quadros de fusão (0,5 s)
EASE = 20

def geom(e):
    l, r = e[:2], e[2:]
    c = (l + r) / 2; d = r - l
    return c, np.hypot(*d), np.degrees(np.arctan2(d[1], d[0]))
# alvo comum: média dos dois rostos no meio da fusão
ca, da, aa = geom(EA[A1 - XF // 2]); cd, dd, ad = geom(ED[D0 + XF // 2])
TC = (ca + cd) / 2; TD = max(da, dd) * 1.08; TA = (aa + ad) / 2

def M_for(e, w):
    """Transformação que leva os olhos ao alvo, com peso w (0 = sem mexer, 1 = alinhado)."""
    c, d, ang = geom(e)
    s = 1 + w * (TD / d - 1); rot = w * (ang - TA); tc = c + w * (TC - c)
    M = cv2.getRotationMatrix2D(tuple(c), rot, s)
    M[:, 2] += tc - c
    return M
def warp(f, M):
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
def sm(p):
    p = min(max(p, 0), 1); return p * p * (3 - 2 * p)

out = []
xf_a0 = A1 - XF
for i in range(A0, xf_a0):
    w = sm((i - (xf_a0 - EASE)) / EASE)
    out.append(warp(A[i], M_for(EA[i], w)))
for k in range(XF):
    fa = warp(A[xf_a0 + k], M_for(EA[xf_a0 + k], 1)).astype(np.float32)
    fd = warp(D[D0 + k], M_for(ED[D0 + k], 1)).astype(np.float32)
    a = sm((k + 1) / (XF + 1))
    out.append((fa * (1 - a) + fd * a).astype(np.uint8))
for i in range(D0 + XF, D1):
    w = 1 - sm((i - (D0 + XF)) / EASE)
    out.append(warp(D[i], M_for(ED[i], w)))

enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', V + 'fusao_sem_som.mp4'], stdin=subprocess.PIPE)
for f in out: enc.stdin.write(f.tobytes())
enc.stdin.close(); enc.wait()
print(len(out), 'quadros', len(out) / FPS, 's | antes', A0 / FPS, (xf_a0 + XF) / FPS, '| depois', D0 / FPS, D1 / FPS, '| fusão começa em', (xf_a0 - A0) / FPS)
