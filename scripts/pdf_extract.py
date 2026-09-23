# -*- coding: utf-8 -*-
"""纯标准库 PDF 解析：抽取课程表 PDF 中的文字(带坐标)与线条/矩形几何。
用途：从 2026-2027-1.pdf 还原每个单元格的横向跨度 -> 课程起止周(ground truth)。
"""
import re, zlib, sys, json, collections

def load(path):
    return open(path,'rb').read()

def objects(raw):
    out={}
    for m in re.finditer(rb'(\d+)\s+0\s+obj(.*?)endobj', raw, re.S):
        out[int(m.group(1))]=m.group(2)
    return out

def stream_of(body):
    i=body.find(b'stream')
    if i<0: return None
    data=body[i+6:]
    data=data.lstrip(b'\r\n')
    j=data.rfind(b'endstream')
    if j>=0: data=data[:j]
    try: return zlib.decompress(data)
    except Exception:
        try: return zlib.decompressobj().decompress(data)
        except Exception: return None

def parse_tounicode(cmap_bytes):
    m={}
    txt=cmap_bytes.decode('latin-1')
    for blk in re.findall(r'beginbfchar(.*?)endbfchar', txt, re.S):
        for src,dst in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            m[int(src,16)]=''.join(chr(int(dst[i:i+4],16)) for i in range(0,len(dst),4))
    for blk in re.findall(r'beginbfrange(.*?)endbfrange', txt, re.S):
        for lo,hi,dst in re.findall(r'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            lo,hi=int(lo,16),int(hi,16); base=int(dst,16)
            for k in range(lo,hi+1):
                m[k]=chr(base+(k-lo))
    return m

def build_fonts(raw, objs):
    """returns {fontname: {cid:char}} by scanning all font objects globally."""
    fonts={}
    for num,body in objs.items():
        if b'/Type0' not in body and b'/Type1' not in body and b'/TrueType' not in body: continue
        tu=re.search(rb'/ToUnicode\s+(\d+)\s+0\s+R', body)
        if not tu: continue
        cm=stream_of(objs.get(int(tu.group(1)),b'')) or b''
        fonts[num]=parse_tounicode(cm)
    return fonts

def page_resources(objs):
    """map: page index -> (content stream bytes, {resname: fontobjnum})"""
    pages=[]
    for num,body in objs.items():
        if b'/Type/Page' in body.replace(b' ',b'') and b'/Contents' in body:
            pages.append((num,body))
    def key(nb):
        return nb[0]
    pages.sort(key=key)
    out=[]
    for num,body in pages:
        cm=re.search(rb'/Contents\s+(\d+)\s+0\s+R', body)
        content=stream_of(objs.get(int(cm.group(1)),b'')) if cm else None
        res={}
        rm=re.search(rb'/Resources\s+(\d+)\s+0\s+R', body)
        rbody = objs.get(int(rm.group(1)),b'') if rm else body
        fm=re.search(rb'/Font\s*<<(.*?)>>', rbody, re.S)
        if fm:
            for name,onum in re.findall(rb'/([A-Za-z0-9]+)\s+(\d+)\s+0\s+R', fm.group(1)):
                res[name.decode()]=int(onum)
        else:
            fr=re.search(rb'/Font\s+(\d+)\s+0\s+R', rbody)
            if fr:
                fb=objs.get(int(fr.group(1)),b'')
                for name,onum in re.findall(rb'/([A-Za-z0-9]+)\s+(\d+)\s+0\s+R', fb):
                    res[name.decode()]=int(onum)
        out.append((num,content,res))
    return out

NUM=r'[-+]?[0-9]*\.?[0-9]+'
def extract(content, res, fonts):
    """returns texts=[(x,y,str)], lines=[(x0,y0,x1,y1)], rects=[(x,y,w,h)]"""
    texts=[]; lines=[]; rects=[]
    ctm=[1,0,0,1,0,0]; stack=[]
    cur_font=None; tm=None; size=1
    # tokenise roughly line by line
    s=content.decode('latin-1')
    tokens=re.finditer(r'<([0-9A-Fa-f]+)>\s*Tj|'
                       r'/([A-Za-z0-9]+)\s+('+NUM+r')\s+Tf|'
                       r'('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s+Tm|'
                       r'('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s+cm|'
                       r'('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s+('+NUM+r')\s+re|'
                       r'('+NUM+r')\s+('+NUM+r')\s+m|'
                       r'('+NUM+r')\s+('+NUM+r')\s+l|'
                       r'(q)|(Q)|(ET)|(BT)|('+NUM+r')\s+('+NUM+r')\s+TD', s)
    def apply(m,x,y):
        a,b,c,d,e,f=m
        return (a*x+c*y+e, b*x+d*y+f)
    def mul(m1,m2):
        a1,b1,c1,d1,e1,f1=m1; a2,b2,c2,d2,e2,f2=m2
        return (a1*a2+b1*c2, a1*b2+b1*d2, c1*a2+d1*c2, c1*b2+d1*d2, e1*a2+f1*c2+e2, e1*b2+f1*d2+f2)
    ctm=(1,0,0,1,0,0)
    curpt=(0,0)
    pending=collections.defaultdict(str)
    for t in tokens:
        g=t.groups()
        if g[0] is not None:
            hexs=g[0]
            cmap=fonts.get(res.get(cur_font,-1),{})
            chars=''
            for i in range(0,len(hexs),4):
                cid=int(hexs[i:i+4],16)
                chars+=cmap.get(cid, '')
            if tm:
                full=mul(tm,ctm)
                x,y=full[4],full[5]
                texts.append((round(x,2),round(y,2),chars))
        elif g[1] is not None:
            cur_font=g[1]; size=float(g[2])
        elif g[3] is not None:
            tm=tuple(float(v) for v in g[3:9])
        elif g[9] is not None:
            ctm=mul(tuple(float(v) for v in g[9:15]), ctm)
        elif g[15] is not None:
            x,y,w,h=[float(v) for v in g[15:19]]
            p0=apply(ctm,x,y); p1=apply(ctm,x+w,y+h)
            rects.append((round(min(p0[0],p1[0]),2),round(min(p0[1],p1[1]),2),
                          round(abs(p1[0]-p0[0]),2),round(abs(p1[1]-p0[1]),2)))
        elif g[19] is not None:
            curpt=apply(ctm,float(g[19]),float(g[20]))
        elif g[21] is not None:
            p=apply(ctm,float(g[21]),float(g[22]))
            lines.append((round(curpt[0],2),round(curpt[1],2),round(p[0],2),round(p[1],2)))
            curpt=p
        elif g[23] is not None:
            stack.append(ctm)
        elif g[24] is not None:
            if stack: ctm=stack.pop()
        elif g[27] is not None:
            if tm:
                dx,dy=float(g[27]),float(g[28])
                tm=mul((1,0,0,1,dx,dy),tm)
    return texts,lines,rects

if __name__=='__main__':
    path=sys.argv[1] if len(sys.argv)>1 else '2026-2027-1.pdf'
    raw=load(path); objs=objects(raw); fonts=build_fonts(raw,objs)
    for idx,(num,content,res) in enumerate(page_resources(objs)):
        if not content: continue
        texts,lines,rects=extract(content,res,fonts)
        print('=== page obj',num,'texts',len(texts),'lines',len(lines),'rects',len(rects))
        for t in texts[:15]: print(t)
        print('lines sample',lines[:10])
        print('rects sample',rects[:10])
