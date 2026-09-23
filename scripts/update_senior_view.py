import re

def main():
    with open('dashboard_v2.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. CSS
    new_css = """
    /* Senior (2023级) Dedicated Phase Roadmap & Matrix Styles */
    .senior-phase-container {
      margin-bottom: 16px;
    }
    .senior-phase-card {
      background: #ffffff;
      border: 1.5px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px 20px;
      box-shadow: var(--shadow-card);
    }
    .senior-phase-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 14px;
    }
    .senior-phase-title-wrap {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }
    .senior-phase-badge {
      font-size: 11px;
      font-weight: 700;
      color: #7c3aed;
      background: #f5f3ff;
      border: 1px solid #ddd6fe;
      padding: 3px 8px;
      border-radius: 6px;
    }
    .senior-phase-h3 {
      font-size: 15px;
      font-weight: 700;
      color: #0f172a;
      margin: 0;
    }
    .senior-phase-sub {
      font-size: 12px;
      color: #64748b;
      font-weight: 400;
    }
    .senior-view-toggle {
      display: inline-flex;
      background: #f1f5f9;
      padding: 3px;
      border-radius: 8px;
      gap: 4px;
    }
    .view-toggle-btn {
      border: none;
      background: transparent;
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 600;
      color: #64748b;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .view-toggle-btn.active {
      background: #ffffff;
      color: #0f172a;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }
    .phase-track {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 10px;
      margin-bottom: 12px;
    }
    @media (max-width: 900px) {
      .phase-track {
        grid-template-columns: 1fr;
      }
    }
    .phase-step {
      border: 1.5px solid #e2e8f0;
      border-radius: 10px;
      padding: 10px 12px;
      background: #f8fafc;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .phase-step:hover {
      border-color: #cbd5e1;
      background: #f1f5f9;
      transform: translateY(-1px);
    }
    .phase-step.active {
      border-color: #3b82f6;
      background: #eff6ff;
      box-shadow: 0 4px 12px -2px rgba(59, 130, 246, 0.18);
    }
    .phase-step.active .step-num {
      background: #2563eb;
      color: #ffffff;
    }
    .step-header {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 4px;
    }
    .step-num {
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: #e2e8f0;
      color: #475569;
      font-weight: 700;
      font-size: 11px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }
    .step-title {
      font-size: 12.5px;
      font-weight: 700;
      color: #1e293b;
    }
    .step-weeks {
      font-size: 11px;
      font-weight: 600;
      color: #2563eb;
      margin-bottom: 3px;
    }
    .step-desc {
      font-size: 11px;
      color: #64748b;
      line-height: 1.35;
    }
    .phase-status-alert {
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 12.5px;
      line-height: 1.5;
      display: flex;
      align-items: flex-start;
      gap: 10px;
      transition: all 0.2s ease;
    }
    .phase-status-alert.alert-blue {
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      color: #1e40af;
    }
    .phase-status-alert.alert-amber {
      background: #fffbeb;
      border: 1px solid #fde68a;
      color: #92400e;
    }
    .phase-status-alert.alert-orange {
      background: #fff7ed;
      border: 1px solid #fed7aa;
      color: #9a3412;
    }
    .phase-status-alert.alert-purple {
      background: #faf5ff;
      border: 1px solid #e9d5ff;
      color: #5b21b6;
    }
    .phase-status-alert.alert-teal {
      background: #f0fdfa;
      border: 1px solid #99f6e4;
      color: #115e59;
    }
    .alert-icon {
      font-size: 16px;
      line-height: 1;
      flex-shrink: 0;
      margin-top: 1px;
    }
    .alert-body strong {
      font-weight: 700;
      margin-right: 4px;
    }

    /* Off-campus classes callout */
    .senior-offcampus-box {
      margin-top: 14px;
      background: #fafaf9;
      border: 1.5px dashed #d6d3d1;
      border-radius: 10px;
      padding: 12px 16px;
    }
    .offcampus-header {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      margin-bottom: 8px;
    }
    .offcampus-title {
      font-size: 12.5px;
      font-weight: 700;
      color: #292524;
    }
    .offcampus-desc {
      font-size: 11.5px;
      color: #57534e;
      margin-top: 2px;
      line-height: 1.4;
    }
    .offcampus-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }
    .offcampus-tag {
      display: inline-flex;
      align-items: center;
      padding: 3px 8px;
      background: #ffffff;
      border: 1px solid #e7e5e4;
      border-radius: 6px;
      font-size: 11px;
      color: #44403c;
      font-weight: 500;
    }
    .offcampus-tag .tag-status {
      font-size: 10px;
      color: #ea580c;
      margin-left: 5px;
      font-weight: 600;
    }

    /* Course Nature Badges */
    .course-nature-tag {
      display: inline-flex;
      align-items: center;
      font-size: 10px;
      font-weight: 600;
      padding: 1.5px 6px;
      border-radius: 4px;
      letter-spacing: 0.02em;
      white-space: nowrap;
    }
    .tag-pub { background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; }
    .tag-cross { background: #eef2ff; color: #4f46e5; border: 1px solid #c7d2fe; }
    .tag-trip { background: #fffbeb; color: #d97706; border: 1px solid #fde68a; }
    .tag-practicum { background: #ecfdf5; color: #059669; border: 1px solid #a7f3d0; }
    .tag-thesis { background: #faf5ff; color: #7c3aed; border: 1px solid #e9d5ff; }
    .tag-lecture { background: #f0fdfa; color: #0d9488; border: 1px solid #99f6e4; }
    .tag-military { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }

    /* Gantt Matrix Table */
    .senior-matrix-card {
      margin-top: 16px;
      overflow-x: auto;
      padding: 16px 20px;
    }
    .gantt-table {
      width: 100%;
      min-width: 980px;
      border-collapse: collapse;
      font-size: 11.5px;
      table-layout: fixed;
    }
    .gantt-table th, .gantt-table td {
      border: 1px solid #e2e8f0;
      padding: 6px 4px;
      text-align: center;
      vertical-align: middle;
    }
    .gantt-th-major {
      width: 85px;
      background: #f8fafc;
      font-weight: 700;
      color: #334155;
    }
    .gantt-th-class {
      width: 105px;
      background: #f8fafc;
      font-weight: 700;
      color: #334155;
      text-align: left !important;
      padding-left: 8px !important;
    }
    .gantt-th-week {
      background: #f8fafc;
      font-weight: 600;
      color: #475569;
      font-size: 10.5px;
      cursor: pointer;
      width: 40px;
    }
    .gantt-th-week:hover {
      background: #eff6ff;
      color: #2563eb;
    }
    .gantt-th-week.current-week-col {
      background: #dbeafe;
      color: #1e40af;
      font-weight: 700;
    }
    .gantt-block {
      border-radius: 6px;
      padding: 5px 4px;
      font-size: 10.5px;
      font-weight: 600;
      text-align: center;
      transition: all 0.15s ease;
      cursor: pointer;
      box-shadow: 0 1px 2px rgba(0,0,0,0.04);
      display: block;
    }
    .gantt-block:hover {
      transform: scale(1.02);
      box-shadow: 0 3px 8px rgba(0,0,0,0.1);
    }
    .gantt-block .gb-name {
      font-weight: 700;
      display: block;
      margin-bottom: 2px;
      line-height: 1.25;
    }
    .gantt-block .gb-meta {
      font-size: 9.5px;
      opacity: 0.85;
      font-weight: 400;
      display: block;
      line-height: 1.2;
    }
    .gantt-pub {
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
    }
    .gantt-cross {
      background: #eef2ff;
      color: #4338ca;
      border: 1px solid #c7d2fe;
    }
    .gantt-trip {
      background: #fffbeb;
      color: #b45309;
      border: 1px solid #fde68a;
    }
    .gantt-practicum {
      background: #ecfdf5;
      color: #047857;
      border: 1px solid #a7f3d0;
    }
    .gantt-thesis {
      background: #faf5ff;
      color: #6b21a8;
      border: 1px solid #e9d5ff;
    }
    .gantt-lecture {
      background: #f0fdfa;
      color: #0f766e;
      border: 1px solid #99f6e4;
    }
    .gantt-empty {
      background: #fafaf9;
      color: #78716c;
      border: 1px dashed #d6d3d1;
      border-radius: 6px;
      padding: 5px 3px;
      font-size: 10px;
      font-weight: 500;
      display: block;
    }
    """

    if 'senior-phase-container' not in html:
        html = html.replace('</style>', new_css + '\n</style>', 1)

    # 2. Insert Senior Phase Container
    if 'id="seniorPhaseContainer"' not in html:
        senior_html = """

    <!-- Senior (2023级) Dedicated Phase Roadmap & View Switcher -->
    <div id="seniorPhaseContainer" class="senior-phase-container" style="display: none;">
      <div class="senior-phase-card">
        <div class="senior-phase-header">
          <div class="senior-phase-title-wrap">
            <span class="senior-phase-badge">2023级 · 毕业学年</span>
            <h3 class="senior-phase-h3">大四教学阶段全景指引</h3>
            <span class="senior-phase-sub">全院 11 个班级“五段式”递进培养体系与排课特征解析</span>
          </div>
          <div class="senior-view-toggle">
            <button class="view-toggle-btn active" id="btnSeniorWeekly" onclick="switchSeniorView('weekly')">📅 单周课程详情</button>
            <button class="view-toggle-btn" id="btnSeniorMatrix" onclick="switchSeniorView('matrix')">🗺️ 11班×20周全景对照矩阵</button>
          </div>
        </div>

        <!-- 5-Stage Step Track -->
        <div class="phase-track" id="seniorPhaseTrack">
          <div class="phase-step" id="stepPhase1" onclick="setWeek(1)">
            <div class="step-header">
              <span class="step-num">1</span>
              <span class="step-title">公选与交叉拓展</span>
            </div>
            <div class="step-weeks">第 1 - 3 周</div>
            <div class="step-desc">避开低年级自主排课 / 跨专业选修</div>
          </div>
          <div class="phase-step" id="stepPhase2" onclick="setWeek(4)">
            <div class="step-header">
              <span class="step-num">2</span>
              <span class="step-title">毕业考察集中采风</span>
            </div>
            <div class="step-weeks">第 4 - 6 周</div>
            <div class="step-desc">全员外出考察基地 / 现场采风调研</div>
          </div>
          <div class="phase-step" id="stepPhase3" onclick="setWeek(7)">
            <div class="step-header">
              <span class="step-num">3</span>
              <span class="step-title">分散实习与实训调研</span>
            </div>
            <div class="step-weeks">第 7 - 13 周</div>
            <div class="step-desc">视传/包装校外实习 · 数媒/印刷实训</div>
          </div>
          <div class="phase-step" id="stepPhase4" onclick="setWeek(14)">
            <div class="step-header">
              <span class="step-num">4</span>
              <span class="step-title">毕业设计(创作)推进</span>
            </div>
            <div class="step-weeks">第 14 - 18 周</div>
            <div class="step-desc">11班全员工作室创作 / 导师指导</div>
          </div>
          <div class="phase-step" id="stepPhase5" onclick="setWeek(19)">
            <div class="step-header">
              <span class="step-num">5</span>
              <span class="step-title">学术讲座周与考查</span>
            </div>
            <div class="step-weeks">第 19 - 20 周</div>
            <div class="step-desc">学术报告厅 / 系列讲座与结题考查</div>
          </div>
        </div>

        <!-- Dynamic Phase Status Alert for current week -->
        <div class="phase-status-alert" id="seniorPhaseAlert"></div>
      </div>
    </div>
"""
        controls_end = '</section>'
        m_pos = html.find(controls_end)
        if m_pos != -1:
            pos_insert = m_pos + len(controls_end)
            html = html[:pos_insert] + senior_html + html[pos_insert:]

    # 3. Add id="mainTableCard"
    html = html.replace('<div class="table-card">', '<div class="table-card" id="mainTableCard">', 1)

    # 4. Add seniorMatrixCard and seniorOffCampusContainer before </main>
    if 'id="seniorMatrixCard"' not in html:
        matrix_html = """
    <!-- Senior 20-Week Full Matrix View (Gantt-style) -->
    <div class="table-card senior-matrix-card" id="seniorMatrixCard" style="display: none;">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; flex-wrap: wrap; gap: 10px;">
        <div>
          <h3 style="font-size: 14.5px; font-weight: 700; color: #0f172a; margin: 0 0 3px 0;">🗺️ 2023级（大四）全院 11 个班级 · 全学期 20 周教学阶段全景对照矩阵</h3>
          <p style="font-size: 12px; color: #64748b; margin: 0;">直观呈现各专业、各班级在 20 周中的阶段递进关系；点击任意课程块可跳转至对应教学周。</p>
        </div>
        <div style="display: flex; gap: 8px; font-size: 11px; flex-wrap: wrap;">
          <span class="course-nature-tag tag-pub">全校公选</span>
          <span class="course-nature-tag tag-cross">交叉选修</span>
          <span class="course-nature-tag tag-trip">毕业考察</span>
          <span class="course-nature-tag tag-practicum">专业实训</span>
          <span class="course-nature-tag tag-thesis">毕业设计</span>
          <span class="course-nature-tag tag-lecture">学术讲座</span>
        </div>
      </div>
      <div id="seniorMatrixContent"></div>
    </div>
"""
        pos_main = html.find('</main>')
        if pos_main != -1:
            html = html[:pos_main] + matrix_html + html[pos_main:]

    with open('dashboard_v2.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print('HTML & CSS injection completed successfully!')

if __name__ == '__main__':
    main()
