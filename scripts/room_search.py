# -*- coding: utf-8 -*-
"""搜索最优「年级上课日」组合：最小化并发教室峰值"""
import itertools, collections, sys
sys.path.insert(0,'scripts')
from room_optimize import RIG, shift, concurrency, pool

def days_of(grade):
    ds=set()
    for c,s in RIG:
        if c['grade']==grade: ds|={k[1] for k in s}
    return sorted(ds)

grades=sorted({c['grade'] for c,s in RIG})
print('各年级现用上课日:')
cur={}
for g in grades:
    cur[g]=days_of(g); print('  %-10s %s' % (g, cur[g]))

MOVE=['2024级','2025级','2026级']
opts={}
for g in MOVE:
    n=len(cur[g])
    opts[g]=[tuple(sorted(c)) for c in itertools.combinations(range(1,6), n)]

def evaluate(assign):
    items=[]
    for c,s in RIG:
        g=c['grade']
        if g in assign:
            mp=dict(zip(cur[g], assign[g]))
            items.append(shift(s, mp))
        else: items.append(s)
    cnt=concurrency(items)
    peak=max(cnt.values())
    byday={dd: max([v for (w,d2,p),v in cnt.items() if d2==dd] or [0]) for dd in range(1,6)}
    return peak, byday, items

best=[]
for a24 in opts['2024级']:
    for a25 in opts['2025级']:
        for a26 in opts['2026级']:
            assign={'2024级':a24,'2025级':a25,'2026级':a26}
            peak,byday,items=evaluate(assign)
            best.append((peak,sum(sorted(byday.values())[-2:]),assign,byday))
best.sort(key=lambda x:(x[0],x[1]))
print('\n现状峰值:', evaluate({})[0])
print('\n最优 12 组（峰值 / 各日峰值）:')
seen=set()
for peak,sec,assign,byday in best[:12]:
    print('  峰值%2d  24级%s 25级%s 26级%s   各日峰值 %s' %
          (peak, assign['2024级'], assign['2025级'], assign['2026级'],
           [byday[d] for d in range(1,6)]))
# 保守方案：只动 25 级
print('\n只调整 25 级（24/26 级不变）:')
res=[]
for a25 in opts['2025级']:
    peak,byday,_=evaluate({'2025级':a25})
    res.append((peak,a25,byday))
res.sort()
for peak,a25,byday in res[:6]:
    print('  峰值%2d  25级→周%s  各日峰值 %s' % (peak, a25, [byday[d] for d in range(1,6)]))
