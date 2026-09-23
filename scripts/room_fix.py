# -*- coding: utf-8 -*-
"""为每处真实教室冲突，给出该时段仍然空闲的教室"""
import collections, sys
sys.path.insert(0,'scripts')
from room_optimize import RIG

ALL_ROOMS=sorted({c['classroom'].strip() for c,s in RIG})
# 普通教学教室（可互换），排除专用工作室/实验室
def generic(r):
    return r.endswith('教室') and '包装工程' not in r

busy=collections.defaultdict(set)      # slot -> rooms in use
who=collections.defaultdict(list)
for c,s in RIG:
    for k in s:
        busy[k].add(c['classroom'].strip()); who[k].append(c)

slot_conf=collections.defaultdict(set)
for k,cs in who.items():
    byroom=collections.defaultdict(set)
    for c in cs: byroom[c['classroom'].strip()].add(c['class_name'])
    for r,names in byroom.items():
        if len(names)>1: slot_conf[(r,tuple(sorted(names)))].add(k)

print('=== 冲突处置建议（该时段空闲的普通教室） ===')
for (r,names),slots in sorted(slot_conf.items(), key=lambda x:-len(x[1])):
    ws=sorted({k[0] for k in slots}); ds=sorted({k[1] for k in slots})
    free=None
    for k in slots:
        f={x for x in ALL_ROOMS if generic(x) and x not in busy[k]}
        free = f if free is None else (free & f)
    print('\n  ✗ %s：%s  第%s周 周%s' % (r, ' / '.join(names), ','.join(map(str,ws)), ','.join(map(str,ds))))
    print('    全时段空闲可调剂: %s' % ('、'.join(sorted(free)) if free else '无（需跨时段调整）'))

print('\n=== 每天各节次的空闲普通教室数（第1-18周平均） ===')
gen=[r for r in ALL_ROOMS if generic(r)]
print('  普通教室总数 %d 间' % len(gen))
for day in range(1,6):
    row=[]
    for p in range(1,9):
        used=[len({r for r in busy[(w,day,p)] if generic(r)}) for w in range(1,19)]
        row.append('%.0f'%(len(gen)-sum(used)/18))
    print('  周%d 各节空闲: %s' % (day, ' '.join('%2s'%x for x in row)))
