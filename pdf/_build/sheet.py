import sys,glob
from PIL import Image
pre=sys.argv[1]; fs=sorted(glob.glob('png/%s-*.png'%pre)); per=int(sys.argv[2]) if len(sys.argv)>2 else 6
for k in range(0,len(fs),per):
    ims=[Image.open(f) for f in fs[k:k+per]]; w,h=ims[0].size; cols=2
    rows=(len(ims)+1)//2; s=Image.new('RGB',(cols*w+10,rows*(h+10)),'white')
    for i,im in enumerate(ims): s.paste(im,((i%cols)*(w+10),(i//cols)*(h+10)))
    s.save('png/sheet_%s_%02d.jpg'%(pre,k//per),quality=85)
print(len(fs))
