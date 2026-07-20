import os, re, glob

all_files = glob.glob('src/pages/**/index.astro', recursive=True)
header_fixed = 0
text_fixed = 0

for fp in sorted(all_files):
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content
    
    # Fix headers
    content = re.sub(r'<header class="(max-w-2xl|max-w-3xl)">', '<header>', content)
    content = re.sub(r'<p class="mt-4 max-w-3xl text-lg', '<p class="mt-4 text-lg', content)
    
    if content != orig:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        header_fixed += 1

print("Header fixes: {}".format(header_fixed))

for fp in sorted(all_files):
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    orig = content
    
    content = re.sub(
        r'class="(mt-8|mt-6)\s+space-y-4\s+text-lg\s+leading-8\s+text-gray-600"',
        r'class="\1 space-y-4 text-justify text-lg leading-8 text-gray-600"',
        content
    )
    content = re.sub(
        r'class="(mt-8|mt-6)\s+max-w-3xl\s+space-y-4\s+text-justify\s+text-lg',
        r'class="\1 space-y-4 text-justify text-lg',
        content
    )
    
    if content != orig:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        text_fixed += 1

print("Text-justify fixes: {}".format(text_fixed))

# Check remaining food/transport with no body text
print("\nStill missing body (food/transport):")
for fp in sorted(all_files):
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'CoverImage' not in content:
        continue
    if re.search(r'<div class="mt-8\s+space-y-4\s+text-justify', content):
        continue
    path = fp.replace(os.sep, '/')
    if '/food/' not in path and '/transport/' not in path:
        continue
    print("  " + path)
