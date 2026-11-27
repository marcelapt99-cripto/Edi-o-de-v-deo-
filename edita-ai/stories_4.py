import sys, math
sys.argv = ['x']
exec(open('/home/user/edita-ai/scripts/stories.py').read())

def story4():
    base = fundo()
    arv, taca = emoji('🎄', 46), emoji('🥂', 46)
    def topo(d, l):
        d.text((W / 2, 300), 'D I S P O N I B I L I D A D E', font=ms(700, 30), fill=DOURADO, anchor='mm')
        d.text((W / 2, 395), 'Últimos horários', font=pf(700, s=84), fill=MARROM, anchor='mm')
        d.text((W / 2, 490), 'de fim de ano', font=pf(700, True, 84), fill=DOURADO, anchor='mm')
    T = layer(topo)
    semanas = [('Semana do Natal', arv, 600, [('SEG', '21', 1), ('TER', '22', 0), ('QUA', '23', 0)]),
               ('Semana do Ano Novo', taca, 1000, [('SEG', '28', 2), ('TER', '29', 3), ('QUA', '30', 1)])]
    CW, CH, GAP = 270, 270, 35
    X0 = (W - (3 * CW + 2 * GAP)) // 2
    titulos, cards, carimbos = [], [], []
    for nome, em, y, dias in semanas:
        def tit(d, l, nome=nome, em=em, y=y):
            f = pf(700, True, 52); w = d.textlength(nome, font=f); x = W / 2 - (w + 60) / 2
            d.text((x, y + 30), nome, font=f, fill=MARROM, anchor='lm'); l.alpha_composite(em, (int(x + w + 14), y + 30 - em.height // 2))
        titulos.append(layer(tit))
        for k, (dw, dn, livres) in enumerate(dias):
            x = X0 + k * (CW + GAP); yy = y + 80
            def card(d, l, x=x, yy=yy, dw=dw, dn=dn, livres=livres):
                cheio = livres == 0
                sombra_card(l, (x, yy, x + CW, yy + CH), r=28, fill=((246, 240, 235, 255) if cheio else BR + (255,)))
                d = ImageDraw.Draw(l)
                d.rounded_rectangle((x, yy, x + CW, yy + 62), 28, fill=(DCLARO if not cheio else BEGE) + (255,))
                d.rectangle((x, yy + 34, x + CW, yy + 62), fill=(DCLARO if not cheio else BEGE) + (255,))
                d.text((x + CW / 2, yy + 33), dw, font=ms(700, 28), fill=MARROM if not cheio else SUAVE, anchor='mm')
                d.text((x + CW / 2, yy + 125), dn, font=pf(700, s=78), fill=MARROM if not cheio else (190, 170, 158), anchor='mm')
                if not cheio:
                    for j in range(livres):     # bolinhas = horários livres
                        cx = x + CW / 2 + (j - (livres - 1) / 2) * 34
                        d.ellipse((cx - 11, yy + 182, cx + 11, yy + 204), fill=DOURADO)
                    t = '%d horário%s' % (livres, '' if livres == 1 else 's')
                    d.text((x + CW / 2, yy + 236), t, font=ms(600, 28), fill=DOURADO, anchor='mm')
            cards.append(layer(card))
            if livres == 0:
                def car(d, l, x=x, yy=yy):
                    st = Image.new('RGBA', (232, 84), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
                    ds.rounded_rectangle((6, 6, 226, 78), 9, outline=(178, 84, 60, 235), width=6)
                    ds.text((116, 43), 'ESGOTADO', font=ms(800, 36), fill=(178, 84, 60, 235), anchor='mm')
                    st = st.rotate(-8 * -1, expand=True, resample=Image.BICUBIC)
                    l.alpha_composite(st, (int(x + CW / 2 - st.width / 2), int(yy + 205 - st.height / 2)))
                carimbos.append((layer(car), (x + CW / 2, yy + 205)))
    corre = layer(lambda d, l: (d.text((W / 2, 1450), 'Corre que tá acabando!', font=pf(700, True, 64), fill=DOURADO, anchor='mm'),
                                d.text((W / 2, 1530), 'horários combinados pelo WhatsApp', font=ms(500, 32), fill=SUAVE, anchor='mm')))
    def fr(t):
        im = base.copy(); put(im, T, ease(t / 0.4), dy=-20 * (1 - ease(t / 0.4)))
        for s_, tl in enumerate(titulos):
            p = ease((t - 0.4 - s_ * 1.0) / 0.35); put(im, tl, p, dy=25 * (1 - p))
        for k, c in enumerate(cards):
            t0 = 0.6 + (k // 3) * 1.0 + (k % 3) * 0.15; p = ease((t - t0) / 0.35); put(im, c, p, dy=40 * (1 - p))
        for k, (c, ctr) in enumerate(carimbos):   # carimbo: 1,6 -> 0,95 -> 1,0
            t0 = 2.4 + k * 0.35; u = (t - t0) / 0.18
            if u > 0:
                sc = 1.6 - 0.65 * min(u, 1) if u < 1 else 0.95 + 0.05 * min((u - 1) * 0.18 / 0.08, 1)
                put(im, c, min(1, u * 1.5), sc=sc, center=ctr)
        p = ease((t - 3.4) / 0.4); put(im, corre, p, dy=30 * (1 - p))
        return im
    encode('story4', fr, 7 * FPS, sfx=[('whoosh', 0.4), ('pop', 0.6), ('pop', 1.6), ('impacto', 2.4), ('impacto', 2.75), ('ding', 3.4)])

story4()
