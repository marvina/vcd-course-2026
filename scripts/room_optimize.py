# -*- coding: utf-8 -*-
"""教室安排优化仿真（只针对"刚性课堂"：有明确节次的常规授课）"""
import json, re, collections, sys
d=json.load(open('schedule_data.json'))
C=d['courses']

def is_campus(r):
    r=(r or '').strip()
    return bool(r) and not any(k in r for k in ('青岛基地','考察基地','外出','操场','长清','报告厅','公选机房'))

def periods(desc):
    m=re.match(r'(\d+)\s*-\s*(\d+)\s*节', desc or '')
    if m: return set(range(int(m.group(1)), min(int(m.group(2)),8)+1))
    return None          # 非刚性（导师指导/全周实践/军训等）

def rigid(c):
    """返回 (week,day,period) 集合；非刚性课程返回空"""
    s=set()
    for w in range(c['start_week'], c['end_week']+1):
        if w>18: continue
        for day in c['days_of_week']:
            ps=periods((c['periods_map'] or {}).get(str(day)))
            if ps:
                for p in ps: s.add((w,day,p))
    return s

RIG=[(c, rigid(c)) for c in C if is_campus(c['classroom'])]
RIG=[(c,s) for c,s in RIG if s]
print('刚性课堂课程 %d 门 / 校内课程 %d 门' % (len(RIG), sum(1 for c in C if is_campus(c['classroom']))))

def shift(s, mapping):
    return {(w, mapping.get(day,day), p) for (w,day,p) in s}

def concurrency(items):
    cnt=collections.Counter()
    for s in items:
        for k in s: cnt[k]+=1
    return cnt

def report(tag, items):
    cnt=concurrency(items)
    peak=max(cnt.values()); tot=sum(cnt.values())
    byday=collections.defaultdict(list)
    for (w,dd,p),v in cnt.items(): byday[dd].append(v)
    print('%-20s 峰值 %2d 间｜需求 %5d 节次｜%s' % (tag, peak, tot,
        ' '.join('周%d 均%4.1f/峰%2d'%(dd, sum(byday[dd])/(18*8), max(byday[dd]) if byday[dd] else 0) for dd in range(1,6))))
    return peak

def pool(items_with_meta):
    """图着色式贪心：把课程分配到共享教室池，返回所需教室数"""
    order=sorted(items_with_meta, key=lambda x:-len(x[1]))
    rooms=[]
    for c,s in order:
        for used in rooms:
            if not (used & s):
                used|=s; break
        else:
            rooms.append(set(s))
    return len(rooms)

base=[s for c,s in RIG]
print('\n=== A. 错峰方案对比（刚性课堂） ===')
report('现状', base); 
SC={'2025级':{1:3,2:4}}   # 25级 周一二 -> 周三四
SC2={'2024级':{1:2}}      # 24级 周一 -> 周二
plans={
 '①25级→周三四': {'2025级':{1:3,2:4}},
 '②25级→周二三': {'2025级':{1:2,2:3}},
 '③24级周一→周四': {'2024级':{1:4}},
 '④25级→周三四+24级周一→周二': {'2025级':{1:3,2:4},'2024级':{1:2}},
 '⑤25级→周二三+24级周一→周四': {'2025级':{1:2,2:3},'2024级':{1:4}},
}
for name,mp in plans.items():
    report(name, [shift(s, mp.get(c['grade'],{})) for c,s in RIG])

print('\n=== B. 教室池化（共享教室）所需间数 ===')
print('  现状固定教室制实际占用: %d 间' % len({c['classroom'].strip() for c,s in RIG}))
print('  池化后(现状课表): %d 间' % pool(RIG))
for name,mp in plans.items():
    print('  池化后(%s): %d 间' % (name, pool([(c, shift(s, mp.get(c['grade'],{}))) for c,s in RIG])))

print('\n=== C. 真实教室冲突（同一常规教室、同一节次、不同班级） ===')
slot=collections.defaultdict(set)
for c,s in RIG:
    for k in s: slot[(c['classroom'].strip(),)+k].add(c['class_name'])
bad=collections.defaultdict(set)
for k,v in slot.items():
    if len(v)>1: bad[(k[0], tuple(sorted(v)))].add(k[1])
for (r,names),ws in sorted(bad.items(), key=lambda x:-len(x[1])):
    print('  %-12s %-34s 第%s周' % (r,'/'.join(names), ','.join(map(str,sorted(ws)))))
if not bad: print('  无')
