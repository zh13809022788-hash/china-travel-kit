"""Generate task files for batch translation of remaining 26 articles into 7 languages."""
import os

LANG_MAP = {
    'fr': {'name': '法语', 'code': 'fr'},
    'de': {'name': '德语', 'code': 'de'},
    'es': {'name': '西班牙语', 'code': 'es'},
    'ru': {'name': '俄语', 'code': 'ru'},
    'ja': {'name': '日语', 'code': 'ja'},
    'ko': {'name': '韩语', 'code': 'ko'},
    'zh-tw': {'name': '繁体中文', 'code': 'zh-TW'},
}

EN_DIR = r'D:\独立站\china-travel-kit\src\content\posts'
WORKBUDDY_DIR = r'D:\独立站\china-travel-kit\.workbuddy'
CONTENT_BASE = r'src/content'

# Get untranslated slugs for a given language
def get_untranslated(lang):
    en_slugs = set()
    for f in os.listdir(EN_DIR):
        if f.endswith('.md'):
            en_slugs.add(f.replace('.md', ''))
    target_dir = os.path.join(r'D:\独立站\china-travel-kit', CONTENT_BASE, f'posts-{lang}')
    translated = set()
    if os.path.exists(target_dir):
        for f in os.listdir(target_dir):
            if f.endswith('.md'):
                translated.add(f.replace('.md', ''))
    return sorted(en_slugs - translated)

# Generate task files
for lang, info in LANG_MAP.items():
    missing = get_untranslated(lang)
    if not missing:
        print(f'{lang}: 全部完成')
        continue
    
    lines = []
    lines.append(f'## 任务：批量重塑 {info["name"]} 翻译（{len(missing)} 篇）')
    lines.append('')
    lines.append('## 工作目录')
    lines.append('D:\\独立站\\china-travel-kit')
    lines.append('')
    lines.append('## 物理隔离红线')
    lines.append(f'仅操作 src/content/posts-{lang}/ 目录')
    lines.append('')
    lines.append('## 核心方法（严格遵守）')
    lines.append('不是翻译，是"用信息重新写"。')
    lines.append('第1轮：阅读英文源文，提取关键信息（步骤/数据/FAQ/注意事项/实操建议）')
    lines.append(f'第2轮：用{info["name"]}从零"写"新文章，地道表达，像真人写给旅行者看的')
    lines.append('')
    lines.append('## 关键提示')
    lines.append('- 标题保持 SEO 风格，含目标语言关键词')
    lines.append('- 保留 frontmatter 的 pubDate、category、tags 结构，tags 翻译为目标语言')
    lines.append('- 保留 faqs 列表不变（问题+答案都写入）')
    lines.append('- 封面图片路径 cover 不变（同名图片各语言通用）')
    lines.append('- 不要添加任何英文段落，全文用目标语言')
    lines.append('- "避坑提示"用 > ⚠️ 引用块格式')
    lines.append('- 保留 AFFILIATE 占位注释行不改')
    lines.append('- 每篇完成后立即写入文件')
    lines.append('')
    lines.append(f'## 文章列表（共 {len(missing)} 篇）')
    lines.append('')
    
    for i, slug in enumerate(missing, 1):
        lines.append(f'### {i}. {slug}.md')
        lines.append(f'源: {CONTENT_BASE}/posts/{slug}.md')
        lines.append(f'目标: {CONTENT_BASE}/posts-{lang}/{slug}.md')
        lines.append('')
    
    # Write task file
    out_path = os.path.join(WORKBUDDY_DIR, f'translate-{lang}-batch-v2_task.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'{lang}: {out_path} ({len(missing)} 篇)')

print('\n全部任务文件生成完毕')
