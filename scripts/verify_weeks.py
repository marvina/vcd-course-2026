# -*- coding: utf-8 -*-
"""把 PDF 几何还原的 ground truth 与 schedule_data.json / index.html 中的 DATA 对比，
输出课程周不一致清单。"""
import json, re, sys, difflib
sys.path.insert(0,'scripts')
import extract_truth

def norm(s):
    return re.sub(r'[\s\(\)（）【】\[\]、,，。.]','',s or '')

ALIAS={
 '23数字媒体25人':'23数字媒体', '23数字媒体':'23数字媒体',
 '23智能交互设计1班':'23智能交互设计班', '23智能交互设计班':'23智能交互设计班',
 '25智能交互设计2':'25智能交互设计2班',
 '包装设计1班517':'26包装设计1班', '包装设计2班518':'26包装设计2班',
 '数字媒体艺术1班513':'26数字媒体艺术1班', '数字媒体艺术1班516':'26数字媒体艺术2班',
 '26智能交互计1班':'26智能交互设计1班', '26智能交互计2班':'26智能交互设计2班',
 '26级印刷1班':'26印刷设计1班', '26级印刷2班':'26印刷设计2班',
 '26级印刷3班':'26印刷设计3班',
}
def class_key(s):
    s=norm(s)
    m=re.search(r'\d{2}[^\d]*?\d*班', s)
    k=m.group(0) if m else s
    if k in ALIAS: return ALIAS[k]
    if '数字媒体' in k and k.startswith('23'): return '23数字媒体'
    return k

def truth_index():
    pages=extract_truth.main()
    idx={}
    for p in pages:
        for row in p['rows']:
            ck=class_key(row['class'])
            if not ck: continue
            idx.setdefault(ck,[]).extend(row['cells'])
    return idx

def main():
    data=json.load(open('schedule_data.json'))
    truth=truth_index()
    bad=[]; nomatch=[]
    for c in data['courses']:
        ck=class_key(c['class_name'])
        cells=truth.get(ck)
        if not cells:
            nomatch.append((c['class_name'],c['course_name'],'班级未在PDF中匹配')); continue
        cname=norm(c['course_name'])
        best=None; score=0
        for cell in cells:
            t=norm(cell['text'])
            if not t: continue
            s=difflib.SequenceMatcher(None,cname,t).ratio()
            if cname and (cname in t or t.startswith(cname[:4])): s=max(s,0.9)
            if s>score: score,best=s,cell
        if not best or score<0.35:
            nomatch.append((c['class_name'],c['course_name'],'课程未在PDF中匹配')); continue
        if (best['start_week'],best['end_week'])!=(c['start_week'],c['end_week']):
            bad.append({'class':c['class_name'],'course':c['course_name'],
                        'dashboard':[c['start_week'],c['end_week']],
                        'pdf':[best['start_week'],best['end_week']],
                        'pdf_text':best['text'][:50],'match':round(score,2),'id':c['id']})
    print('课程总数 %d｜周次不一致 %d｜未匹配 %d'%(len(data['courses']),len(bad),len(nomatch)))
    print('\n--- 周次不一致（dashboard -> 课程表） ---')
    for b in bad:
        print('%-18s %-22s %2d-%-2d -> %2d-%-2d  [%.2f] %s'%(
            b['class'],b['course'],b['dashboard'][0],b['dashboard'][1],
            b['pdf'][0],b['pdf'][1],b['match'],b['pdf_text']))
    print('\n--- 未匹配 ---')
    for n in nomatch: print('%-18s %-22s %s'%n)
    json.dump({'mismatch':bad,'unmatched':nomatch},open('week_diff.json','w'),ensure_ascii=False,indent=1)

main()
