# -*- coding: utf-8 -*-
"""从课程表 PDF 几何还原 ground truth：每个班级每门课的起止教学周。
原理：表头行的竖线定义 20 个教学周的 x 区间；每个班级行内的竖线定义单元格边界；
单元格 [x0,x1] 覆盖哪些周列 -> start_week / end_week。全程无人工判读。
"""
import sys, json, collections, re
sys.path.insert(0,'scripts')
from pdf_extract import load, objects, build_fonts, page_resources, extract

TOL = 1.2

def cluster(vals, tol=TOL):
    vals=sorted(vals); out=[]
    for v in vals:
        if out and v-out[-1][-1]<=tol: out[-1].append(v)
        else: out.append([v])
    return [sum(g)/len(g) for g in out]

def build_page(texts, lines):
    H=[l for l in lines if abs(l[1]-l[3])<0.6 and abs(l[0]-l[2])>40]
    V=[l for l in lines if abs(l[0]-l[2])<0.6 and abs(l[1]-l[3])>8]
    # 表头行：最高的两条长横线之间（周次/日期行）
    ys=sorted({round(l[1],2) for l in H}, reverse=True)
    head_top, head_bot = ys[0], None
    # 表头下边界 = 覆盖整表宽度、且下面开始出现班级行的横线
    # 取第三条长横线（周次线、日期线、表头底线）
    long_h=sorted(H, key=lambda l: -l[1])
    ys3 = sorted({round(l[1],2) for l in H}, reverse=True)
    head_top, head_mid, head_bot = ys3[0], ys3[1], ys3[2]
    # 表头竖线 -> 周列边界
    hv=[l for l in V if min(l[1],l[3])<head_bot+2 and max(l[1],l[3])>head_bot+8]
    xs=cluster([l[0] for l in hv])
    return H,V,head_bot,head_mid,head_top,xs

def week_cols(xs, texts, head_mid, head_top):
    """把表头 x 区间映射到周号：只读表头最上面的“周次”行。"""
    cols=[]
    for i in range(len(xs)-1):
        x0,x1=xs[i],xs[i+1]
        lab=''.join(t[2] for t in sorted([t for t in texts
                    if x0+0.5<t[0]<x1-0.5 and head_mid+1 < t[1] < head_top-0.5],
                    key=lambda t:t[0]))
        cols.append((x0,x1,lab))
    return cols

def date_cols(xs, texts, head_bot, head_mid):
    """日期行每格 = 1 个教学周，按 x 从左到右即第 1..20 周。"""
    cols=[]
    for i in range(len(xs)-1):
        x0,x1=xs[i],xs[i+1]
        lab=''.join(t[2] for t in sorted([t for t in texts
                    if x0+0.5<t[0]<x1-0.5 and head_bot+1 < t[1] < head_mid-0.5],
                    key=lambda t:(-t[1],t[0])))
        cols.append((x0,x1,lab))
    return cols

def parse_weeks(lab):
    import re
    ns=[int(n) for n in re.findall(r'\d+', lab)]
    ns=[n for n in ns if 1<=n<=20]
    if not ns: return None
    return (min(ns), max(ns))

def main(pdf='2026-2027-1.pdf'):
    raw=load(pdf); objs=objects(raw); fonts=build_fonts(raw,objs)
    result=[]
    for pi,(num,content,res) in enumerate(page_resources(objs)):
        if not content: continue
        texts,lines,rects=extract(content,res,fonts)
        H,V,head_bot,head_mid,head_top,xs=build_page(texts,lines)
        dcols=[c for c in date_cols(xs,texts,head_bot,head_mid) if '-' in c[2] and '.' in c[2]]
        if len(dcols)<15: continue
        wk=[(x0,x1,(i+1,i+1)) for i,(x0,x1,lab) in enumerate(dcols)]
        wkdates=[lab for _,_,lab in dcols]
        x_left=wk[0][0]
        # 班级行：head_bot 以下的长横线
        rowys=[head_bot]+sorted({round(l[1],2) for l in H if l[1]<head_bot-2}, reverse=True)
        rows=[(rowys[i],rowys[i+1]) for i in range(len(rowys)-1)]
        page={'page':pi,'week_dates':wkdates,'rows':[]}
        for ytop,ybot in rows:
            if ytop-ybot<6: continue
            # 班级名：x_left 左侧最近一列
            cls=''.join(t[2] for t in sorted([t for t in texts if ybot<t[1]<ytop and x_left-62<t[0]<x_left-1],
                                             key=lambda t:(-t[1],t[0])))
            # 该行的竖线
            rv=[l for l in V if min(l[1],l[3])<ytop-3 and max(l[1],l[3])>ybot+3 and l[0]>=x_left-1]
            bx=cluster([l[0] for l in rv]+[x_left, wk[-1][1]])
            cells=[]
            for i in range(len(bx)-1):
                x0,x1=bx[i],bx[i+1]
                if x1-x0<4: continue
                txt=''.join(t[2] for t in sorted([t for t in texts if ybot<t[1]<ytop and x0+0.5<t[0]<x1-0.5],
                                                 key=lambda t:(-t[1],t[0])))
                covered=[w for a,b,w in wk
                         if (min(b,x1)-max(a,x0)) > 0.5*(b-a)]
                if not covered: continue
                sw=min(w[0] for w in covered); ew=max(w[1] for w in covered)
                cells.append({'start_week':sw,'end_week':ew,'text':txt.strip(),
                              'x':[round(x0,1),round(x1,1)]})
            if not cells: continue
            cls=cls.strip()
            probe = re.sub(r'【[^】]*】|\d+人|\d{3}|青岛基地|长清校区|考察基地', '', cls)
            has_name = bool(re.search(r'[\u4e00-\u9fa5]{2,}', probe))
            if has_name:
                page['rows'].append({'class':cls,'cells':cells})
            elif page['rows']:
                prev=page['rows'][-1]
                merged={(c['start_week'],c['end_week']):c for c in prev['cells']}
                for c in cells:
                    k=(c['start_week'],c['end_week'])
                    if k in merged:
                        if len(c['text'])>len(merged[k]['text']):
                            merged[k]['text']=c['text'] if not merged[k]['text'] else merged[k]['text']+c['text']
                        else:
                            merged[k]['text']+=c['text']
                    else:
                        merged[k]=c
                prev['cells']=[merged[k] for k in sorted(merged)]
        result.append(page)
    return result

if __name__=='__main__':
    r=main(sys.argv[1] if len(sys.argv)>1 else '2026-2027-1.pdf')
    json.dump(r, open('truth_cells.json','w'), ensure_ascii=False, indent=1)
    for p in r:
        print('=== page',p['page'],'weeks',len(p['week_dates']),'rows',len(p['rows']))
        for row in p['rows']:
            print(' ',row['class'])
            for c in row['cells']:
                print('    W%02d-%02d | %s'%(c['start_week'],c['end_week'],c['text'][:60]))
