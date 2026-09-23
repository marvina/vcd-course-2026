# -*- coding: utf-8 -*-
"""分类输出 dashboard 与课程表(26-27-1 PDF) 的不一致清单"""
import json, re, sys, difflib, collections
sys.path.insert(0,'scripts')
import extract_truth
from verify_weeks import norm, class_key

data=json.load(open('schedule_data.json'))
truth=collections.defaultdict(list)
for p in extract_truth.main():
    for row in p['rows']:
        k=class_key(row['class'])
        if k: truth[k].extend(row['cells'])

A=[]; B=[]; C=[]; D=[]
used=collections.defaultdict(set)
for c in data['courses']:
    ck=class_key(c['class_name']); cells=truth.get(ck)
    if not cells:
        C.append((c['class_name'], c['course_name'], '整个班级在课程表中不存在')); continue
    cname=norm(c['course_name'])
    best=None; score=0
    for cell in cells:
        t=norm(cell['text'])
        if not t: continue
        s=difflib.SequenceMatcher(None,cname,t).ratio()
        if cname and cname in t: s=max(s,0.95)
        elif cname and cname[1:] and cname[1:] in t: s=max(s,0.85)   # 首字被列边界截掉
        if s>score: score,best=s,cell
    if not best or score<0.5:
        C.append((c['class_name'], c['course_name'], '该班级下无此课程')); continue
    used[ck].add((best['start_week'],best['end_week']))
    if (best['start_week'],best['end_week'])==(c['start_week'],c['end_week']): continue
    row=(c['class_name'],c['course_name'],c['start_week'],c['end_week'],
         best['start_week'],best['end_week'],best['text'][:44])
    if '考试' in c['course_name'] and '讲座' in c['course_name']:
        B.append(row)
    else:
        A.append(row)

# PDF 有内容、dashboard 没覆盖到的格子
for ck,cells in truth.items():
    for cell in cells:
        if not cell['text'].strip(): continue
        if (cell['start_week'],cell['end_week']) not in used[ck]:
            D.append((ck, cell['start_week'], cell['end_week'], cell['text'][:46]))

W=lambda a,b: '%d-%d'%(a,b) if a!=b else '第%d周'%a
print('【A】周次与课程表不符 —— %d 条' % len(A))
print('%-16s %-22s %-8s %-8s %s' % ('班级','课程','dashboard','课程表','课程表原文'))
for r in sorted(A):
    print('%-16s %-22s %-8s %-8s %s' % (r[0],r[1],W(r[2],r[3]),W(r[4],r[5]),r[6]))

print('\n【B】口径差异，非错误 —— %d 条' % len(B))
print('  dashboard 把「考试周(第19周)」和「学术讲座(第20周)」合并成一条 19-20：')
print('  ' + '、'.join(sorted({r[0] for r in B})))

print('\n【C】dashboard 有、课程表没有 —— %d 条' % len(C))
for r in sorted(C): print('  %-16s %-24s %s' % r)

print('\n【D】课程表有、dashboard 没排到 —— %d 条' % len(D))
for r in sorted(D): print('  %-16s %-8s %s' % (r[0], W(r[1],r[2]), r[3]))
