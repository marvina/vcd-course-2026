import re

def remove_guidance(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove HTML seniorPhaseContainer
    phase_container_pattern = r'\s*<!-- Senior \(2023级\) Dedicated Phase Roadmap & View Switcher -->[\s\S]*?</div>\s*</div>\s*'
    content = re.sub(phase_container_pattern, '\n', content)

    # 2. Remove HTML seniorMatrixCard
    matrix_card_pattern = r'\s*<!-- Senior 20-Week Full Matrix View \(Gantt-style\) -->[\s\S]*?</div>\s*</div>\s*'
    content = re.sub(matrix_card_pattern, '\n', content)

    # 3. Remove CSS for senior phase, roadmap, matrix, offcampus
    css_pattern = r'\s*/\* Senior \(2023级\) Dedicated Phase Roadmap & Matrix Styles \*/[\s\S]*?(?=\.course-nature-tag)'
    content = re.sub(css_pattern, '\n    ', content)

    # Also remove the Gantt Matrix Table CSS after course-nature-tag
    css_gantt_pattern = r'\s*/\* Gantt Matrix Table \*/[\s\S]*?(?=</style>)'
    content = re.sub(css_gantt_pattern, '\n    ', content)

    # 4. Remove JS state variable
    content = content.replace("let seniorViewMode = 'weekly';\n", "")
    content = content.replace("let seniorViewMode = 'weekly';", "")

    # 5. Remove calls in renderTable()
    render_table_clean = """      updateDataCards(activeCourses);
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

    content = content.replace(render_table_clean, "      updateDataCards(activeCourses);")
    content = content.replace("updateSeniorPhaseBanner(activeCourses);", "")

    # 6. Remove switchSeniorView, jumpToWeek, updateSeniorPhaseBanner, renderSeniorMatrix
    js_funcs_pattern = r'\s*// Switch Senior View Mode: \'weekly\' or \'matrix\'[\s\S]*?(?=// Update Bottom Data Cards:)'
    content = re.sub(js_funcs_pattern, '\n\n    ', content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Successfully removed senior guidance from {filepath}')

if __name__ == '__main__':
    remove_guidance('dashboard_v2.html')
    remove_guidance('index.html')
