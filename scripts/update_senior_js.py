import re

def main():
    with open('dashboard_v2.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add seniorViewMode state variable
    if 'let seniorViewMode' not in content:
        content = content.replace(
            "let currentMajor = 'ALL';",
            "let currentMajor = 'ALL';\n    let seniorViewMode = 'weekly';"
        )

    # 2. Add getCourseNatureBadge helper
    nature_badge_fn = """
    // Course Nature Badge Helper
    function getCourseNatureBadge(c) {
      const name = c.course_name || '';
      const type = c.course_type || '';
      if (name.includes('军训')) {
        return '<span class="course-nature-tag tag-military">入学军训</span>';
      }
      if (type.includes('全校公选') || name.includes('品牌形象设计') || name.includes('品牌与包装设计')) {
        return '<span class="course-nature-tag tag-pub">全校公选</span>';
      }
      if (type.includes('交叉') || name.includes('动态图形设计') || name.includes('信息设计与数据可视化')) {
        return '<span class="course-nature-tag tag-cross">交叉选修</span>';
      }
      if (name.includes('考察')) {
        return '<span class="course-nature-tag tag-trip">毕业考察</span>';
      }
      if (name.includes('实训')) {
        return '<span class="course-nature-tag tag-practicum">专业实训</span>';
      }
      if (name.includes('毕业设计') || name.includes('毕业创作') || name.includes('毕业论文')) {
        return '<span class="course-nature-tag tag-thesis">毕业设计</span>';
      }
      if (name.includes('讲座')) {
        return '<span class="course-nature-tag tag-lecture">学术讲座</span>';
      }
      return '';
    }
"""

    if 'function getCourseNatureBadge' not in content:
        pos = content.find('function getMajorBadge')
        if pos != -1:
            content = content[:pos] + nature_badge_fn + '\n' + content[pos:]

    # 3. Update Course column rendering to include getCourseNatureBadge(c)
    # Search for course-title
    old_course_td = """        tdCourse.innerHTML = `
          <span class="course-title" title="点击查看详情">${c.course_name}</span>
        `;"""

    new_course_td = """        const natureBadge = getCourseNatureBadge(c);
        tdCourse.innerHTML = `
          <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
            <span class="course-title" title="点击查看详情">${c.course_name}</span>
            ${natureBadge}
          </div>
        `;"""

    if old_course_td in content:
        content = content.replace(old_course_td, new_course_td)

    # 4. Add switchSeniorView, updateSeniorPhaseBanner, renderSeniorMatrix, jumpToWeek
    senior_funcs = """
    // Switch Senior View Mode: 'weekly' or 'matrix'
    function switchSeniorView(mode) {
      seniorViewMode = mode;
      const btnWeekly = document.getElementById('btnSeniorWeekly');
      const btnMatrix = document.getElementById('btnSeniorMatrix');
      const mainTableCard = document.getElementById('mainTableCard');
      const seniorMatrixCard = document.getElementById('seniorMatrixCard');

      if (mode === 'weekly') {
        if (btnWeekly) btnWeekly.classList.add('active');
        if (btnMatrix) btnMatrix.classList.remove('active');
        if (mainTableCard) mainTableCard.style.display = 'block';
        if (seniorMatrixCard) seniorMatrixCard.style.display = 'none';
        renderTable();
      } else {
        if (btnWeekly) btnWeekly.classList.remove('active');
        if (btnMatrix) btnMatrix.classList.add('active');
        if (mainTableCard) mainTableCard.style.display = 'none';
        if (seniorMatrixCard) seniorMatrixCard.style.display = 'block';
        renderSeniorMatrix();
      }
    }

    function jumpToWeek(w) {
      setWeek(w);
      switchSeniorView('weekly');
    }

    // Update Senior Phase Banner Roadmap & Alert
    function updateSeniorPhaseBanner(activeCourses) {
      const container = document.getElementById('seniorPhaseContainer');
      if (!container) return;

      if (currentGrade !== '2023级') {
        container.style.display = 'none';
        const seniorMatrixCard = document.getElementById('seniorMatrixCard');
        if (seniorMatrixCard) seniorMatrixCard.style.display = 'none';
        const mainTableCard = document.getElementById('mainTableCard');
        if (mainTableCard) mainTableCard.style.display = 'block';
        return;
      }

      container.style.display = 'block';

      // 1. Determine active phase step
      let activePhase = 1;
      let alertClass = 'alert-blue';
      let alertIcon = '💡';
      let alertTitle = '';
      let alertDesc = '';

      if (currentWeek >= 1 && currentWeek <= 3) {
        activePhase = 1;
        alertClass = 'alert-blue';
        alertIcon = '💡';
        alertTitle = `第 ${currentWeek} 周 · 阶段一【公选与交叉拓展期】`;
        alertDesc = '本阶段全院大四 11 个班级同时开课。视传1-6班《品牌形象设计》、包装班《品牌与包装设计》为全校公选课（安排在周四周五全天，避开低年级自主排课）；数媒在514机房、交互在515机房修读交叉选修课；印刷1-2班在青岛基地修读《字体应用实训》。';
      } else if (currentWeek >= 4 && currentWeek <= 6) {
        activePhase = 2;
        alertClass = 'alert-amber';
        alertIcon = '🚌';
        alertTitle = `第 ${currentWeek} 周 · 阶段二【毕业考察集中采风期】`;
        alertDesc = '本阶段全院大四学生外出前往考察基地开展现场调研与艺术采风，无校内固定教室占用。视传1-6班、包装工程班、智能交互班考察3周（W4-W6）；数媒班考察持续5周（W6-W10）；印刷班考察安排在第10-11周。';
      } else if (currentWeek >= 7 && currentWeek <= 13) {
        activePhase = 3;
        alertClass = 'alert-orange';
        alertIcon = '💼';
        if (currentWeek <= 10) {
          alertTitle = `第 ${currentWeek} 周 · 阶段三【校外分散实习与项目实训期】`;
          alertDesc = '视传1-6班、包装工程班按培养方案进入【校外企业分散实习与毕业设计开题调研】（校内无固定排课，由指导老师跟进）；数媒在考察基地开展毕业考察；印刷1-2班在青岛基地集中开展《综合项目实训》；智能交互班进行自主选题调研。';
        } else {
          alertTitle = `第 ${currentWeek} 周 · 阶段三向阶段四过渡【毕业设计开题启动期】`;
          alertDesc = '数媒与智能交互班【提前两周启动毕业设计开题指导】（W11-W18共8周）；印刷1-2班完成考察进入选题休整；视传1-6班、包装工程班继续在校外推进毕业设计选题与资料筹备。';
        }
      } else if (currentWeek >= 14 && currentWeek <= 18) {
        activePhase = 4;
        alertClass = 'alert-purple';
        alertIcon = '🎓';
        alertTitle = `第 ${currentWeek} 周 · 阶段四【毕业设计(创作)集中推进期】`;
        alertDesc = '全院大四 11 个班级全员进入毕业创作核心阶段！由视传、包装、数媒、交互、印刷各教研室指导老师在工作室开展全周毕业创作与论文集中深化指导，11个班级齐头并进。';
      } else {
        activePhase = 5;
        alertClass = 'alert-teal';
        alertIcon = '🎤';
        alertTitle = `第 ${currentWeek} 周 · 阶段五【学术讲座周与考查结题】`;
        alertDesc = '全院大四 11 个班级统一修读《学术讲座I》（2学分），在学院学术报告厅及青岛基地报告厅集中聆听系列学术前沿报告，完成学期考查结课。';
      }

      for (let p = 1; p <= 5; p++) {
        const stepEl = document.getElementById(`stepPhase${p}`);
        if (stepEl) {
          if (p === activePhase) stepEl.classList.add('active');
          else stepEl.classList.remove('active');
        }
      }

      const alertEl = document.getElementById('seniorPhaseAlert');
      if (alertEl) {
        alertEl.className = `phase-status-alert ${alertClass}`;
        alertEl.innerHTML = `
          <div class="alert-icon">${alertIcon}</div>
          <div class="alert-body">
            <strong>${alertTitle}</strong> ${alertDesc}
          </div>
        `;
      }
    }

    // Render Senior Gantt Matrix Table
    function renderSeniorMatrix() {
      const container = document.getElementById('seniorMatrixContent');
      if (!container) return;

      const matrixData = [
        {
          major: '视觉传达设计',
          rowspan: 6,
          classes: [
            { name: '23视觉传达1班', t1: '常言平', t2: '张楠、常言平' },
            { name: '23视觉传达2班', t1: '吴瑶', t2: '王雪、李霞' },
            { name: '23视觉传达3班', t1: '徐德记', t2: '王刚、李海峰' },
            { name: '23视觉传达4班', t1: '姜晓慧', t2: '曲展、刘泽延' },
            { name: '23视觉传达5班', t1: '杜明星', t2: '宋梅梅、邓雅楠' },
            { name: '23视觉传达6班', t1: '高蓬', t2: '焦燕、董雪莲' }
          ],
          renderRow: (c) => `
            <td class="gantt-th-class">${c.name}</td>
            <td colspan="3" class="gantt-cell"><div class="gantt-block gantt-pub" onclick="jumpToWeek(1)"><span class="gb-name">品牌形象设计</span><span class="gb-meta">${c.t1} · 公选</span></div></td>
            <td colspan="3" class="gantt-cell"><div class="gantt-block gantt-trip" onclick="jumpToWeek(4)"><span class="gb-name">毕业考察</span><span class="gb-meta">${c.t2} · 采风</span></div></td>
            <td colspan="7" class="gantt-cell"><div class="gantt-empty"><span style="font-weight:600;display:block;">校外分散毕业实习 / 毕设调研</span><span style="font-size:9.5px;opacity:0.8;">校外实践 · 校内无课</span></div></td>
            <td colspan="5" class="gantt-cell"><div class="gantt-block gantt-thesis" onclick="jumpToWeek(14)"><span class="gb-name">毕业设计(创作)</span><span class="gb-meta">${c.t2} · 工作室</span></div></td>
            <td colspan="2" class="gantt-cell"><div class="gantt-block gantt-lecture" onclick="jumpToWeek(19)"><span class="gb-name">学术讲座I</span><span class="gb-meta">报告厅 · 2学分</span></div></td>
          `
        },
        {
          major: '包装工程',
          rowspan: 1,
          classes: [{ name: '23包装工程班' }],
          renderRow: () => `
            <td class="gantt-th-class">23包装工程班</td>
            <td colspan="3" class="gantt-cell"><div class="gantt-block gantt-pub" onclick="jumpToWeek(1)"><span class="gb-name">品牌与包装设计</span><span class="gb-meta">周美丽 · 公选</span></div></td>
            <td colspan="3" class="gantt-cell"><div class="gantt-block gantt-trip" onclick="jumpToWeek(4)"><span class="gb-name">毕业考察</span><span class="gb-meta">李永慧、吴瑶 · 采风</span></div></td>
            <td colspan="7" class="gantt-cell"><div class="gantt-empty"><span style="font-weight:600;display:block;">校外分散毕业实习 / 毕设调研</span><span style="font-size:9.5px;opacity:0.8;">校外实践 · 校内无课</span></div></td>
            <td colspan="5" class="gantt-cell"><div class="gantt-block gantt-thesis" onclick="jumpToWeek(14)"><span class="gb-name">毕业设计(创作)</span><span class="gb-meta">李永慧、吴瑶 · 工作室</span></div></td>
            <td colspan="2" class="gantt-cell"><div class="gantt-block gantt-lecture" onclick="jumpToWeek(19)"><span class="gb-name">学术讲座I</span><span class="gb-meta">报告厅 · 2学分</span></div></td>
          `
        },
        {
          major: '数字媒体',
          rowspan: 1,
          classes: [{ name: '23数字媒体' }],
          renderRow: () => `
            <td class="gantt-th-class">23数字媒体</td>
            <td colspan="3" class="gantt-cell"><div class="gantt-block gantt-cross" onclick="jumpToWeek(1)"><span class="gb-name">动态图形设计</span><span class="gb-meta">王颖慧 · 514</span></div></td>
            <td colspan="2" class="gantt-cell"><div class="gantt-block gantt-cross" onclick="jumpToWeek(4)"><span class="gb-name">信息设计II</span><span class="gb-meta">待定教师 · 514</span></div></td>
            <td colspan="5" class="gantt-cell"><div class="gantt-block gantt-trip" onclick="jumpToWeek(6)"><span class="gb-name">毕业考察 (5周)</span><span class="gb-meta">王颖惠、刘付 · 基地</span></div></td>
            <td colspan="8" class="gantt-cell"><div class="gantt-block gantt-thesis" onclick="jumpToWeek(11)"><span class="gb-name">毕业设计 (前两周开题)</span><span class="gb-meta">王颖惠、刘付 · 工作室 (8周)</span></div></td>
            <td colspan="2" class="gantt-cell"><div class="gantt-block gantt-lecture" onclick="jumpToWeek(19)"><span class="gb-name">学术讲座I</span><span class="gb-meta">报告厅 · 2学分</span></div></td>
          `
        },
        {
          major: '智能交互',
          rowspan: 1,
          classes: [{ name: '23智能交互设计1班' }],
          renderRow: () => `
            <td class="gantt-th-class">23智能交互1班</td>
            <td colspan="3" class="gantt-cell"><div class="gantt-block gantt-cross" onclick="jumpToWeek(1)"><span class="gb-name">信息设计与数据可视化</span><span class="gb-meta">张才忠 · 515</span></div></td>
            <td colspan="3" class="gantt-cell"><div class="gantt-block gantt-trip" onclick="jumpToWeek(4)"><span class="gb-name">毕业考察</span><span class="gb-meta">张小娟、周晓玉 · 采风</span></div></td>
            <td colspan="4" class="gantt-cell"><div class="gantt-empty"><span style="font-weight:600;display:block;">自主调研与开题准备</span><span style="font-size:9.5px;opacity:0.8;">自主调研 · 校内无课</span></div></td>
            <td colspan="8" class="gantt-cell"><div class="gantt-block gantt-thesis" onclick="jumpToWeek(11)"><span class="gb-name">毕业设计 (前两周开题)</span><span class="gb-meta">张小娟、周晓玉 · 工作室 (8周)</span></div></td>
            <td colspan="2" class="gantt-cell"><div class="gantt-block gantt-lecture" onclick="jumpToWeek(19)"><span class="gb-name">学术讲座I</span><span class="gb-meta">报告厅 · 2学分</span></div></td>
          `
        },
        {
          major: '视觉传达(印刷)',
          rowspan: 2,
          classes: [
            { name: '23级印刷1班', t1: '李啸海', t2: '李啸海', t3: '甄艳霞', t4: '李啸海、甄艳霞', c2: '综合项目实训1' },
            { name: '23级印刷2班', t1: '李娜', t2: '郝颖', t3: '王承利', t4: '李颖、王承利', c2: '综合项目实训2' }
          ],
          renderRow: (c) => `
            <td class="gantt-th-class">${c.name}</td>
            <td colspan="4" class="gantt-cell"><div class="gantt-block gantt-practicum" onclick="jumpToWeek(1)"><span class="gb-name">字体应用实训</span><span class="gb-meta">${c.t1} · 青岛</span></div></td>
            <td colspan="5" class="gantt-cell"><div class="gantt-block gantt-practicum" onclick="jumpToWeek(5)"><span class="gb-name">${c.c2}</span><span class="gb-meta">${c.t2} · 85学时</span></div></td>
            <td colspan="2" class="gantt-cell"><div class="gantt-block gantt-trip" onclick="jumpToWeek(10)"><span class="gb-name">毕业考察</span><span class="gb-meta">${c.t3} · 2学分</span></div></td>
            <td colspan="2" class="gantt-cell"><div class="gantt-empty"><span style="font-weight:600;display:block;">毕设休整准备</span><span style="font-size:9.5px;opacity:0.8;">基地无课</span></div></td>
            <td colspan="5" class="gantt-cell"><div class="gantt-block gantt-thesis" onclick="jumpToWeek(14)"><span class="gb-name">毕业创作/论文</span><span class="gb-meta">${c.t4} · 工作室</span></div></td>
            <td colspan="2" class="gantt-cell"><div class="gantt-block gantt-lecture" onclick="jumpToWeek(19)"><span class="gb-name">学术讲座I</span><span class="gb-meta">青岛报告厅 · 2分</span></div></td>
          `
        }
      ];

      let tableHtml = '<table class="gantt-table"><thead><tr><th class="gantt-th-major">专业</th><th class="gantt-th-class">班级</th>';
      for (let w = 1; w <= 20; w++) {
        const isCur = (w === currentWeek);
        tableHtml += `<th class="gantt-th-week ${isCur ? 'current-week-col' : ''}" onclick="jumpToWeek(${w})" title="点击切换至第${w}周">W${w}</th>`;
      }
      tableHtml += '</tr></thead><tbody>';

      matrixData.forEach(m => {
        m.classes.forEach((c, idx) => {
          tableHtml += '<tr>';
          if (idx === 0) {
            tableHtml += `<td class="gantt-th-major" rowspan="${m.rowspan}">${getMajorBadge(m.major)}</td>`;
          }
          tableHtml += m.renderRow(c);
          tableHtml += '</tr>';
        });
      });

      tableHtml += '</tbody></table>';
      container.innerHTML = tableHtml;
    }
"""

    if 'function switchSeniorView' not in content:
        pos = content.find('function updateDataCards')
        if pos != -1:
            content = content[:pos] + senior_funcs + '\n' + content[pos:]

    # 5. In renderTable, wire up updateSeniorPhaseBanner(activeCourses) and off-campus notice
    # Let's inspect where renderTable ends
    old_render_call = "updateDataCards(activeCourses);"
    new_render_call = """updateDataCards(activeCourses);
      updateSeniorPhaseBanner(activeCourses);

      // Render Off-campus Notice for Grade 4 in Weeks 7-13
      const existingOffCampus = document.getElementById('seniorOffCampusBox');
      if (existingOffCampus) existingOffCampus.remove();

      if (currentGrade === '2023级' && currentWeek >= 7 && currentWeek <= 13 && seniorViewMode === 'weekly') {
        const allG4Classes = ['23视觉传达1班', '23视觉传达2班', '23视觉传达3班', '23视觉传达4班', '23视觉传达5班', '23视觉传达6班',
                             '23包装工程班', '23数字媒体', '23智能交互设计1班', '23级印刷1班', '23级印刷2班'];
        const activeG4ClassNames = new Set(activeCourses.filter(c => c.grade === '2023级').map(c => c.class_name));
        const inactiveG4Classes = allG4Classes.filter(cls => !activeG4ClassNames.has(cls));

        if (inactiveG4Classes.length > 0) {
          const offBox = document.createElement('div');
          offBox.id = 'seniorOffCampusBox';
          offBox.className = 'senior-offcampus-box';
          offBox.innerHTML = `
            <div class="offcampus-header">
              <div style="font-size: 16px;">📌</div>
              <div>
                <div class="offcampus-title">第 ${currentWeek} 周校外分散实践与毕业调研班级（共 ${inactiveG4Classes.length} 个班级）</div>
                <div class="offcampus-desc">大四教学大纲规定：第 7 - 13 周为毕业实习与毕业设计前期调研阶段，以下班级在校外企业分散实践或由导师指导开展选题，无需在校内固定教室排课：</div>
              </div>
            </div>
            <div class="offcampus-tags">
              ${inactiveG4Classes.map(cls => `<span class="offcampus-tag">${cls}<span class="tag-status">校外实习/调研</span></span>`).join('')}
            </div>
          `;
          const mainTableCard = document.getElementById('mainTableCard');
          if (mainTableCard) mainTableCard.appendChild(offBox);
        }
      }"""

    if old_render_call in content:
        content = content.replace(old_render_call, new_render_call)

    with open('dashboard_v2.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Senior JavaScript logic injected successfully!')

if __name__ == '__main__':
    main()
