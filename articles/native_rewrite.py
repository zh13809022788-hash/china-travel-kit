#!/usr/bin/env python3
"""Native rewrite 2 articles to 7 languages, anti-AI detection rules applied"""
import requests, json, os, time, re

API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_URL = "https://sub.llmwc.com/v1/responses"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json", "User-Agent": "curl/8.7.1"}
BASE = "D:/独立站/china-travel-kit/src/content"

ARTICLES = ["article41", "article42"]
LANG_MAP = [
    ("posts-zh-tw", "Traditional Chinese", "native Taiwanese Mandarin"),
    ("posts-ja", "Japanese", "native Japanese"),
    ("posts-ko", "Korean", "native Korean"),
    ("posts-ru", "Russian", "native Russian"),
    ("posts-fr", "French", "native French"),
    ("posts-de", "German", "native German"),
    ("posts-es", "Spanish", "native Spanish"),
]

ARTS_DIR = "C:/Users/aomanhanliu/WorkBuddy/2026-07-13-22-17-42/articles"

for art in ARTICLES:
    with open(f"{ARTS_DIR}/{art}_en.md", "r", encoding="utf-8") as f:
        source = f.read()

    for lang_dir, lang_name, tone in LANG_MAP:
        out_path = f"{BASE}/{lang_dir}"
        if art == "article41":
            filename = "china-public-toilets-guide-foreigners.md"
        else:
            filename = "guangzhou-city-guide-2026-foreigners.md"

        full_path = f"{out_path}/{filename}"
        if os.path.exists(full_path):
            print(f"SKIP (exists): {lang_dir}/{filename}")
            continue

        prompt = f"""You are a {tone} travel writer. Rewrite the following article in {lang_name}. 
DO NOT machine translate. Write it as a native {lang_name} travel blog post.

RULES:
- Use natural {lang_name} expressions, NOT translated English syntax
- Break the AI-perfect structure: vary paragraph length, use colloquial phrases
- Keep all factual data (prices, distances, names, URLs) intact
- Keep markdown ## headings structure but rewrite in natural {lang_name}
- Keep FAQ section and frontmatter structure
- Frontmatter: keep title/description/date, translate tags
- Translation of title and description:
  For zh-tw: 
    art41 title = "中國公廁使用指南2026：外國遊客不慌張的生存技巧"
    art41 desc = "中國公共廁所實用指南：哪裡找乾淨洗手間、裡面長什麼樣、蹲式vs坐式選擇、外國遊客應急技巧。"
    art42 title = "廣州旅遊指南2026：外國遊客須知"
    art42 desc = "廣州實用旅遊指南：必去景點、粵菜美食、機場交通、最佳住宿區域、深圳香港一日遊。"
  For ja: translate naturally
  For ko: translate naturally
  For ru/fr/de/es: translate naturally

SOURCE ARTICLE:
{source}

Return ONLY the complete markdown file content including frontmatter. Do NOT add any explanation."""

        data = {"model": "gpt-5.5", "input": prompt, "temperature": 0.35, "max_output_tokens": 4000}
        ok = False
        for attempt in range(2):
            try:
                resp = requests.post(API_URL, headers=headers, json=data, timeout=300)
                txt = ""
                for o in resp.json().get("output", []):
                    for c in o.get("content", []):
                        if c.get("type") == "output_text":
                            txt += c.get("text", "")
                if txt:
                    # Remove possible code block wrapping
                    txt = txt.strip()
                    if txt.startswith("```"):
                        txt = re.sub(r"^```\w*\n?", "", txt)
                        txt = re.sub(r"\n```$", "", txt)
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(txt)
                    print(f"✅ {lang_dir}/{filename} ({len(txt)} chars)")
                    ok = True
                    break
            except Exception as e:
                print(f"  ⚠️  retry {attempt+1}: {str(e)[:40]}")
                time.sleep(5)
        if not ok:
            print(f"❌ {lang_dir}/{filename} - FAILED")
        time.sleep(2)

print("\nDone! All language versions generated.")
