# -*- coding: utf-8 -*-
import collections, sys, random
sys.path.insert(0,'scripts')
from room_optimize import RIG, shift

def pool(items, tries=400):
    """随机重启贪心图着色，求近似最少教室数"""
    best=None; bestrooms=None
    base=list(items)
    for t in range(tries):
        order=sorted(base, key=lambda x:(-len(x[1]), random.random())) if t==0 else random.sample(base,len(base))
        rooms=[]
        for c,s in order:
            for i,(used,cls) in enumerate(rooms):
                if not (used & s):
                    used|=s; cls.append(c); break
            else:
                rooms.append([set(s),[c]])
        if best is None or len(rooms)<best:
            best=len(rooms); bestrooms=rooms
    return best,bestrooms

def peak(items):
    cnt=collections.Counter()
    for c,s in items:
        for k in s: cnt[k]+=1
    return max(cnt.values())

groups={
 '全院(校内刚性课)': RIG,
 '2025级+2026级(每周2天)': [(c,s) for c,s in RIG if c['grade'] in ('2025级','2026级')],
 '2024级': [(c,s) for c,s in RIG if c['grade']=='2024级'],
 '2023级': [(c,s) for c,s in RIG if c['grade']=='2023级'],
}
print('%-24s %8s %8s %8s' % ('范围','现用教室','并发峰值','池化最少'))
for name,items in groups.items():
    if not items: continue
    now=len({c['classroom'].strip() for c,s in items})
    n,rooms=pool(items)
    print('%-24s %6d 间 %6d 间 %6d 间' % (name, now, peak(items), n))

print('\n=== 低年级池化后的教室共用方案（25+26级） ===')
items=[(c,s) for c,s in RIG if c['grade'] in ('2025级','2026级')]
n,rooms=pool(items)
for i,(used,cs) in enumerate(rooms,1):
    print(' 教室池#%d: %s' % (i, '；'.join('%s %s(第%d-%d周,周%s)'%(
        c['class_name'],c['course_name'],c['start_week'],c['end_week'],
        ''.join(map(str,c['days_of_week']))) for c in cs)))

print('\n=== 若维持现状，各教室可释放判断 ===')
use=collections.Counter()
for c,s in RIG: use[c['classroom'].strip()]+=len(s)
for r,v in sorted(use.items(), key=lambda x:x[1]):
    print('  %-12s %4d 节次  (%.1f%% of 720)' % (r, v, v/720*100))
