def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    skip = False
    skip_reason = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # 1. Skip phase track HTML
        if '<!-- 5-Stage Step Track -->' in line or 'id="seniorPhaseTrack"' in line:
            # Skip until after </div>\n    </div> before <!-- Controls Card -->
            while i < len(lines) and '<!-- Controls Card -->' not in lines[i]:
                i += 1
            continue

        # 2. Skip seniorMatrixContent
        if 'id="seniorMatrixContent"' in line:
            # Skip line and next line if it is </div>
            i += 1
            if i < len(lines) and '</div>' in lines[i]:
                i += 1
            continue

        # 3. Skip senior JS functions
        if "// Switch Senior View Mode: 'weekly' or 'matrix'" in line:
            while i < len(lines) and 'function updateDataCards' not in lines[i]:
                i += 1
            continue

        # 4. Skip any calls to updateSeniorPhaseBanner
        if 'updateSeniorPhaseBanner' in line:
            i += 1
            continue

        new_lines.append(line)
        i += 1

    content = ''.join(new_lines)

    # Clean any extra blank lines before Controls Card
    content = content.replace('</section>\n\n\n    <!-- Controls Card -->', '</section>\n\n    <!-- Controls Card -->')
    content = content.replace('</section>\n\n    <!-- Controls Card -->', '</section>\n\n    <!-- Controls Card -->')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Cleaned {filepath}')

clean_file('dashboard_v2.html')
clean_file('index.html')
