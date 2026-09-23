# -*- coding: utf-8 -*-
"""教室使用分析：占用模型 -> 冲突、利用率、空闲、班级-教室绑定度"""
import json, re, collections, sys

d=json.load(open('schedule_data.json'))
C=d['courses']

OFFSITE=('青岛基地','考察基地','外出','操场','长清校区','学术报告厅','专业教室/公选机房','')
def is_campus(r):
    r=r.strip()
    if not r: return False
    return not any(k in r for k in ('青岛基地','考察基地','外出','操场','长清','报告厅','公选机房'))

def periods(desc):
    if not desc: return set()
    m=re.match(r'(\d+)\s*-\s*(\d+)\s*节', desc)
    if m: return set(range(int(m.group(1)), int(m.group(2))+1))
    if '全天' in desc: return set(range(1,9))
    return set(range(1,9))   # 全周实践/导师指导等按全天计

occ=collections.defaultdict(list)   # (room, week, day, period) -> [course]
room_slots=collections.Counter()
for c in C:
    r=c['classroom'].strip()
    for w in range(c['start_week'], c['end_week']+1):
        for day in c['days_of_week']:
            ps=periods((c['periods_map'] or {}).get(str(day)))
            for p in ps:
                occ[(r,w,day,p)].append(c)
                room_slots[r]+=1

# 1. 冲突
conf=collections.defaultdict(set)
for k,v in occ.items():
    if len(v)>1:
        names={x['class_name'] for x in v}
        if len(names)>1:
            conf[(k[0], tuple(sorted(names)))].add((k[1],k[2],k[3]))

# 2. 校内教室利用率（第1-18周，周一至周五，1-8节）
CAP=18*5*8
campus=sorted({c['classroom'].strip() for c in C if is_campus(c['classroom'])})
util=[]
for r in campus:
    used=len({(w,day,p) for (rr,w,day,p) in occ if rr==r and w<=18})
    util.append((r, used, used/CAP))

# 3. 班级 -> 教室数；教室 -> 班级数
cls_rooms=collections.defaultdict(set); room_cls=collections.defaultdict(set)
for c in C:
    r=c['classroom'].strip()
    if is_campus(r):
        cls_rooms[c['class_name']].add(r); room_cls[r].add(c['class_name'])

# 4. 每周校内在校班级数 vs 教室需求
week_need=collections.defaultdict(set)
for c in C:
    for w in range(c['start_week'], c['end_week']+1):
        if is_campus(c['classroom']): week_need[w].add((c['class_name'], c['classroom'].strip()))

if __name__=='__main__':
    print('=== 1. 教室冲突（同教室同节次两个班） ===')
    if not conf: print('  无')
    for (r,names),slots in sorted(conf.items(), key=lambda x:-len(x[1])):
        ws=sorted({s[0] for s in slots})
        print('  %-12s %-30s 周%s 共%d个节次' % (r, '/'.join(names), ws, len(slots)))

    print('\n=== 2. 校内教室利用率（第1-18周 / 5天 / 8节 = %d 节次） ===' % CAP)
    for r,used,u in sorted(util, key=lambda x:-x[2]):
        bar='█'*int(u*40)
        print('  %-12s %4d 节  %5.1f%%  %s  班级:%s' % (r, used, u*100, bar, '、'.join(sorted(room_cls[r])) or '-'))
    tot=sum(u[1] for u in util)
    print('  --- 合计 %d 间教室，平均利用率 %.1f%%' % (len(util), tot/(len(util)*CAP)*100))

    print('\n=== 3. 班级换教室次数（校内） ===')
    for cl,rs in sorted(cls_rooms.items(), key=lambda x:-len(x[1])):
        if len(rs)>1: print('  %-18s %d 间: %s' % (cl, len(rs), '、'.join(sorted(rs))))
    single=[c for c,rs in cls_rooms.items() if len(rs)==1]
    print('  固定单一教室的班级: %d 个' % len(single))

    print('\n=== 4. 教室被几个班共用 ===')
    for r,cs in sorted(room_cls.items(), key=lambda x:-len(x[1])):
        print('  %-12s %d 班: %s' % (r, len(cs), '、'.join(sorted(cs))))

    print('\n=== 5. 每周校内教室占用数 ===')
    for w in range(1,21):
        rooms={r for (cl,r) in week_need[w]}
        print('  第%2d周: %2d 间教室 / %2d 个班级课程' % (w, len(rooms), len(week_need[w])))

def part2():
    print('\n=== 6. 并发需求：每(周,天,节)同时占用的校内教室数 ===')
    conc=collections.Counter()
    for (r,w,day,p) in occ:
        if is_campus(r) and w<=18: conc[(w,day,p)]+=1
    peak=max(conc.values()); 
    print('  峰值同时占用 %d 间；现有校内教室 %d 间' % (peak, len(campus)))
    dist=collections.Counter(conc.values())
    for k in sorted(dist): print('    同时占用 %2d 间的节次数: %d' % (k,dist[k]))
    # 按星期几
    print('\n  按星期分布（第1-18周，平均同时占用教室数 / 峰值）:')
    for day in range(1,6):
        vals=[v for (w,dd,p),v in conc.items() if dd==day]
        allslots=18*8
        print('    周%d  平均%.1f 间  峰值%d 间  有课节次占比 %.0f%%' %
              (day, sum(vals)/allslots, max(vals) if vals else 0, len(vals)/allslots*100))
    # 按节次
    print('\n  按节次分布:')
    for p in range(1,9):
        vals=[v for (w,dd,pp),v in conc.items() if pp==p]
        print('    第%d节  平均%.1f 间  峰值%d 间' % (p, sum(vals)/(18*5), max(vals) if vals else 0))
    # 理论最少教室
    total=sum(conc.values())
    print('\n  校内总需求 %d 教室·节次；按 18周×5天×8节=720 计，理论最少教室 = %.1f 间' % (total, total/720))
    print('  当前使用 %d 间 -> 冗余 %.0f%%' % (len(campus), (len(campus)-total/720)/len(campus)*100))

    print('\n=== 7. 每班每周上课天数（固定教室制的利用率天花板） ===')
    per=collections.defaultdict(set)
    for c in C:
        if is_campus(c['classroom']):
            for w in range(c['start_week'],c['end_week']+1):
                for day in c['days_of_week']: per[(c['class_name'],w)].add(day)
    byc=collections.defaultdict(list)
    for (cl,w),ds in per.items(): byc[cl].append(len(ds))
    for cl,v in sorted(byc.items()):
        print('  %-18s 平均每周 %.1f 天上课（占5天的 %.0f%%）' % (cl, sum(v)/len(v), sum(v)/len(v)/5*100))

    print('\n=== 8. 班级规模 vs 教室 ===')
    seen={}
    for c in C:
        if is_campus(c['classroom']):
            seen.setdefault(c['classroom'].strip(),set()).add((c['class_name'],c['students_count']))
    for r,s in sorted(seen.items()):
        print('  %-12s %s' % (r, '、'.join('%s(%s人)'%x for x in sorted(s))))

part2()
