from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ["ja", "ko", "fr", "de", "es", "ru", "zh-tw"]
PATTERN = re.compile(
    r"'([^'\n]*[A-Za-z][^'\n]*)'|\"([^\"\n]*[A-Za-z][^\"\n]*)\"|>([^<\n]*[A-Za-z][^<\n]*)<"
)
SKIP_PREFIXES = ("http", "/", "src/", "astro:", "https", "_astro", "../")
SKIP_TOKENS = {
    "class", "const", "import", "from", "href", "src", "alt", "loading", "format",
    "click", "change", "input", "hidden", "lazy", "eager", "smooth", "numeric",
    "banner", "in-article", "card", "btn-primary", "btn-outline", "section-kicker",
    "section-heading", "sr-only", "result", "short", "good", "all", "border",
}


def main():
    items = {}
    for locale in LOCALES:
        root = ROOT / "src" / "pages" / locale
        for path in root.rglob("*.astro"):
            text = path.read_text(encoding="utf-8")
            for match in PATTERN.finditer(text):
                value = next(group for group in match.groups() if group)
                value = re.sub(r"\s+", " ", value).strip()
                looks_like_class = (
                    " " in value
                    and any(part.startswith(("mt-", "text-", "bg-", "border", "grid", "flex", "rounded", "max-", "container", "md:", "lg:", "sm:", "xl:", "hover:", "p-", "py-", "px-", "gap-", "font-", "leading-", "shadow")) for part in value.split())
                )
                if len(value) < 3 or value.startswith(SKIP_PREFIXES) or value in SKIP_TOKENS or looks_like_class:
                    continue
                items.setdefault(value, set()).add(str(path.relative_to(ROOT)))

    for value, files in sorted(items.items(), key=lambda item: (-len(item[1]), item[0]))[:400]:
        print(f"{len(files):3} | {value}")


if __name__ == "__main__":
    main()
