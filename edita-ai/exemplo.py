from PIL import Image, ImageDraw, ImageFont, ImageFilter
F='/home/user/edita-ai/fontes/pk_fontsource-%s.tgz/files/%s.woff'
pf=lambda w,i=False,s=100: ImageFont.truetype(F%('playfair-display-5.3.0','playfair-display-latin-%d-%s'%(w,'italic' if i else 'normal')),s)
ms=lambda w,s: ImageFont.truetype(F%('montserrat-5.3.0','montserrat-latin-%d-normal'%w),s)
FUNDO=(238,225,215); MARROM=(90,53,36); DOURADO=(196,138,58); SALMAO=(216,167,156); BR=(255,255,255)
W,H=1080,1920
im=Image.new('RGB',(W,H),FUNDO)
d=ImageDraw.Draw(im)
# moldura simulando o vídeo
d.rounded_rectangle((90,700,990,1500),radius=28,fill=(214,198,186))
d.text((540,1100),'[ você no vídeo ]',font=ms(500,40),fill=(150,128,115),anchor='mm')
def sombra(txtfn):
    lay=Image.new('RGBA',(W,H),(0,0,0,0)); txtfn(ImageDraw.Draw(lay),(0,0,0,110))
    lay=lay.filter(ImageFilter.GaussianBlur(6)); im.paste(lay,(0,3),lay)
# gancho Manchete
def g(dd,c=None):
    dd.text((540,330),'Seus cílios estão',font=pf(700,s=96),fill=c or MARROM,anchor='mm')
    dd.text((540,450),'ficando capengas?',font=pf(700,True,104),fill=c or DOURADO,anchor='mm')
g(d)
d.line((380,530,700,530),fill=DOURADO,width=2)
# legenda Elegante sobre faixa suave
f1=pf(600,s=64); f2=pf(600,True,64)
parts=[('bora',f1,MARROM),(' chamar no ',f1,MARROM),('WhatsApp',f2,DOURADO)]
tw=sum(d.textlength(t,font=f) for t,f,_ in parts)
x=(W-tw)/2; y=1180
lay=Image.new('RGBA',(W,H),(0,0,0,0)); dl=ImageDraw.Draw(lay)
dl.rounded_rectangle((x-30,y-10,x+tw+30,y+100),radius=14,fill=(255,250,246,235))
im.paste(lay,(0,0),lay); d=ImageDraw.Draw(im)
for t,f,c in parts:
    d.text((x,y+45),t,font=f,fill=c,anchor='lm'); x+=d.textlength(t,font=f)
# cartão E-book da chamada final
d.rounded_rectangle((130,1590,950,1790),radius=28,fill=BR,outline=(232,222,211),width=2)
d.ellipse((190,1640,290,1740),fill=(244,232,214)); d.line((215,1692,235,1712,268,1668),fill=DOURADO,width=8,joint='curve')
d.text((320,1650),'Bora já chamar no WhatsApp',font=pf(700,s=40),fill=MARROM)
d.text((320,1710),'pra não ficar sem horário! · @materencelash',font=ms(500,25),fill=(140,110,95))
im.save('/home/user/Edi-o-de-v-deo-/edita-ai/exemplo_estilo.png')
