#!/usr/bin/env python3
"""Generate 2 English articles via GPT-5.5 API"""
import requests, json, os, time

API_KEY = os.environ.get("OPENAI_API_KEY", "")
API_URL = "https://sub.llmwc.com/v1/responses"
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

DIR = os.path.expanduser("~") + "/WorkBuddy/2026-07-13-22-17-42/articles"
os.makedirs(DIR, exist_ok=True)

# Article 41
prompt41 = open(DIR + "/prompt41.txt", "r", encoding="utf-8").read()
data = {"model": "gpt-5.5", "input": prompt41, "temperature": 0.35, "max_output_tokens": 4000}
resp = requests.post(API_URL, headers=headers, json=data, timeout=120)
txt = ""
for o in resp.json().get("output", []):
    for c in o.get("content", []):
        if c.get("type") == "output_text":
            txt += c.get("text", "")
with open(DIR + "/article41_en.md", "w", encoding="utf-8") as f:
    f.write(txt)
print(f"Article 41: {len(txt)} chars")

# Article 42
time.sleep(3)
prompt42 = open(DIR + "/prompt42.txt", "r", encoding="utf-8").read()
data = {"model": "gpt-5.5", "input": prompt42, "temperature": 0.35, "max_output_tokens": 4000}
resp = requests.post(API_URL, headers=headers, json=data, timeout=120)
txt = ""
for o in resp.json().get("output", []):
    for c in o.get("content", []):
        if c.get("type") == "output_text":
            txt += c.get("text", "")
with open(DIR + "/article42_en.md", "w", encoding="utf-8") as f:
    f.write(txt)
print(f"Article 42: {len(txt)} chars")
